from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.mbti_test.domain.surprise_answer import SurpriseAnswer


class SurpriseAnswerRepository(ABC):
    @abstractmethod
    def save(self, answer: SurpriseAnswer) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_user(self, user_id: UUID) -> List[SurpriseAnswer]:
        raise NotImplementedError
