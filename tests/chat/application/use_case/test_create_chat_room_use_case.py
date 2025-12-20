import pytest
from datetime import datetime

from app.chat.application.use_case.create_chat_room_use_case import CreateChatRoomUseCase
from tests.chat.fixtures.fake_chat_room_repository import FakeChatRoomRepository


@pytest.fixture
def repository():
    """테스트용 Fake ChatRoom 저장소"""
    return FakeChatRoomRepository()


@pytest.fixture
def use_case(repository):
    """CreateChatRoomUseCase"""
    return CreateChatRoomUseCase(repository)


def test_create_chat_room_with_match_data(use_case, repository):
    """match 도메인에서 전달한 데이터로 채팅방을 생성한다"""
    # Given: match 도메인에서 전달한 데이터
    room_id = "room-uuid-123"
    user1_id = "userA"
    user2_id = "userB"
    timestamp = datetime.now()

    # When: 채팅방을 생성하면
    created_room_id = use_case.execute(
        room_id=room_id,
        user1_id=user1_id,
        user2_id=user2_id,
        timestamp=timestamp
    )

    # Then: 채팅방이 생성되고 저장된다
    assert created_room_id == room_id
    saved_room = repository.find_by_id(room_id)
    assert saved_room is not None
    assert saved_room.id == room_id
    assert saved_room.user1_id == user1_id
    assert saved_room.user2_id == user2_id
    assert saved_room.created_at == timestamp


def test_create_chat_room_prevents_duplicate_creation(use_case, repository):
    """동일한 room_id로 중복 생성을 방지한다"""
    # Given: 이미 생성된 채팅방
    room_id = "room-uuid-123"
    user1_id = "userA"
    user2_id = "userB"
    timestamp = datetime.now()

    use_case.execute(
        room_id=room_id,
        user1_id=user1_id,
        user2_id=user2_id,
        timestamp=timestamp
    )

    # When & Then: 동일한 room_id로 다시 생성하려고 하면 에러가 발생한다
    with pytest.raises(ValueError, match="이미 존재하는 채팅방입니다"):
        use_case.execute(
            room_id=room_id,
            user1_id=user1_id,
            user2_id=user2_id,
            timestamp=timestamp
        )