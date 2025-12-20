import pytest
from datetime import datetime
from app.chat.domain.chat_message import ChatMessage


def test_chat_message_creates_with_required_fields():
    """필수 필드로 ChatMessage 객체를 생성할 수 있다"""
    # Given: 유효한 메시지 정보
    message_id = "msg-uuid-123"
    room_id = "room-uuid-456"
    sender_id = "user-789"
    content = "안녕하세요!"
    created_at = datetime.now()

    # When: ChatMessage 객체를 생성하면
    message = ChatMessage(
        id=message_id,
        room_id=room_id,
        sender_id=sender_id,
        content=content,
        created_at=created_at
    )

    # Then: 정상적으로 생성되고 값을 조회할 수 있다
    assert message.id == message_id
    assert message.room_id == room_id
    assert message.sender_id == sender_id
    assert message.content == content
    assert message.created_at == created_at


def test_chat_message_rejects_empty_id():
    """빈 id를 거부한다"""
    # Given: 빈 message_id
    message_id = ""
    room_id = "room-123"
    sender_id = "user-456"
    content = "안녕하세요!"

    # When & Then: ChatMessage 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError):
        ChatMessage(id=message_id, room_id=room_id, sender_id=sender_id, content=content)


def test_chat_message_rejects_empty_room_id():
    """빈 room_id를 거부한다"""
    # Given: 빈 room_id
    message_id = "msg-123"
    room_id = ""
    sender_id = "user-456"
    content = "안녕하세요!"

    # When & Then: ChatMessage 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError):
        ChatMessage(id=message_id, room_id=room_id, sender_id=sender_id, content=content)


def test_chat_message_rejects_empty_sender_id():
    """빈 sender_id를 거부한다"""
    # Given: 빈 sender_id
    message_id = "msg-123"
    room_id = "room-456"
    sender_id = ""
    content = "안녕하세요!"

    # When & Then: ChatMessage 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError):
        ChatMessage(id=message_id, room_id=room_id, sender_id=sender_id, content=content)


def test_chat_message_rejects_empty_content():
    """빈 content를 거부한다"""
    # Given: 빈 content
    message_id = "msg-123"
    room_id = "room-456"
    sender_id = "user-789"
    content = ""

    # When & Then: ChatMessage 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError):
        ChatMessage(id=message_id, room_id=room_id, sender_id=sender_id, content=content)


def test_chat_message_rejects_whitespace_only_content():
    """공백만 있는 content를 거부한다"""
    # Given: 공백만 있는 content
    message_id = "msg-123"
    room_id = "room-456"
    sender_id = "user-789"
    content = "   "

    # When & Then: ChatMessage 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError):
        ChatMessage(id=message_id, room_id=room_id, sender_id=sender_id, content=content)


def test_chat_message_auto_generates_created_at_if_not_provided():
    """created_at이 제공되지 않으면 자동으로 생성한다"""
    # Given: created_at 없이 메시지 정보
    message_id = "msg-123"
    room_id = "room-456"
    sender_id = "user-789"
    content = "안녕하세요!"

    # When: created_at 없이 ChatMessage를 생성하면
    message = ChatMessage(
        id=message_id,
        room_id=room_id,
        sender_id=sender_id,
        content=content
    )

    # Then: created_at이 자동으로 설정된다
    assert isinstance(message.created_at, datetime)