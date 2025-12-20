import pytest
from datetime import datetime
from app.chat.domain.chat_room import ChatRoom


def test_chat_room_creates_with_required_fields():
    """필수 필드로 ChatRoom 객체를 생성할 수 있다"""
    # Given: match 도메인에서 전달한 채팅방 정보
    room_id = "room-uuid-123"
    user1_id = "userA"
    user2_id = "userB"
    created_at = datetime.now()

    # When: ChatRoom 객체를 생성하면
    room = ChatRoom(
        id=room_id,
        user1_id=user1_id,
        user2_id=user2_id,
        created_at=created_at
    )

    # Then: 정상적으로 생성되고 값을 조회할 수 있다
    assert room.id == room_id
    assert room.user1_id == user1_id
    assert room.user2_id == user2_id
    assert room.created_at == created_at


def test_chat_room_rejects_empty_id():
    """빈 id를 거부한다"""
    # Given: 빈 room_id
    room_id = ""
    user1_id = "userA"
    user2_id = "userB"

    # When & Then: ChatRoom 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError):
        ChatRoom(id=room_id, user1_id=user1_id, user2_id=user2_id)


def test_chat_room_rejects_empty_user1_id():
    """빈 user1_id를 거부한다"""
    # Given: 빈 user1_id
    room_id = "room-123"
    user1_id = ""
    user2_id = "userB"

    # When & Then: ChatRoom 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError):
        ChatRoom(id=room_id, user1_id=user1_id, user2_id=user2_id)


def test_chat_room_rejects_empty_user2_id():
    """빈 user2_id를 거부한다"""
    # Given: 빈 user2_id
    room_id = "room-123"
    user1_id = "userA"
    user2_id = ""

    # When & Then: ChatRoom 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError):
        ChatRoom(id=room_id, user1_id=user1_id, user2_id=user2_id)


def test_chat_room_auto_generates_created_at_if_not_provided():
    """created_at이 제공되지 않으면 자동으로 생성한다"""
    # Given: created_at 없이 채팅방 정보
    room_id = "room-123"
    user1_id = "userA"
    user2_id = "userB"

    # When: created_at 없이 ChatRoom을 생성하면
    room = ChatRoom(id=room_id, user1_id=user1_id, user2_id=user2_id)

    # Then: created_at이 자동으로 설정된다
    assert isinstance(room.created_at, datetime)