import pytest
from datetime import datetime

from app.chat.application.use_case.report_user_use_case import ReportUserUseCase
from app.chat.domain.report import ReportReason
from app.chat.domain.chat_room import ChatRoom
from app.chat.domain.chat_message import ChatMessage
from tests.chat.fixtures.fake_report_repository import FakeReportRepository
from tests.chat.fixtures.fake_chat_room_repository import FakeChatRoomRepository
from tests.chat.fixtures.fake_chat_message_repository import FakeChatMessageRepository


@pytest.fixture
def report_repository():
    """테스트용 Fake Report 저장소"""
    return FakeReportRepository()


@pytest.fixture
def chat_room_repository():
    """테스트용 Fake ChatRoom 저장소"""
    return FakeChatRoomRepository()


@pytest.fixture
def chat_message_repository():
    """테스트용 Fake ChatMessage 저장소"""
    return FakeChatMessageRepository()


@pytest.fixture
def use_case(report_repository, chat_room_repository, chat_message_repository):
    """ReportUserUseCase"""
    return ReportUserUseCase(report_repository, chat_room_repository, chat_message_repository)


def test_report_message_successfully(use_case, report_repository, chat_room_repository, chat_message_repository):
    """메시지를 성공적으로 신고한다"""
    # Given: 채팅방에 두 사용자가 참여 중이고 메시지가 있음
    room = ChatRoom(
        id="room-123",
        user1_id="userA",
        user2_id="userB",
        created_at=datetime.now()
    )
    chat_room_repository.save(room)

    message = ChatMessage(
        id="message-456",
        room_id="room-123",
        sender_id="userB",
        content="불쾌한 메시지",
        created_at=datetime.now()
    )
    chat_message_repository.save(message)

    # When: userA가 userB의 메시지를 신고하면
    report_id = use_case.execute(
        reporter_id="userA",
        message_id="message-456",
        reasons=[ReportReason.ABUSE, ReportReason.SPAM]
    )

    # Then: 신고가 저장된다
    assert report_id is not None
    saved_report = report_repository.find_by_id(report_id)
    assert saved_report is not None
    assert saved_report.reporter_id == "userA"
    assert saved_report.reported_user_id == "userB"
    assert saved_report.room_id == "room-123"
    assert saved_report.message_id == "message-456"
    assert ReportReason.ABUSE in saved_report.reasons
    assert ReportReason.SPAM in saved_report.reasons


def test_report_message_rejects_duplicate_report(use_case, report_repository, chat_room_repository, chat_message_repository):
    """동일한 메시지를 중복 신고하는 것을 거부한다"""
    # Given: 채팅방, 메시지, 그리고 이미 신고한 이력
    room = ChatRoom(
        id="room-123",
        user1_id="userA",
        user2_id="userB",
        created_at=datetime.now()
    )
    chat_room_repository.save(room)

    message = ChatMessage(
        id="message-456",
        room_id="room-123",
        sender_id="userB",
        content="불쾌한 메시지",
        created_at=datetime.now()
    )
    chat_message_repository.save(message)

    # 첫 번째 신고
    use_case.execute(
        reporter_id="userA",
        message_id="message-456",
        reasons=[ReportReason.ABUSE]
    )

    # When & Then: 같은 메시지를 다시 신고하려고 하면 ValueError가 발생한다
    with pytest.raises(ValueError, match="이미 신고한 메시지입니다"):
        use_case.execute(
            reporter_id="userA",
            message_id="message-456",
            reasons=[ReportReason.SPAM]
        )


def test_report_message_rejects_self_report(use_case, chat_room_repository, chat_message_repository):
    """자기 메시지를 신고하는 것을 거부한다"""
    # Given: 채팅방과 자신의 메시지
    room = ChatRoom(
        id="room-123",
        user1_id="userA",
        user2_id="userB",
        created_at=datetime.now()
    )
    chat_room_repository.save(room)

    message = ChatMessage(
        id="message-456",
        room_id="room-123",
        sender_id="userA",
        content="내 메시지",
        created_at=datetime.now()
    )
    chat_message_repository.save(message)

    # When & Then: 자기 메시지를 신고하려고 하면 ValueError가 발생한다
    with pytest.raises(ValueError, match="자기 자신을 신고할 수 없습니다"):
        use_case.execute(
            reporter_id="userA",
            message_id="message-456",
            reasons=[ReportReason.ABUSE]
        )


def test_report_message_rejects_non_participant_reporter(use_case, chat_room_repository, chat_message_repository):
    """채팅방 참여자가 아닌 사용자의 신고를 거부한다"""
    # Given: userA와 userB만 참여 중인 채팅방
    room = ChatRoom(
        id="room-123",
        user1_id="userA",
        user2_id="userB",
        created_at=datetime.now()
    )
    chat_room_repository.save(room)

    message = ChatMessage(
        id="message-456",
        room_id="room-123",
        sender_id="userB",
        content="메시지",
        created_at=datetime.now()
    )
    chat_message_repository.save(message)

    # When & Then: 참여자가 아닌 userC가 신고하려고 하면 ValueError가 발생한다
    with pytest.raises(ValueError, match="채팅방 참여자만 신고할 수 있습니다"):
        use_case.execute(
            reporter_id="userC",
            message_id="message-456",
            reasons=[ReportReason.SPAM]
        )


def test_report_message_rejects_nonexistent_message(use_case, chat_room_repository):
    """존재하지 않는 메시지에 대한 신고를 거부한다"""
    # Given: 존재하지 않는 메시지 ID
    message_id = "nonexistent-message"

    # When & Then: 존재하지 않는 메시지를 신고하려고 하면 ValueError가 발생한다
    with pytest.raises(ValueError, match="메시지를 찾을 수 없습니다"):
        use_case.execute(
            reporter_id="userA",
            message_id=message_id,
            reasons=[ReportReason.OTHER]
        )
