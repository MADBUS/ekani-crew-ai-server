from app.chat.application.port.chat_message_repository_port import ChatMessageRepositoryPort
from app.chat.domain.chat_message import ChatMessage


class FakeChatMessageRepository(ChatMessageRepositoryPort):
    """테스트용 Fake ChatMessage 저장소"""

    def __init__(self):
        self._messages: dict[str, ChatMessage] = {}

    def save(self, message: ChatMessage) -> None:
        self._messages[message.id] = message

    def find_by_id(self, message_id: str) -> ChatMessage | None:
        return self._messages.get(message_id)

    def find_by_room_id(self, room_id: str) -> list[ChatMessage]:
        messages = [
            msg for msg in self._messages.values()
            if msg.room_id == room_id
        ]
        # created_at 순으로 정렬
        return sorted(messages, key=lambda m: m.created_at)