"""
基础的聊天管理
"""
from __future__ import annotations
from pydantic import BaseModel
from typing_extensions import Literal, List, Generator, Callable

class ChatResponse(BaseModel):
    type: Literal[
        "char",
        "sentence",
        "finish"
    ]
    content: str

class ChatMessage(BaseModel):
    role: Literal[
        "system",
        "assistant",
        "user"
    ]
    content: str

Chat = Callable[[List[ChatMessage]], Generator[ChatResponse]]
