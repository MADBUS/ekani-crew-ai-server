import json
import redis.asyncio as aioredis
from typing import Optional

from app.match.application.port.output.match_state_port import (
    MatchStatePort,
    MatchState,
    UserMatchState
)


class RedisMatchStateAdapter(MatchStatePort):
    """
    Redis adapter for tracking user match states.
    Uses Redis Hash for storing state data with optional TTL for matched state.
    """

    def __init__(self, client: aioredis.Redis):
        self.redis = client
        self.key_prefix = "match:state:"

    def _get_key(self, user_id: str) -> str:
        return f"{self.key_prefix}{user_id}"

    def _serialize(self, state: UserMatchState) -> str:
        return json.dumps({
            "user_id": state.user_id,
            "state": state.state.value,
            "mbti": state.mbti,
            "room_id": state.room_id,
            "partner_id": state.partner_id
        })

    def _deserialize(self, data: str) -> UserMatchState:
        raw = json.loads(data)
        return UserMatchState(
            user_id=raw["user_id"],
            state=MatchState(raw["state"]),
            mbti=raw.get("mbti"),
            room_id=raw.get("room_id"),
            partner_id=raw.get("partner_id")
        )

    async def get_state(self, user_id: str) -> Optional[UserMatchState]:
        """Get user's current match state"""
        key = self._get_key(user_id)
        data = await self.redis.get(key)

        if not data:
            return None

        return self._deserialize(data)

    async def set_queued(self, user_id: str, mbti: str) -> None:
        """
        Mark user as queued for matching, unless they are already in a CHATTING state.
        A user can be in a queue while chatting.
        """
        current_state = await self.get_state(user_id)
        if current_state and current_state.state == MatchState.CHATTING:
            print(f"[MatchState] User {user_id} is CHATTING, not downgrading state to QUEUED.")
            return

        key = self._get_key(user_id)
        state = UserMatchState(
            user_id=user_id,
            state=MatchState.QUEUED,
            mbti=mbti
        )
        # No expiration for queued state - user stays in queue until cancel
        await self.redis.set(key, self._serialize(state))
        print(f"[MatchState] User {user_id} state: QUEUED")

    async def set_matched(
        self,
        user_id: str,
        mbti: str,
        room_id: str,
        partner_id: str,
        expire_seconds: int = 60
    ) -> None:
        """
        Mark user as matched.
        State expires after expire_seconds if user doesn't connect to chat.
        After expiration, user can be matched again.
        """
        key = self._get_key(user_id)
        state = UserMatchState(
            user_id=user_id,
            state=MatchState.MATCHED,
            mbti=mbti,
            room_id=room_id,
            partner_id=partner_id
        )
        # Set with expiration - if user doesn't connect to chat, state expires
        await self.redis.set(key, self._serialize(state), ex=expire_seconds)
        print(f"[MatchState] User {user_id} state: MATCHED (room: {room_id}, expires in {expire_seconds}s)")

    async def set_chatting(self, user_id: str, room_id: str) -> None:
        """Mark user as connected to chat - no expiration"""
        # First get current state to preserve mbti and partner_id
        current_state = await self.get_state(user_id)

        key = self._get_key(user_id)
        state = UserMatchState(
            user_id=user_id,
            state=MatchState.CHATTING,
            mbti=current_state.mbti if current_state else None,
            room_id=room_id,
            partner_id=current_state.partner_id if current_state else None
        )
        # No expiration for chatting state - cleared on disconnect
        await self.redis.set(key, self._serialize(state))
        print(f"[MatchState] User {user_id} state: CHATTING (room: {room_id})")

    async def clear_state(self, user_id: str) -> None:
        """Clear user's match state (back to idle)"""
        key = self._get_key(user_id)
        await self.redis.delete(key)
        print(f"[MatchState] User {user_id} state: CLEARED (idle)")

    async def is_available_for_match(self, user_id: str) -> bool:
        """
        Check if user can be matched.
        User is available if:
        - No state exists (idle)
        - State is QUEUED (waiting in queue)
        - State is CHATTING (user can have multiple chat rooms)

        User is NOT available if:
        - State is MATCHED (already matched, waiting to connect to NEW chat room)
        """
        state = await self.get_state(user_id)

        if state is None:
            return True

        # Only MATCHED state blocks - user should connect to that chat first
        return state.state != MatchState.MATCHED
