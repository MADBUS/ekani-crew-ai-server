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
    """다른 사용자 조합인데 동일한 room_id를 사용하려고 하면 에러를 발생시킨다"""
    # Given: 이미 생성된 채팅방 (userA와 userB)
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

    # When & Then: 다른 사용자 조합(userC와 userD)인데 같은 room_id로 생성하려고 하면 에러가 발생한다
    with pytest.raises(ValueError, match="이미 존재하는 채팅방입니다"):
        use_case.execute(
            room_id=room_id,
            user1_id="userC",
            user2_id="userD",
            timestamp=timestamp
        )


def test_create_chat_room_returns_existing_room_for_same_users(use_case, repository):
    """동일한 두 사용자에 대해 이미 채팅방이 있으면 기존 room_id를 반환한다"""
    # Given: 이미 생성된 채팅방
    first_room_id = "room-uuid-123"
    user1_id = "userA"
    user2_id = "userB"
    timestamp1 = datetime.now()

    created_room_id = use_case.execute(
        room_id=first_room_id,
        user1_id=user1_id,
        user2_id=user2_id,
        timestamp=timestamp1
    )
    assert created_room_id == first_room_id

    # When: 같은 두 사용자로 새로운 채팅방을 생성하려고 하면
    second_room_id = "room-uuid-456"  # 다른 room_id
    timestamp2 = datetime.now()

    returned_room_id = use_case.execute(
        room_id=second_room_id,
        user1_id=user1_id,
        user2_id=user2_id,
        timestamp=timestamp2
    )

    # Then: 기존 채팅방의 room_id를 반환한다
    assert returned_room_id == first_room_id
    assert repository.find_by_id(second_room_id) is None  # 새로운 방은 생성되지 않음
    assert repository.find_by_id(first_room_id) is not None  # 기존 방은 존재


def test_create_chat_room_returns_existing_room_regardless_of_user_order(use_case, repository):
    """user1_id와 user2_id의 순서와 관계없이 동일한 두 사용자면 기존 room_id를 반환한다"""
    # Given: userA와 userB로 생성된 채팅방
    first_room_id = "room-uuid-123"
    user1_id = "userA"
    user2_id = "userB"
    timestamp1 = datetime.now()

    created_room_id = use_case.execute(
        room_id=first_room_id,
        user1_id=user1_id,
        user2_id=user2_id,
        timestamp=timestamp1
    )
    assert created_room_id == first_room_id

    # When: userB와 userA 순서를 바꿔서 채팅방을 생성하려고 하면
    second_room_id = "room-uuid-456"
    timestamp2 = datetime.now()

    returned_room_id = use_case.execute(
        room_id=second_room_id,
        user1_id=user2_id,  # 순서 바뀜
        user2_id=user1_id,  # 순서 바뀜
        timestamp=timestamp2
    )

    # Then: 기존 채팅방의 room_id를 반환한다
    assert returned_room_id == first_room_id
    assert repository.find_by_id(second_room_id) is None  # 새로운 방은 생성되지 않음