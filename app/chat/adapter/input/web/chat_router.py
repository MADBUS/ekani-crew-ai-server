from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.chat.application.use_case.get_chat_history_use_case import GetChatHistoryUseCase
from app.chat.application.use_case.get_my_chat_rooms_use_case import GetMyChatRoomsUseCase
from app.chat.application.use_case.mark_chat_room_as_read_use_case import MarkChatRoomAsReadUseCase
from app.chat.application.port.chat_message_repository_port import ChatMessageRepositoryPort
from app.chat.application.port.chat_room_repository_port import ChatRoomRepositoryPort
from app.chat.infrastructure.repository.mysql_chat_message_repository import MySQLChatMessageRepository
from app.chat.infrastructure.repository.mysql_chat_room_repository import MySQLChatRoomRepository
from config.database import get_db

chat_router = APIRouter()


def get_chat_message_repository(db: Session = Depends(get_db)) -> ChatMessageRepositoryPort:
    """ChatMessage Repository 의존성 주입"""
    return MySQLChatMessageRepository(db)


def get_chat_room_repository(db: Session = Depends(get_db)) -> ChatRoomRepositoryPort:
    """ChatRoom Repository 의존성 주입"""
    return MySQLChatRoomRepository(db)


class ChatMessageResponse(BaseModel):
    """채팅 메시지 응답 DTO"""
    id: str
    room_id: str
    sender_id: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    """채팅 기록 응답 DTO"""
    messages: list[ChatMessageResponse]


class ChatRoomPreviewResponse(BaseModel):
    """채팅방 미리보기 응답 DTO"""
    id: str
    user1_id: str
    user2_id: str
    created_at: datetime
    latest_message: Optional[ChatMessageResponse] = None
    unread_count: int = 0


class MyChatRoomsResponse(BaseModel):
    """내 채팅방 목록 응답 DTO"""
    rooms: list[ChatRoomPreviewResponse]


@chat_router.get("/chat/{room_id}/messages", response_model=ChatHistoryResponse)
def get_chat_history(
    room_id: str,
    repository: ChatMessageRepositoryPort = Depends(get_chat_message_repository)
):
    """
    채팅방의 메시지 기록을 조회한다.

    - room_id: 채팅방 ID
    - 반환: 시간순으로 정렬된 메시지 목록
    """
    use_case = GetChatHistoryUseCase(repository)
    messages = use_case.execute(room_id)

    message_responses = [
        ChatMessageResponse(
            id=msg.id,
            room_id=msg.room_id,
            sender_id=msg.sender_id,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in messages
    ]

    return ChatHistoryResponse(messages=message_responses)


@chat_router.get("/chat/rooms/my", response_model=MyChatRoomsResponse)
def get_my_chat_rooms(
    user_id: str,
    room_repository: ChatRoomRepositoryPort = Depends(get_chat_room_repository),
    message_repository: ChatMessageRepositoryPort = Depends(get_chat_message_repository)
):
    """
    사용자의 채팅방 목록을 조회한다.

    - user_id: 사용자 ID
    - 반환: 최신 메시지 미리보기와 읽지 않은 메시지 수를 포함한 채팅방 목록
    """
    use_case = GetMyChatRoomsUseCase(room_repository, message_repository)
    room_previews = use_case.execute(user_id)

    room_responses = []
    for preview in room_previews:
        latest_message_response = None
        if preview.latest_message:
            latest_message_response = ChatMessageResponse(
                id=preview.latest_message.id,
                room_id=preview.latest_message.room_id,
                sender_id=preview.latest_message.sender_id,
                content=preview.latest_message.content,
                created_at=preview.latest_message.created_at
            )

        room_response = ChatRoomPreviewResponse(
            id=preview.id,
            user1_id=preview.user1_id,
            user2_id=preview.user2_id,
            created_at=preview.created_at,
            latest_message=latest_message_response,
            unread_count=preview.unread_count
        )
        room_responses.append(room_response)

    return MyChatRoomsResponse(rooms=room_responses)


@chat_router.post("/chat/{room_id}/read")
def mark_room_as_read(
    room_id: str,
    user_id: str,
    room_repository: ChatRoomRepositoryPort = Depends(get_chat_room_repository)
):
    """
    채팅방의 메시지를 읽음 처리한다.

    - room_id: 채팅방 ID
    - user_id: 읽음 처리할 사용자 ID (query parameter)
    """
    use_case = MarkChatRoomAsReadUseCase(room_repository)
    use_case.execute(room_id, user_id)

    return {"status": "success", "message": "채팅방이 읽음 처리되었습니다"}
