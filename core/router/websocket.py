import base64
import fastapi
import asyncio
import numpy as np
from pydantic import BaseModel
from typing import Literal
from logging import getLogger
logger = getLogger(__name__)

from model.denoise import denoise
from model.sensor import vad_array, asr_array
from model.sovits import stream_io
from ..utils.audio import wave_header_chunk
from ..interview import InterviewManager
from . import session_manager, chat

router = fastapi.APIRouter()
@router.websocket("/ws")
async def ws(websocket: fastapi.WebSocket, session_id: str, user_id: str = None):
    await websocket.accept()
    session = session_manager.get(session_id)
    if session is None:
        await websocket.close()
    else:
        ws_client = WebsocketClient(websocket)
        ws_client.session_id = session_id
        ws_client.user_id = user_id
        session["ws"] = ws_client
        session["chat"] = InterviewManager(user_id)
        await ws_client.run()

@router.get("/api/tts")
async def tts(request: fastapi.Request):
    session_id = request.cookies.get("session_id")
    session = session_manager.get(session_id)
    return fastapi.responses.StreamingResponse(sts_method(session), media_type="audio/wav")


@router.get("/api/history")
async def history(request: fastapi.Request):
    session_id = request.cookies.get("session_id")
    session = session_manager.get(session_id)
    cm: InterviewManager = session["chat"]
    return fastapi.responses.JSONResponse({
        "history": [item.model_dump() for item in cm.data.history]
    })

def sts_method(session: dict[str, any]):
    b = b""
    cm: InterviewManager = session["chat"]
    for blob in stream_io(generate_msg(session)):
        b += blob
        yield blob
    cm.save_audio(b)

def generate_msg(session: dict[str, any]):
    cm: InterviewManager = session["chat"]
    ws: WebsocketClient = session["ws"]
    if len(cm.data.messages) and cm.data.messages[-1].role == "assistant":
        yield cm.data.messages[-1].content
    else:
        for resp in chat(cm.get_llm_message()):
            if resp.type == "char":
                # 流式输出llm的响应
                asyncio.run(ws.ws.send_text("stream:llm:%s" % resp.content))
            if resp.type == "sentence":
                logger.debug("start generate llm sentence: %s" % resp.content)
                yield resp.content
        cm.add_chat(resp.content, "assistant")


class WebsocketMessage(BaseModel):
    action: Literal["init", "record", "finish"]
    param: dict[str, str | int] = {}


class WebsocketClient:
    def __init__(self, ws: fastapi.WebSocket) -> None:
        self.rest_time = 800  # 讲话时，最长允许的停顿时间, 单位ms
        self.min_audio_frame_len = 25 * 0.001  # 最小音频帧应该保证25毫秒
        self.ws = ws
        self.session_id = None # session，便于相互索引
        self.user_id: str = ""
        self.sampleRate: int = 0
        self.audioBuffer: np.ndarray = np.array([], dtype=np.float32)

        self._task_queue = asyncio.Queue()  # 任务队列
        self._running = True

    def _tran_ms_to_audioframe(self, ms: int):
        return int(ms / 1000 * self.sampleRate)

    def _load_audio_buffer(self, blob):
        array = np.frombuffer(blob, dtype=np.int16).astype(np.float32)
        if array.std() > 300:
            # 如果音频片段达到了要求
            self.audioBuffer = np.concatenate(
                [self.audioBuffer, array], dtype=np.float32, axis=0
            )
            return True
        else:
            # 插入空白音频片段，避免问题
            self.audioBuffer = np.concatenate(
                [self.audioBuffer, np.zeros(array.shape[0], dtype=np.float32)],
                dtype=np.float32,
                axis=0,
            )
            return False

    async def asr(self, item: list[int]):
        [startPos, stopPos] = [
            self._tran_ms_to_audioframe(item[0]),
            self._tran_ms_to_audioframe(item[1]),
        ]
        audioBuffer = self.audioBuffer[startPos:stopPos]

        audioPad = (
            int(self.sampleRate * self.min_audio_frame_len) - audioBuffer.shape[0]
        )
        if audioPad > 0:
            audioBuffer = np.concatenate(
                [audioBuffer, np.zeros(audioPad, dtype=np.float32)],
                axis=0,
                dtype=np.float32,
            )

        asr = asr_array(audioBuffer, sampleRate=self.sampleRate, lang="zh")
        logger.debug("asr result: %s" % (asr.clean_text))
        if len(asr.clean_text):
            cm: InterviewManager = session_manager.get(self.session_id)["chat"]
            cm.add_chat(asr.clean_text, "user")
            cm.save_audio(wave_header_chunk(sample_rate=self.sampleRate) + audioBuffer.astype(np.int16).tobytes())
            await self.ws.send_text("stream:asr:%s" % asr.text)
            return True
        return False

    async def valid(self):
        # 验证音频是否存在声音，且停止讲话
        array = self.audioBuffer
        audio_len = (array.shape[0] / self.sampleRate) * 1000  # ms

        [items, param] = vad_array(array, sampleRate=self.sampleRate)
        logger.debug(items)

        if not len(items):
            # 没有有效的音频, 清空缓存
            self.audioBuffer = np.array([], dtype=np.float32)
            return False

        if len(items) > 1:
            # 超过一段的语音内容，识别前几段
            for item in items[:-1]:
                await self.asr(item)
        if audio_len - items[-1][1] > self.rest_time:
            # 超过指定时长没有新的语音输入，意味着结束讲话
            r = await self.asr(items[-1])
            if r:
                await self.ws.send_text("tts:start")
            self.audioBuffer = np.array([], dtype=np.float32)
        elif len(items) > 1:
            # 删除前几段
            self.audioBuffer = self.audioBuffer[
                self._tran_ms_to_audioframe(items[-1][0]) :
            ]

    async def action(self, wm: WebsocketMessage):
        if wm.action == "init":
            self.sampleRate = int(wm.param["sampleRate"])
        elif self.sampleRate <= 0:
            # 还未初始化
            return
        elif wm.action == "record":
            if not self._load_audio_buffer(base64.b64decode(wm.param["audio"])):
                await self.ws.send_text("asr:toolow")
            else:
                await self.ws.send_text("tts:stop")
            await self.valid()

    async def _worker(self):
        """后台任务处理 worker"""
        while self._running:
            try:
                # 从队列中获取任务
                wm = await self._task_queue.get()
                if wm is None:
                    break  # 收到终止信号
                await self.action(wm)
            except Exception as e:
                logger.error(
                    f"Error processing action: {e}", stack_info=True, exc_info=1
                )
            finally:
                self._task_queue.task_done()

    async def run(self):
        """启动 WebSocket 客户端"""
        # 启动后台任务处理 worker
        worker_task = asyncio.create_task(self._worker())

        try:
            while True:
                # 接收 WebSocket 消息
                data = await self.ws.receive_json()
                wm = WebsocketMessage.model_validate(data)
                # 将任务放入队列，由后台 worker 处理
                await self._task_queue.put(wm)
        except fastapi.WebSocketDisconnect:
            logger.error(f"Client disconnected")
        finally:
            # 清理资源
            self._running = False
            await self._task_queue.put(None)  # 发送终止信号
            await worker_task  # 等待 worker 完成
