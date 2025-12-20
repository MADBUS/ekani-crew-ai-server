import pytest
from datetime import datetime, timedelta

from app.chat.domain.chat_message import ChatMessage
from tests.chat.fixtures.fake_chat_message_repository import FakeChatMessageRepository


@pytest.fixture
def repository():
    """테스트용 Fake ChatMessage 저장소"""
    return FakeChatMessageRepository()


def test_save_and_find_message_by_id(repository):
    """메시지를 저장하고 id로 조회할 수 있다"""
    # Given: 유효한 메시지
    message = ChatMessage(
        id="msg-123",
        room_id="room-456",
        sender_id="user-789",
        content="안녕하세요!"
    )

    # When: 메시지를 저장하고 조회하면
    repository.save(message)
    found = repository.find_by_id("msg-123")

    # Then: 저장된 메시지를 찾을 수 있다
    assert found is not None
    assert found.id == "msg-123"
    assert found.room_id == "room-456"
    assert found.sender_id == "user-789"
    assert found.content == "안녕하세요!"


def test_find_nonexistent_message_returns_none(repository):
    """존재하지 않는 id로 조회하면 None을 반환한다"""
    # When: 존재하지 않는 메시지를 조회하면
    found = repository.find_by_id("nonexistent-msg")

    # Then: None을 반환한다
    assert found is None


def test_find_messages_by_room_id(repository):
    """room_id로 해당 채팅방의 메시지 목록을 조회할 수 있다"""
    # Given: 여러 채팅방의 메시지
    msg1 = ChatMessage(id="msg-1", room_id="room-A", sender_id="user1", content="첫 번째")
    msg2 = ChatMessage(id="msg-2", room_id="room-A", sender_id="user2", content="두 번째")
    msg3 = ChatMessage(id="msg-3", room_id="room-B", sender_id="user1", content="다른 방")

    repository.save(msg1)
    repository.save(msg2)
    repository.save(msg3)

    # When: room-A의 메시지를 조회하면
    messages = repository.find_by_room_id("room-A")

    # Then: room-A의 메시지만 반환된다
    assert len(messages) == 2
    message_ids = [m.id for m in messages]
    assert "msg-1" in message_ids
    assert "msg-2" in message_ids
    assert "msg-3" not in message_ids


def test_find_messages_by_room_id_returns_sorted_by_created_at(repository):
    """room_id로 메시지를 조회할 때 생성 시간순으로 정렬된다"""
    # Given: 시간이 다른 메시지들
    now = datetime.now()
    msg1 = ChatMessage(
        id="msg-1",
        room_id="room-A",
        sender_id="user1",
        content="첫 번째",
        created_at=now - timedelta(seconds=10)
    )
    msg2 = ChatMessage(
        id="msg-2",
        room_id="room-A",
        sender_id="user2",
        content="두 번째",
        created_at=now - timedelta(seconds=5)
    )
    msg3 = ChatMessage(
        id="msg-3",
        room_id="room-A",
        sender_id="user1",
        content="세 번째",
        created_at=now
    )

    # 순서 섞어서 저장
    repository.save(msg2)
    repository.save(msg1)
    repository.save(msg3)

    # When: room-A의 메시지를 조회하면
    messages = repository.find_by_room_id("room-A")

    # Then: 시간 순서대로 정렬되어 반환된다
    assert len(messages) == 3
    assert messages[0].id == "msg-1"  # 가장 오래된 메시지
    assert messages[1].id == "msg-2"
    assert messages[2].id == "msg-3"  # 가장 최근 메시지


def test_find_messages_by_room_id_returns_empty_list_for_no_messages(repository):
    """메시지가 없는 채팅방은 빈 리스트를 반환한다"""
    # When: 메시지가 없는 채팅방을 조회하면
    messages = repository.find_by_room_id("room-with-no-messages")

    # Then: 빈 리스트를 반환한다
    assert messages == []