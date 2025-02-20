from  __future__ import annotations
import fastapi
from typing import Annotated, List
router = fastapi.APIRouter()

"""
LLM聊天管理
"""
from .interview import put_llm, generate_msg
from ..model.cosy import stream_io
@router.get("/api/tts")
async def tts(cid: int):
    return fastapi.responses.StreamingResponse(stream_io(generate_msg(cid)), media_type="audio/wav")

from ..model.sensor import asr as sensor
from ..utils.audio import webm2wav
@router.post("/api/asr")
async def asr(files: Annotated[List[bytes], fastapi.File(description="wav or mp3 audios in 16KHz")],
              lang: Annotated[str, fastapi.Form(description="language of audio content")] = "auto",
              cid: Annotated[int, fastapi.Form()] = None):
    resp = sensor(webm2wav(files[0]), lang)
    if len(resp.text):
        await put_llm(resp.text, cid)
    return fastapi.responses.JSONResponse({})

from ..utils.snowflake import generate_snowflake_id
@router.get("/api/id")
async def get_id():
    return fastapi.Response(str(generate_snowflake_id()))
