import pytest
from unittest.mock import AsyncMock, MagicMock

from app.match.application.usecase.match_usecase import MatchUseCase, MatchTicket
from app.shared.vo.mbti import MBTI

# 이 파일의 모든 테스트를 asyncio 테스트로 표시합니다.
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_ports():
    """MatchUseCase에 대한 Mock 포트를 생성하는 Fixture."""
    return {
        "match_queue_port": AsyncMock(),
        "chat_room_port": AsyncMock(),
        "match_state_port": AsyncMock(),
        "match_notification_port": AsyncMock(),
    }


@pytest.fixture
def match_usecase(mock_ports, monkeypatch):
    """mock 포트와 mock 서비스를 사용하여 MatchUseCase 인스턴스를 생성하는 Fixture."""
    # MatchService는 UseCase 내부에서 생성되므로, 이를 모의 객체로 대체합니다.
    mock_match_service = MagicMock()
    mock_match_service.find_partner = AsyncMock()

    monkeypatch.setattr(
        "app.match.application.usecase.match_usecase.MatchService",
        lambda *args, **kwargs: mock_match_service
    )

    usecase = MatchUseCase(**mock_ports)
    # 테스트에서 match_service 모의 객체에 접근할 수 있도록 주입합니다.
    usecase.match_service = mock_match_service

    # 초기 상태 설정: 모든 유저는 기본적으로 이용 가능하며, 파트너가 아닌 것으로 설정
    mock_ports["match_state_port"].is_available_for_match.return_value = True
    mock_ports["chat_room_port"].are_users_partners.return_value = False
    mock_ports["match_queue_port"].is_user_in_queue.return_value = False
    mock_ports["match_state_port"].get_state.return_value = None

    return usecase


class TestRequestMatch:
    """request_match 유스케이스에 대한 테스트 스위트"""

    async def test_should_remove_and_requeue_when_user_is_already_waiting(self, match_usecase, mock_ports):
        """
        [#1] 사용자가 이미 대기열에 있을 때 다시 매칭을 요청하면, 기존 요청을 제거하고 다시 대기열에 등록해야 합니다.
        """
        # GIVEN: 사용자가 이미 대기열에 있습니다. 파트너는 찾지 못하는 상황을 가정합니다.
        user_id = "user_a"
        mbti = MBTI("INFP")
        mock_ports["match_queue_port"].is_user_in_queue.return_value = True
        match_usecase.match_service.find_partner.return_value = None

        # WHEN: 동일한 사용자가 다른 레벨로 다시 매칭을 요청합니다.
        result = await match_usecase.request_match(user_id=user_id, mbti=mbti, level=2)

        # THEN: 기존 대기열에서 사용자를 제거하고, 새로운 요청으로 다시 대기열에 등록해야 합니다.
        mock_ports["match_queue_port"].remove.assert_called_once_with(user_id, mbti)
        mock_ports["match_queue_port"].enqueue.assert_called_once()
        assert result["status"] == "waiting"

    async def test_should_skip_unavailable_partner_and_find_next(self, match_usecase, mock_ports):
        """
        [#2] 찾은 파트너가 이용 불가 상태일 때, 그를 건너뛰고 다음 후보자와 매칭되어야 합니다.
        """
        # GIVEN: 요청자 A, 이용 불가 파트너 B, 이용 가능 파트너 C
        user_a = "user_a"
        mbti_a = MBTI("INFP")
        unavailable_partner = MatchTicket(user_id="user_b", mbti=MBTI("ENFJ"))
        available_partner = MatchTicket(user_id="user_c", mbti=MBTI("ENTJ"))

        # find_partner는 B를 먼저, 그 다음에 C를 반환합니다.
        match_usecase.match_service.find_partner.side_effect = [unavailable_partner, available_partner]

        # is_available_for_match는 B에 대해 False, C에 대해 True를 반환합니다.
        mock_ports["match_state_port"].is_available_for_match.side_effect = [False, True]

        # WHEN: A가 매칭을 요청합니다.
        result = await match_usecase.request_match(user_id=user_a, mbti=mbti_a, level=1)

        # THEN: 최종 매칭은 이용 가능한 C와 이루어져야 합니다.
        assert result["status"] == "matched"
        assert result["partner"]["user_id"] == "user_c"

        # AND: 두 파트너 모두에 대해 상태 확인을 시도해야 합니다.
        assert mock_ports["match_state_port"].is_available_for_match.call_count == 2

        # AND: 파트너를 찾기 위해 두 번 시도해야 합니다.
        assert match_usecase.match_service.find_partner.call_count == 2

    async def test_should_skip_existing_partner_and_find_next(self, match_usecase, mock_ports):
        """
        [#3] 찾은 파트너가 이미 채팅 중인 상대일 때, 그를 건너뛰고 다음 후보자와 매칭되어야 합니다.
        """
        # GIVEN: 요청자 A, 이미 파트너인 B, 새로운 파트너 C
        user_a = "user_a"
        mbti_a = MBTI("INFP")
        existing_partner = MatchTicket(user_id="user_b", mbti=MBTI("ENFJ"))
        new_partner = MatchTicket(user_id="user_c", mbti=MBTI("ENTJ"))
        
        # find_partner는 B를 먼저, 그 다음에 C를 반환합니다.
        match_usecase.match_service.find_partner.side_effect = [existing_partner, new_partner]

        # are_users_partners는 B에 대해 True, C에 대해 False를 반환합니다.
        mock_ports["chat_room_port"].are_users_partners.side_effect = [True, False]

        # WHEN: A가 매칭을 요청합니다.
        result = await match_usecase.request_match(user_id=user_a, mbti=mbti_a, level=1)

        # THEN: 최종 매칭은 새로운 파트너인 C와 이루어져야 합니다.
        assert result["status"] == "matched"
        assert result["partner"]["user_id"] == "user_c"

        # AND: 두 파트너 모두에 대해 파트너 관계 확인을 시도해야 합니다.
        assert mock_ports["chat_room_port"].are_users_partners.call_count == 2
        mock_ports["chat_room_port"].are_users_partners.assert_any_call(user_a, existing_partner.user_id)
        mock_ports["chat_room_port"].are_users_partners.assert_any_call(user_a, new_partner.user_id)

        # AND: 파트너를 찾기 위해 두 번 시도해야 합니다.
        assert match_usecase.match_service.find_partner.call_count == 2