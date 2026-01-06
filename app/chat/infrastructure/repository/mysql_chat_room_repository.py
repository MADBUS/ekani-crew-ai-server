from sqlalchemy.orm import Session

from app.chat.application.port.chat_room_repository_port import ChatRoomRepositoryPort
from app.chat.domain.chat_room import ChatRoom
from app.chat.infrastructure.model.chat_room_model import ChatRoomModel


class MySQLChatRoomRepository(ChatRoomRepositoryPort):
    """MySQL 기반 채팅방 저장소"""

    def __init__(self, db_session: Session):
        self._db = db_session

    def save(self, room: ChatRoom) -> None:
        """채팅방을 저장한다 (insert 또는 update)"""
        room_model = ChatRoomModel(
            id=room.id,
            user1_id=room.user1_id,
            user2_id=room.user2_id,
            created_at=room.created_at,
            user1_last_read_at=room.user1_last_read_at,
            user2_last_read_at=room.user2_last_read_at,
            status=room.status,
        )
        self._db.merge(room_model)
        self._db.commit()

    def find_by_id(self, room_id: str) -> ChatRoom | None:
        """id로 채팅방을 조회한다"""
        room_model = self._db.query(ChatRoomModel).filter(
            ChatRoomModel.id == room_id
        ).first()

        if room_model is None:
            return None

        return ChatRoom(
            id=room_model.id,
            user1_id=room_model.user1_id,
            user2_id=room_model.user2_id,
            created_at=room_model.created_at,
            user1_last_read_at=room_model.user1_last_read_at,
            user2_last_read_at=room_model.user2_last_read_at,
            status=room_model.status,
        )

    def find_by_user_id(self, user_id: str) -> list[ChatRoom]:
        """user_id로 해당 사용자가 참여한 채팅방 목록을 조회한다 (나간 채팅방 제외)"""
        room_models = self._db.query(ChatRoomModel).filter(
            (
                (ChatRoomModel.user1_id == user_id) &
                (~ChatRoomModel.status.in_(["left_by_user1", "closed"]))
            ) | (
                (ChatRoomModel.user2_id == user_id) &
                (~ChatRoomModel.status.in_(["left_by_user2", "closed"]))
            )
        ).order_by(ChatRoomModel.created_at.desc()).all()

        return [
            ChatRoom(
                id=model.id,
                user1_id=model.user1_id,
                user2_id=model.user2_id,
                created_at=model.created_at,
                user1_last_read_at=model.user1_last_read_at,
                user2_last_read_at=model.user2_last_read_at,
                status=model.status,
            )
            for model in room_models
        ]

    def find_by_users(self, user1_id: str, user2_id: str) -> ChatRoom | None:
        """두 사용자 간의 활성 채팅방을 조회한다 (순서 무관, active 상태만)"""
        room_model = self._db.query(ChatRoomModel).filter(
            (
                ((ChatRoomModel.user1_id == user1_id) & (ChatRoomModel.user2_id == user2_id)) |
                ((ChatRoomModel.user1_id == user2_id) & (ChatRoomModel.user2_id == user1_id))
            ) &
            (ChatRoomModel.status == "active")
        ).first()

        if room_model is None:
            return None

        return ChatRoom(
            id=room_model.id,
            user1_id=room_model.user1_id,
            user2_id=room_model.user2_id,
            created_at=room_model.created_at,
            user1_last_read_at=room_model.user1_last_read_at,
            user2_last_read_at=room_model.user2_last_read_at,
            status=room_model.status,
        )