import pytest
from datetime import datetime

from app.chat.application.use_case.leave_chat_room_use_case import LeaveChatRoomUseCase
from tests.chat.fixtures.fake_chat_room_repository import FakeChatRoomRepository
from app.chat.domain.chat_room import ChatRoom


@pytest.fixture
def repository():
    """테스트용 Fake ChatRoom 저장소"""
    return FakeChatRoomRepository()


@pytest.fixture
def use_case(repository):
    """LeaveChatRoomUseCase"""
    return LeaveChatRoomUseCase(repository)


def test_user1_leaves_chat_room(use_case, repository):
    """user1이 채팅방을 나가면 상태가 left_by_user1로 변경된다"""
    # Given: 활성화된 채팅방
    room = ChatRoom(
        id="room-123",
        user1_id="userA",
        user2_id="userB",
        created_at=datetime.now()
    )
    repository.save(room)

    # When: user1이 채팅방을 나가면
    use_case.execute(room_id="room-123", user_id="userA")

    # Then: 상태가 left_by_user1로 변경된다
    updated_room = repository.find_by_id("room-123")
    assert updated_room.status == "left_by_user1"


def test_user2_leaves_chat_room(use_case, repository):
    """user2가 채팅방을 나가면 상태가 left_by_user2로 변경된다"""
    # Given: 활성화된 채팅방
    room = ChatRoom(
        id="room-123",
        user1_id="userA",
        user2_id="userB",
        created_at=datetime.now()
    )
    repository.save(room)

    # When: user2가 채팅방을 나가면
    use_case.execute(room_id="room-123", user_id="userB")

    # Then: 상태가 left_by_user2로 변경된다
    updated_room = repository.find_by_id("room-123")
    assert updated_room.status == "left_by_user2"


def test_both_users_leave_chat_room(use_case, repository):
    """양쪽 사용자가 모두 나가면 상태가 closed로 변경된다"""
    # Given: 활성화된 채팅방
    room = ChatRoom(
        id="room-123",
        user1_id="userA",
        user2_id="userB",
        created_at=datetime.now()
    )
    repository.save(room)

    # When: 먼저 user1이 나가고
    use_case.execute(room_id="room-123", user_id="userA")

    # Then: 상태가 left_by_user1로 변경된다
    updated_room = repository.find_by_id("room-123")
    assert updated_room.status == "left_by_user1"

    # When: user2도 나가면
    use_case.execute(room_id="room-123", user_id="userB")

    # Then: 상태가 closed로 변경된다
    final_room = repository.find_by_id("room-123")
    assert final_room.status == "closed"


def test_leave_nonexistent_room_raises_error(use_case, repository):
    """존재하지 않는 채팅방을 나가려고 하면 에러가 발생한다"""
    # Given: 존재하지 않는 채팅방 ID
    room_id = "nonexistent-room"

    # When & Then: 채팅방을 나가려고 하면 ValueError가 발생한다
    with pytest.raises(ValueError, match="채팅방을 찾을 수 없습니다"):
        use_case.execute(room_id=room_id, user_id="userA")


def test_leave_room_by_non_participant_raises_error(use_case, repository):
    """참여자가 아닌 사용자가 나가려고 하면 에러가 발생한다"""
    # Given: 채팅방
    room = ChatRoom(
        id="room-123",
        user1_id="userA",
        user2_id="userB",
        created_at=datetime.now()
    )
    repository.save(room)

    # When & Then: 참여자가 아닌 사용자가 나가려고 하면 ValueError가 발생한다
    with pytest.raises(ValueError):
        use_case.execute(room_id="room-123", user_id="userC")
