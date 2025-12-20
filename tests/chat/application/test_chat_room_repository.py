import pytest

from app.chat.domain.chat_room import ChatRoom
from tests.chat.fixtures.fake_chat_room_repository import FakeChatRoomRepository


@pytest.fixture
def repository():
    """테스트용 Fake ChatRoom 저장소"""
    return FakeChatRoomRepository()


def test_save_and_find_room_by_id(repository):
    """채팅방을 저장하고 id로 조회할 수 있다"""
    # Given: 유효한 채팅방
    room = ChatRoom(
        id="room-123",
        user1_id="userA",
        user2_id="userB"
    )

    # When: 채팅방을 저장하고 조회하면
    repository.save(room)
    found = repository.find_by_id("room-123")

    # Then: 저장된 채팅방을 찾을 수 있다
    assert found is not None
    assert found.id == "room-123"
    assert found.user1_id == "userA"
    assert found.user2_id == "userB"


def test_find_nonexistent_room_returns_none(repository):
    """존재하지 않는 id로 조회하면 None을 반환한다"""
    # When: 존재하지 않는 채팅방을 조회하면
    found = repository.find_by_id("nonexistent-room")

    # Then: None을 반환한다
    assert found is None


def test_find_rooms_by_user_id(repository):
    """user_id로 해당 사용자가 참여한 채팅방 목록을 조회할 수 있다"""
    # Given: 여러 채팅방
    room1 = ChatRoom(id="room-1", user1_id="userA", user2_id="userB")
    room2 = ChatRoom(id="room-2", user1_id="userA", user2_id="userC")
    room3 = ChatRoom(id="room-3", user1_id="userB", user2_id="userC")

    repository.save(room1)
    repository.save(room2)
    repository.save(room3)

    # When: userA의 채팅방을 조회하면
    rooms = repository.find_by_user_id("userA")

    # Then: userA가 참여한 채팅방만 반환된다
    assert len(rooms) == 2
    room_ids = [r.id for r in rooms]
    assert "room-1" in room_ids
    assert "room-2" in room_ids
    assert "room-3" not in room_ids


def test_find_rooms_by_user_id_returns_empty_list_for_no_rooms(repository):
    """채팅방이 없는 사용자는 빈 리스트를 반환한다"""
    # When: 채팅방이 없는 사용자를 조회하면
    rooms = repository.find_by_user_id("userWithNoRooms")

    # Then: 빈 리스트를 반환한다
    assert rooms == []