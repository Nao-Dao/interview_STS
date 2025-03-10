from ..llm import ChatResponse, ChatMessage
from typing import List


class AudioMessage(ChatMessage):
    audio_path: List[str] = []
