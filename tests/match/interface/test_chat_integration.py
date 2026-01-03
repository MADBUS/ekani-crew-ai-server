import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from app.shared.vo.mbti import MBTI
from app.match.domain.match_ticket import MatchTicket
from app.match.application.usecase.match_usecase import MatchUseCase
from tests.match.fixtures.fake_match_queue_adapter import FakeMatchQueueAdapter

@pytest.mark.asyncio

async def test_format_match_result_payload(monkeypatch):

    """
    [MATCH-3] 매칭 성공 시, Chat 도메인으로 보내는 데이터 규격(JSON)이
    Success Criteria에 맞게 생성되는지 검증
    """
    # Given
    mock_chat_port = AsyncMock()
    mock_chat_port.create_chat_room.return_value = True
    mock_chat_port.are_users_partners.return_value = False  # 항상 새로운 파트너라고 가정

    # MatchUseCase의 의존성을 모킹합니다.
    mock_queue_port = AsyncMock()
    mock_state_port = AsyncMock()
    mock_state_port.is_available_for_match.return_value = True
    mock_notification_port = AsyncMock()

    # MatchService를 모킹합니다.
    mock_match_service = MagicMock()
    mock_match_service.find_partner = AsyncMock()
    monkeypatch.setattr(
        "app.match.application.usecase.match_usecase.MatchService",
        lambda *args, **kwargs: mock_match_service
    )

    usecase = MatchUseCase(
        match_queue_port=mock_queue_port,
        chat_room_port=mock_chat_port,
        match_state_port=mock_state_port,
        match_notification_port=mock_notification_port,
    )

    usecase.match_service = mock_match_service

    # find_partner가 즉시 유효한 파트너를 반환하도록 설정
    partner = MatchTicket("partner_enfj", MBTI("ENFJ"))
    usecase.match_service.find_partner.return_value = partner

    # When: 매칭 요청
    my_id = "me_infp"
    my_mbti = MBTI("INFP")
    result = await usecase.request_match(my_id, my_mbti, level=1)

    # Then 1: UseCase 응답에 roomId가 포함되어야 함
    assert result["status"] == "matched"
    assert "roomId" in result
    assert len(result["roomId"]) > 0

    # Then 2: ChatPort가 호출되었는지 확인
    mock_chat_port.create_chat_room.assert_called_once()

    # Then 3: 전달된 Payload 데이터 규격 검증 (핵심)
    # call_args[0][0]은 첫 번째 호출의 첫 번째 인자(match_payload)입니다.
    payload = mock_chat_port.create_chat_room.call_args[0][0]

    print(f"\n[Captured Payload]: {payload}")

    # 3-1. roomId는 UUID v4 형식이어야 함
    try:
        uuid_obj = uuid.UUID(payload["roomId"], version=4)
    except ValueError:
        pytest.fail("roomId is not a valid UUID v4")

    # 3-2. users 리스트 검증
    assert len(payload["users"]) == 2
    users = payload["users"]

    # 순서는 보장되지 않을 수 있으므로 ID 집합으로 확인
    user_ids = {u["userId"] for u in users}
    assert my_id in user_ids
    assert "partner_enfj" in user_ids

    # MBTI 정보 포함 확인
    assert any(u["mbti"] == "INFP" for u in users)
    assert any(u["mbti"] == "ENFJ" for u in users)

    # 3-3. Timestamp 존재 확인
    assert "timestamp" in payload