from __future__ import annotations
import os
import time
import threading

from core.utils.cache import cache as CacheUtils
from core.utils.snowflake import generate_snowflake_id
from core.interview import InterviewManager

cache: dict[int, InterviewManager] = {}

module = __import__(f"core.llm.{os.getenv('LLM', 'chatgpt')}", globals(), locals(), ["chat"])
chat = module.chat

def timeHandler():
    # 定时任务
    while True:
        for key, item in cache.items():
            print("check: %s" % str(key))
            item.check_llm_message(chat)
            if item.judge(chat):
                item.next()
        time.sleep(30) # 30s 执行一次
thread = threading.Thread(target=timeHandler, daemon=True)
thread.start()


def _get_im_instance(cid: int = None):
    if cid is None:
        cid = generate_snowflake_id()
    if not isinstance(cid, int):
       cid = int(cid) 
    if cid not in cache:
        cache[cid] = InterviewManager(cid)
    return cache[cid]


def put_llm(msg: str, cid: int = None):
    """
    放置用户的聊天记录
    """
    im = _get_im_instance(cid)
    im.add_chat(msg, "user")
    im.save_data(im.data)


def generate_msg(cid: int = None):
    """
    产生LLM产生的语音数据
    """
    im = _get_im_instance(cid)
    if len(im.data.messages) and im.data.messages[-1].role == "assistant":
        yield im.data.messages[-1].content
    else:
        for resp in chat(im.get_llm_message()):
            if resp.type == "sentence":
                yield resp.content
        im.add_chat(resp.content, "assistant")
        im.save_data(im.data)


def save_audio(cid: int = None, audio: bytes = None):
    """
    将音频数据保存到聊天记录当中
    """
    im = _get_im_instance(cid)
    path = CacheUtils.get_path(CacheUtils.save(audio, "wav"))
    im.data.history[-1].audio_path.append(path)
    im.save_data(im.data)


