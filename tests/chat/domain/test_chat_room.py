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


def test_mark_read_by_user1_updates_user1_last_read_at():
    """user1이 읽음 처리하면 user1_last_read_at이 업데이트된다"""
    # Given: 채팅방
    room = ChatRoom(id="room-123", user1_id="userA", user2_id="userB")
    read_time = datetime(2025, 12, 29, 10, 0, 0)

    # When: user1이 읽음 처리하면
    room.mark_read_by_user("userA", read_time)

    # Then: user1_last_read_at이 업데이트된다
    assert room.user1_last_read_at == read_time
    assert room.user2_last_read_at is None


def test_mark_read_by_user2_updates_user2_last_read_at():
    """user2가 읽음 처리하면 user2_last_read_at이 업데이트된다"""
    # Given: 채팅방
    room = ChatRoom(id="room-123", user1_id="userA", user2_id="userB")
    read_time = datetime(2025, 12, 29, 10, 0, 0)

    # When: user2가 읽음 처리하면
    room.mark_read_by_user("userB", read_time)

    # Then: user2_last_read_at이 업데이트된다
    assert room.user1_last_read_at is None
    assert room.user2_last_read_at == read_time


def test_mark_read_by_invalid_user_raises_error():
    """참여자가 아닌 사용자가 읽음 처리하면 에러가 발생한다"""
    # Given: 채팅방
    room = ChatRoom(id="room-123", user1_id="userA", user2_id="userB")

    # When & Then: 참여자가 아닌 사용자가 읽음 처리하면 ValueError가 발생한다
    with pytest.raises(ValueError):
        room.mark_read_by_user("userC")


def test_get_last_read_at_returns_user1_read_time():
    """user1의 마지막 읽은 시간을 반환한다"""
    # Given: user1이 읽음 처리한 채팅방
    room = ChatRoom(id="room-123", user1_id="userA", user2_id="userB")
    read_time = datetime(2025, 12, 29, 10, 0, 0)
    room.mark_read_by_user("userA", read_time)

    # When: user1의 마지막 읽은 시간을 조회하면
    last_read = room.get_last_read_at("userA")

    # Then: 읽은 시간이 반환된다
    assert last_read == read_time


def test_get_last_read_at_returns_none_if_never_read():
    """한 번도 읽지 않은 경우 None을 반환한다"""
    # Given: 읽지 않은 채팅방
    room = ChatRoom(id="room-123", user1_id="userA", user2_id="userB")

    # When: 마지막 읽은 시간을 조회하면
    last_read = room.get_last_read_at("userA")

    # Then: None이 반환된다
    assert last_read is None


def test_get_last_read_at_for_invalid_user_raises_error():
    """참여자가 아닌 사용자의 읽은 시간 조회 시 에러가 발생한다"""
    # Given: 채팅방
    room = ChatRoom(id="room-123", user1_id="userA", user2_id="userB")

    # When & Then: 참여자가 아닌 사용자의 읽은 시간을 조회하면 ValueError가 발생한다
    with pytest.raises(ValueError):
        room.get_last_read_at("userC")


def test_leave_room_by_user1_updates_status_to_left_by_user1():
    """user1이 채팅방을 나가면 상태가 left_by_user1로 변경된다"""
    # Given: 활성화된 채팅방
    room = ChatRoom(id="room-123", user1_id="userA", user2_id="userB")

    # When: user1이 채팅방을 나가면
    room.leave_room("userA")

    # Then: 상태가 left_by_user1로 변경된다
    assert room.status == "left_by_user1"


def test_leave_room_by_user2_updates_status_to_left_by_user2():
    """user2가 채팅방을 나가면 상태가 left_by_user2로 변경된다"""
    # Given: 활성화된 채팅방
    room = ChatRoom(id="room-123", user1_id="userA", user2_id="userB")

    # When: user2가 채팅방을 나가면
    room.leave_room("userB")

    # Then: 상태가 left_by_user2로 변경된다
    assert room.status == "left_by_user2"


def test_leave_room_by_both_users_updates_status_to_closed():
    """양쪽 사용자가 모두 나가면 상태가 closed로 변경된다"""
    # Given: user1이 나간 채팅방
    room = ChatRoom(id="room-123", user1_id="userA", user2_id="userB")
    room.leave_room("userA")

    # When: user2도 채팅방을 나가면
    room.leave_room("userB")

    # Then: 상태가 closed로 변경된다
    assert room.status == "closed"


def test_leave_room_by_invalid_user_raises_error():
    """참여자가 아닌 사용자가 나가기를 시도하면 에러가 발생한다"""
    # Given: 채팅방
    room = ChatRoom(id="room-123", user1_id="userA", user2_id="userB")

    # When & Then: 참여자가 아닌 사용자가 나가기를 시도하면 ValueError가 발생한다
    with pytest.raises(ValueError):
        room.leave_room("userC")


def test_new_chat_room_has_active_status():
    """새로 생성된 채팅방은 active 상태를 가진다"""
    # Given & When: 새 채팅방을 생성하면
    room = ChatRoom(id="room-123", user1_id="userA", user2_id="userB")

    # Then: 상태가 active이다
    assert room.status == "active"