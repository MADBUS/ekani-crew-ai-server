import pytest
from datetime import datetime
from app.chat.domain.report import Report, ReportReason


def test_report_creates_with_required_fields():
    """필수 필드로 Report 객체를 생성할 수 있다"""
    # Given: 신고에 필요한 정보
    report_id = "report-123"
    reporter_id = "userA"
    reported_user_id = "userB"
    room_id = "room-123"
    message_id = "message-456"
    reasons = [ReportReason.ABUSE, ReportReason.SPAM]
    created_at = datetime.now()

    # When: Report 객체를 생성하면
    report = Report(
        id=report_id,
        reporter_id=reporter_id,
        reported_user_id=reported_user_id,
        room_id=room_id,
        message_id=message_id,
        reasons=reasons,
        created_at=created_at
    )

    # Then: 정상적으로 생성되고 값을 조회할 수 있다
    assert report.id == report_id
    assert report.reporter_id == reporter_id
    assert report.reported_user_id == reported_user_id
    assert report.room_id == room_id
    assert report.message_id == message_id
    assert report.reasons == reasons
    assert report.created_at == created_at


def test_report_rejects_empty_id():
    """빈 id를 거부한다"""
    # Given: 빈 report_id
    report_id = ""

    # When & Then: Report 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="Report id는 비어있을 수 없습니다"):
        Report(
            id=report_id,
            reporter_id="userA",
            reported_user_id="userB",
            room_id="room-123",
            message_id="message-456",
            reasons=[ReportReason.ABUSE]
        )


def test_report_rejects_empty_reporter_id():
    """빈 reporter_id를 거부한다"""
    # Given: 빈 reporter_id
    reporter_id = ""

    # When & Then: Report 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="Reporter id는 비어있을 수 없습니다"):
        Report(
            id="report-123",
            reporter_id=reporter_id,
            reported_user_id="userB",
            room_id="room-123",
            message_id="message-456",
            reasons=[ReportReason.ABUSE]
        )


def test_report_rejects_empty_reported_user_id():
    """빈 reported_user_id를 거부한다"""
    # Given: 빈 reported_user_id
    reported_user_id = ""

    # When & Then: Report 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="Reported user id는 비어있을 수 없습니다"):
        Report(
            id="report-123",
            reporter_id="userA",
            reported_user_id=reported_user_id,
            room_id="room-123",
            message_id="message-456",
            reasons=[ReportReason.ABUSE]
        )


def test_report_rejects_empty_room_id():
    """빈 room_id를 거부한다"""
    # Given: 빈 room_id
    room_id = ""

    # When & Then: Report 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="Room id는 비어있을 수 없습니다"):
        Report(
            id="report-123",
            reporter_id="userA",
            reported_user_id="userB",
            room_id=room_id,
            message_id="message-456",
            reasons=[ReportReason.ABUSE]
        )


def test_report_rejects_empty_message_id():
    """빈 message_id를 거부한다"""
    # Given: 빈 message_id
    message_id = ""

    # When & Then: Report 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="Message id는 비어있을 수 없습니다"):
        Report(
            id="report-123",
            reporter_id="userA",
            reported_user_id="userB",
            room_id="room-123",
            message_id=message_id,
            reasons=[ReportReason.ABUSE]
        )


def test_report_rejects_empty_reasons():
    """빈 reasons 리스트를 거부한다"""
    # Given: 빈 reasons 리스트
    reasons = []

    # When & Then: Report 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="최소 하나의 신고 사유를 선택해야 합니다"):
        Report(
            id="report-123",
            reporter_id="userA",
            reported_user_id="userB",
            room_id="room-123",
            message_id="message-456",
            reasons=reasons
        )


def test_report_rejects_self_report():
    """자기 자신을 신고하는 것을 거부한다"""
    # Given: reporter_id와 reported_user_id가 동일
    user_id = "userA"

    # When & Then: Report 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="자기 자신을 신고할 수 없습니다"):
        Report(
            id="report-123",
            reporter_id=user_id,
            reported_user_id=user_id,
            room_id="room-123",
            message_id="message-456",
            reasons=[ReportReason.ABUSE]
        )


def test_report_auto_generates_created_at_if_not_provided():
    """created_at이 제공되지 않으면 자동으로 생성한다"""
    # Given: created_at 없이 신고 정보
    report_id = "report-123"

    # When: created_at 없이 Report를 생성하면
    report = Report(
        id=report_id,
        reporter_id="userA",
        reported_user_id="userB",
        room_id="room-123",
        message_id="message-456",
        reasons=[ReportReason.HARASSMENT]
    )

    # Then: created_at이 자동으로 설정된다
    assert isinstance(report.created_at, datetime)


def test_report_accepts_multiple_reasons():
    """여러 개의 신고 사유를 받을 수 있다"""
    # Given: 여러 신고 사유
    reasons = [ReportReason.ABUSE, ReportReason.SPAM, ReportReason.HARASSMENT]

    # When: 여러 사유로 Report를 생성하면
    report = Report(
        id="report-123",
        reporter_id="userA",
        reported_user_id="userB",
        room_id="room-123",
        message_id="message-456",
        reasons=reasons
    )

    # Then: 모든 사유가 저장된다
    assert len(report.reasons) == 3
    assert ReportReason.ABUSE in report.reasons
    assert ReportReason.SPAM in report.reasons
    assert ReportReason.HARASSMENT in report.reasons


def test_report_reason_enum_has_all_types():
    """ReportReason enum이 모든 신고 사유 타입을 가진다"""
    # Then: 모든 신고 사유가 정의되어 있다
    assert ReportReason.ABUSE == "ABUSE"
    assert ReportReason.HARASSMENT == "HARASSMENT"
    assert ReportReason.SPAM == "SPAM"
    assert ReportReason.OTHER == "OTHER"
