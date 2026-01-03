from abc import ABC, abstractmethod
from typing import Dict, Any


class ChatRoomPort(ABC):
    """
    Chat 도메인과 통신하기 위한 아웃바운드 포트
    """

    @abstractmethod
    async def create_chat_room(self, match_payload: Dict[str, Any]) -> bool:
        """
        매칭된 사용자들의 정보를 받아 채팅방 생성을 요청합니다.

        Args:
            match_payload: {
                "roomId": str (UUID),
                "users": List[{"userId": str, "mbti": str}],
                "timestamp": str (ISO8601)
            }
        """
        pass

    @abstractmethod
    async def are_users_partners(self, user1_id: str, user2_id: str) -> bool:
        """
        두 사용자가 이미 활성화된 채팅방에 함께 있는지 확인합니다.
        """
        pass