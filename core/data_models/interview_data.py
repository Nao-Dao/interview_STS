from pydantic import BaseModel
from .chat_message import ChatMessage
from .audio_message import AudioMessage


class InterviewData(BaseModel):
    # id 来自微信openid
    user_id: str
    # 访问的进度
    progress: int
    # 访谈的议题, 需要从议题里面选择
    questions: list[str]
    # 聊天历史记录
    history: list[AudioMessage]
    # 与llm聊天的记录
    # 与聊天的历史记录不同，这个需要限制最大值
    # 这里默认不超过5000个字
    messages: list[ChatMessage]
