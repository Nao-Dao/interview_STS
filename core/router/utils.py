from model.sovits import stream_io
from core.utils.snowflake import generate_snowflake_id
from core.interview import InterviewManager
import os
from typing import Protocol, Generator, Any
from importlib.metadata import import_module


cache: dict[int, InterviewManager] = {}


def get_llm_module() -> Any:
    llm_type = os.getenv("LLM", "chatgpt")
    module_path = f"core.llm.{llm_type}"
    try:
        return import_module(module_path)
    except ImportError as e:
        raise ImportError(f"Could not load LLM module {llm_type}: {e}")


chat = get_llm_module().chat


def stream_text_to_speech(user_id):
    b = b""
    for blob in stream_io(generate_msg(user_id)):
        b += blob
        yield blob
    yield b""


def generate_msg(user_id: str = None):
    """
    产生LLM产生的语音数据
    """
    im = _get_im_instance(user_id)
    if len(im.data.messages) and im.data.messages[-1].role == "assistant":
        yield im.data.messages[-1].content
    else:
        for resp in chat(im.get_llm_message()):
            if resp.type == "sentence":
                yield resp.content
        im.add_chat(resp.content, "assistant")
        im.save_data(im.data)


def _get_im_instance(user_id: str = None):
    if user_id is None:
        user_id = generate_snowflake_id()
    if not isinstance(user_id, str):
        user_id = str(user_id)
    if user_id not in cache:
        cache[user_id] = InterviewManager(user_id)
    return cache[user_id]


def put_llm(msg: str, user_id: str = None):
    """
    放置用户的聊天记录
    """
    im = _get_im_instance(user_id)
    im.add_chat(msg, "user")
    im.save_data(im.data)


def save_audio(user_id: str = None, audio: bytes = None):
    """
    将音频数据保存到聊天记录当中
    """
    im = _get_im_instance(user_id)
    path = im.save_audio(audio)
    im.data.history[-1].audio_path.append(path)
    im.save_data(im.data)
