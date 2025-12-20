from abc import ABC, abstractmethod

from app.mbti.domain.mbti_message import MBTIMessage


class QuestionProviderPort(ABC):
    @abstractmethod
    def get_initial_question(self) -> MBTIMessage:
        pass
