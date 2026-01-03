import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from config.connection_manager import manager
from app.chat.application.use_case.save_chat_message_use_case import SaveChatMessageUseCase
from app.chat.infrastructure.repository.mysql_chat_message_repository import MySQLChatMessageRepository
from app.chat.infrastructure.repository.mysql_chat_room_repository import MySQLChatRoomRepository
from app.match.adapter.output.persistence.redis_match_state_adapter import RedisMatchStateAdapter
from config.database import get_db
from config.redis import get_redis

chat_websocket_router = APIRouter()


async def _clear_user_state(user_id: str):
    """Clear user's match state when they disconnect from chat"""
    if user_id:
        redis_client = get_redis()
        match_state = RedisMatchStateAdapter(redis_client)
        await match_state.clear_state(user_id)
        print(f"[WebSocket] Cleared match state for user {user_id}")


async def _set_user_chatting(user_id: str, room_id: str):
    """Set user's state to chatting when they connect"""
    if user_id:
        redis_client = get_redis()
        match_state = RedisMatchStateAdapter(redis_client)
        await match_state.set_chatting(user_id, room_id)
        print(f"[WebSocket] Set chatting state for user {user_id} in room {room_id}")


@chat_websocket_router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, db: Session = Depends(get_db)):
    await manager.connect(websocket, room_id)

    room_repository = MySQLChatRoomRepository(db)
    chat_room = room_repository.find_by_id(room_id)
    if not chat_room:
        await websocket.send_json({"error": "채팅방을 찾을 수 없습니다"})
        await websocket.close()
        return
    
    user1_id = chat_room.user1_id
    user2_id = chat_room.user2_id

    connected_user_id = None

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            sender_id = message_data.get("sender_id")
            content = message_data.get("content")

            if not sender_id or not content:
                await websocket.send_json({"error": "sender_id and content are required"})
                continue

            if sender_id not in [user1_id, user2_id]:
                await websocket.send_json({"error": "이 채팅방의 참여자가 아닙니다"})
                continue

            if connected_user_id is None:
                connected_user_id = sender_id
                manager.register_user(sender_id, room_id, websocket)
                await _set_user_chatting(sender_id, room_id)

            message_id = str(uuid.uuid4())

            message_repository = MySQLChatMessageRepository(db)
            save_message_use_case = SaveChatMessageUseCase(message_repository)
            save_message_use_case.execute(
                message_id=message_id,
                room_id=room_id,
                sender_id=sender_id,
                content=content
            )

            broadcast_message = {
                "message_id": message_id,
                "room_id": room_id,
                "sender_id": sender_id,
                "content": content
            }
            
            await manager.broadcast(json.dumps(broadcast_message), room_id)

    except WebSocketDisconnect:
        disconnected_user_id = manager.disconnect(websocket, room_id)
        if disconnected_user_id:
            await _clear_user_state(disconnected_user_id)