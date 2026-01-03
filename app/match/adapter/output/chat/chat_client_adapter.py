import logging
from datetime import datetime
from typing import Dict, Any

from config.database import get_db_session
from app.match.application.port.output.chat_room_port import ChatRoomPort

from app.chat.application.use_case.create_chat_room_use_case import CreateChatRoomUseCase
from app.chat.infrastructure.repository.mysql_chat_room_repository import MySQLChatRoomRepository

logger = logging.getLogger("match_adapter")


class ChatClientAdapter(ChatRoomPort):
    """
    Match 도메인의 요청을 Chat 도메인의 유스케이스 호출로 변환하는 어댑터
    """

    async def create_chat_room(self, match_payload: Dict[str, Any]) -> bool:
        db = None
        try:
            # 1. 데이터 파싱 (Match 규격 -> Chat 규격 변환)
            room_id = match_payload["roomId"]
            users = match_payload["users"]

            # users 리스트를 user1, user2로 분해
            if len(users) < 2:
                raise ValueError("채팅방 생성에는 최소 2명의 유저가 필요합니다.")

            user1_id = users[0]["userId"]
            user2_id = users[1]["userId"]

            # 문자열 Timestamp를 datetime 객체로 변환
            timestamp_str = match_payload["timestamp"]
            timestamp = datetime.fromisoformat(timestamp_str)

            # 2. Chat 도메인 컴포넌트 준비
            # DB 세션 생성 (Modular Monolith 구조이므로 직접 DB 접근)
            db = get_db_session()
            chat_repo = MySQLChatRoomRepository(db)
            chat_usecase = CreateChatRoomUseCase(chat_repo)

            # 3. Chat 유스케이스 실행
            logger.info(f"[Chat Integration] Creating room {room_id} for {user1_id}, {user2_id}")

            chat_usecase.execute(
                room_id=room_id,
                user1_id=user1_id,
                user2_id=user2_id,
                timestamp=timestamp
            )

            logger.info(f"[Chat Integration] Successfully created room: {room_id}")
            return True

        except ValueError as ve:
            logger.error(f"[Chat Integration] Validation Error: {ve}")
            return False
        except Exception as e:
            logger.error(f"[Chat Integration] Failed to create chat room: {e}")
            # 필요 시 여기서 재시도 로직을 추가하거나, 에러를 상위로 전파할 수 있음
            return False
        finally:
            # 4. DB 세션 정리
            if db:
                db.close()
    async def are_users_partners(self, user1_id: str, user2_id: str) -> bool:
        db = None
        try:
            db = get_db_session()
            chat_repo = MySQLChatRoomRepository(db)
            existing_room = chat_repo.find_by_users(user1_id, user2_id)
            return existing_room is not None
        except Exception as e:
            logger.error(f"[Chat Integration] Failed to check partnership for {user1_id}, {user2_id}: {e}")
            # 에러 발생 시 안전하게 처리 (매칭을 막지 않도록 False 반환)
            return False
        finally:
            if db:
                db.close()