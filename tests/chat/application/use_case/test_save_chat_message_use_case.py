import pytest

from app.chat.application.use_case.save_chat_message_use_case import SaveChatMessageUseCase
from tests.chat.fixtures.fake_chat_message_repository import FakeChatMessageRepository


@pytest.fixture
def repository():
    """테스트용 Fake ChatMessage 저장소"""
    return FakeChatMessageRepository()


@pytest.fixture
def use_case(repository):
    """SaveChatMessageUseCase"""
    return SaveChatMessageUseCase(repository)


def test_save_chat_message(use_case, repository):
    """채팅 메시지를 저장한다"""
    # Given: 메시지 정보
    message_id = "msg-uuid-123"
    room_id = "room-456"
    sender_id = "user-789"
    content = "안녕하세요!"

    # When: 메시지를 저장하면
    saved_message_id = use_case.execute(
        message_id=message_id,
        room_id=room_id,
        sender_id=sender_id,
        content=content
    )

    # Then: 메시지가 저장된다
    assert saved_message_id == message_id
    saved_message = repository.find_by_id(message_id)
    assert saved_message is not None
    assert saved_message.id == message_id
    assert saved_message.room_id == room_id
    assert saved_message.sender_id == sender_id
    assert saved_message.content == content


def test_save_chat_message_rejects_empty_content(use_case):
    """빈 content로 메시지 저장 시 에러가 발생한다"""
    # Given: 빈 content
    message_id = "msg-123"
    room_id = "room-456"
    sender_id = "user-789"
    content = ""

    # When & Then: 빈 content로 저장하려고 하면 에러가 발생한다
    with pytest.raises(ValueError):
        use_case.execute(
            message_id=message_id,
            room_id=room_id,
            sender_id=sender_id,
            content=content
        )