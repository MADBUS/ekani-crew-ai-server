from app.chat.application.port.chat_room_repository_port import ChatRoomRepositoryPort
from app.chat.application.port.chat_message_repository_port import ChatMessageRepositoryPort
from app.chat.application.dto.chat_room_with_preview_dto import ChatRoomWithPreviewDTO


class GetMyChatRoomsUseCase:
    """사용자의 채팅방 목록 조회 유스케이스"""

    def __init__(
        self,
        room_repository: ChatRoomRepositoryPort,
        message_repository: ChatMessageRepositoryPort
    ):
        self._room_repository = room_repository
        self._message_repository = message_repository

    def execute(self, user_id: str) -> list[ChatRoomWithPreviewDTO]:
        """사용자가 참여한 채팅방 목록을 조회하고, 각 방의 최신 메시지와 읽지 않은 메시지 수를 포함한다"""
        rooms = self._room_repository.find_by_user_id(user_id)

        room_previews = []
        for room in rooms:
            # 각 채팅방의 모든 메시지를 조회
            messages = self._message_repository.find_by_room_id(room.id)

            # 최신 메시지 찾기 (마지막 메시지)
            latest_message = messages[-1] if messages else None

            # 마지막 읽은 시간 가져오기
            last_read_at = room.get_last_read_at(user_id)

            # 읽지 않은 메시지 수 계산 (마지막 읽은 시간 이후 상대방이 보낸 메시지)
            if last_read_at is None:
                # 한 번도 읽지 않은 경우: 모든 상대방 메시지
                unread_count = sum(
                    1 for msg in messages
                    if msg.sender_id != user_id
                )
            else:
                # 마지막 읽은 시간 이후의 상대방 메시지만
                unread_count = sum(
                    1 for msg in messages
                    if msg.sender_id != user_id and msg.created_at > last_read_at
                )

            room_preview = ChatRoomWithPreviewDTO(
                id=room.id,
                user1_id=room.user1_id,
                user2_id=room.user2_id,
                created_at=room.created_at,
                latest_message=latest_message,
                unread_count=unread_count
            )
            room_previews.append(room_preview)

        return room_previews
