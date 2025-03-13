from .chat_message import ChatMessage
from typing import List


class AudioMessage(ChatMessage):
    audio_path: List[str] = []
