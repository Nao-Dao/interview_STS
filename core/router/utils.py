from model.sovits import stream_io
from core.utils.snowflake import generate_snowflake_id
from core.interview import InterviewManager
import os
from typing import Protocol, Generator, Any
from importlib.metadata import import_module


cache: dict[int, InterviewManager] = {}

def get_llm_module() -> Any:
    llm_type = os.getenv('LLM', 'chatgpt')
    module_path = f"core.llm.{llm_type}"
    try:
        return import_module(module_path)
    except ImportError as e:
        raise ImportError(f"Could not load LLM module {llm_type}: {e}")
chat = get_llm_module().chat

def stream_text_to_speech(cid):
    b = b""
    for blob in stream_io(generate_msg(cid)):
        b += blob
        yield blob
    yield b""
    
    
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

def save_audio(cid: int = None, audio: bytes = None):
    """
    将音频数据保存到聊天记录当中
    """
    im = _get_im_instance(cid)
    path = im.save_audio(audio)
    im.data.history[-1].audio_path.append(path)
    im.save_data(im.data)