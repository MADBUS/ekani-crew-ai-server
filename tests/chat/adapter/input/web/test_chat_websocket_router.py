
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.user.infrastructure.model.user_model import UserModel
from app.chat.infrastructure.model.chat_message_model import ChatMessageModel
from app.chat.infrastructure.model.chat_room_model import ChatRoomModel

def _create_test_users(db_session, *user_ids):
    """Helper to create user models for tests."""
    for user_id in user_ids:
        user = db_session.query(UserModel).filter_by(id=user_id).first()
        if not user:
            db_session.add(UserModel(id=user_id, email=f"{user_id}@test.com"))
    db_session.commit()

def _create_test_room(db_session, room_id: str, user1_id: str, user2_id: str):
    """Helper to create a chat room with corresponding users."""
    _create_test_users(db_session, user1_id, user2_id)
    room = ChatRoomModel(
        id=room_id,
        user1_id=user1_id,
        user2_id=user2_id,
        created_at=datetime.now()
    )
    db_session.add(room)
    db_session.commit()

def test_websocket_connection_and_disconnection(client: TestClient, db_session):
    """WebSocket connection and disconnection test"""
    room_id = "test_room_connect"
    user1_id = "user1_conn"
    user2_id = "user2_conn"
    _create_test_room(db_session, room_id, user1_id, user2_id)

    try:
        with client.websocket_connect(f"/ws/chat/{room_id}") as websocket:
            assert websocket
    except WebSocketDisconnect as e:
        pytest.fail(f"WebSocket connection failed unexpectedly: {e}")

def test_send_and_receive_message(client: TestClient, db_session):
    """Message sending and receiving test"""
    room_id = "test_room_send"
    user1_id = "user1_send"
    user2_id = "user2_send"
    _create_test_room(db_session, room_id, user1_id, user2_id)

    with client.websocket_connect(f"/ws/chat/{room_id}") as websocket:
        message_payload = {
            "sender_id": user1_id,
            "content": "Hello, WebSocket!"
        }
        websocket.send_json(message_payload)
        received = websocket.receive_json()
        assert received["content"] == "Hello, WebSocket!"
        assert received["sender_id"] == user1_id

def test_message_saved_to_database(client: TestClient, db_session):
    """Verify that messages sent via WebSocket are saved to the DB."""
    room_id = "test_room_db"
    sender_id = "user123_db"
    user2_id = "user456_db"
    content = "Hello, this should be saved to DB!"
    _create_test_room(db_session, room_id, sender_id, user2_id)

    with client.websocket_connect(f"/ws/chat/{room_id}") as websocket:
        message_payload = {
            "sender_id": sender_id,
            "content": content
        }
        websocket.send_json(message_payload)
        # We need to receive the message for the send operation to complete
        websocket.receive_json()

    # The dependency override on the client ensures this query uses the same session
    saved_message = db_session.query(ChatMessageModel).filter_by(room_id=room_id, sender_id=sender_id, content=content).one_or_none()
    assert saved_message is not None
    assert saved_message.sender_id == sender_id
    assert saved_message.content == content
