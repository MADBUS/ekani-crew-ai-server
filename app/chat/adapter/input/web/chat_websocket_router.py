import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .connection_manager import manager
from app.chat.application.use_case.save_chat_message_use_case import SaveChatMessageUseCase
from app.chat.infrastructure.repository.mysql_chat_message_repository import MySQLChatMessageRepository
from app.chat.infrastructure.repository.mysql_chat_room_repository import MySQLChatRoomRepository
from config.database import get_db_session

chat_websocket_router = APIRouter()


@chat_websocket_router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)

    # 채팅방 존재 여부 확인 (세션 열고 바로 닫음)
    db_session = get_db_session()
    try:
        room_repository = MySQLChatRoomRepository(db_session)
        chat_room = room_repository.find_by_id(room_id)
        if not chat_room:
            await websocket.send_json({"error": "채팅방을 찾을 수 없습니다"})
            await websocket.close()
            return
        # 채팅방 참여자 정보 저장 (세션 닫기 전에)
        user1_id = chat_room.user1_id
        user2_id = chat_room.user2_id
    finally:
        db_session.close()

    try:
        while True:
            # JSON 형식으로 메시지 수신
            data = await websocket.receive_text()
            message_data = json.loads(data)

            sender_id = message_data.get("sender_id")
            content = message_data.get("content")

            if not sender_id or not content:
                await websocket.send_json({"error": "sender_id and content are required"})
                continue

            # sender_id가 채팅방 참여자인지 확인
            if sender_id not in [user1_id, user2_id]:
                await websocket.send_json({"error": "이 채팅방의 참여자가 아닙니다"})
                continue

            # 메시지 ID 생성
            message_id = str(uuid.uuid4())

            # DB에 메시지 저장 (메시지마다 세션 열고 닫음)
            db_session = get_db_session()
            try:
                message_repository = MySQLChatMessageRepository(db_session)
                save_message_use_case = SaveChatMessageUseCase(message_repository)
                save_message_use_case.execute(
                    message_id=message_id,
                    room_id=room_id,
                    sender_id=sender_id,
                    content=content
                )
            finally:
                db_session.close()

            # 브로드캐스트용 메시지 생성
            broadcast_message = {
                "message_id": message_id,
                "room_id": room_id,
                "sender_id": sender_id,
                "content": content
            }

            # 채팅방의 모든 클라이언트에게 브로드캐스트
            await manager.broadcast(json.dumps(broadcast_message), room_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)

