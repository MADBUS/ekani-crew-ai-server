from app.chat.application.port.chat_message_repository_port import ChatMessageRepositoryPort
from app.chat.domain.chat_message import ChatMessage


class SaveChatMessageUseCase:
    """채팅 메시지 저장 유스케이스"""

    def __init__(self, repository: ChatMessageRepositoryPort):
        self._repository = repository

    def execute(
        self,
        message_id: str,
        room_id: str,
        sender_id: str,
        content: str
    ) -> str:
        """채팅 메시지를 저장하고 message_id를 반환한다"""
        # 새로운 메시지 생성 (ChatMessage가 유효성 검증)
        message = ChatMessage(
            id=message_id,
            room_id=room_id,
            sender_id=sender_id,
            content=content
        )

        # 저장
        self._repository.save(message)

        return message_id