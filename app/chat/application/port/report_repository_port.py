from abc import ABC, abstractmethod
from app.chat.domain.report import Report


class ReportRepositoryPort(ABC):
    """신고 저장소 포트 (인터페이스)"""

    @abstractmethod
    def save(self, report: Report) -> None:
        """신고를 저장한다"""
        pass

    @abstractmethod
    def find_by_id(self, report_id: str) -> Report | None:
        """id로 신고를 조회한다"""
        pass

    @abstractmethod
    def find_by_reporter_id(self, reporter_id: str) -> list[Report]:
        """신고자 id로 신고 목록을 조회한다"""
        pass

    @abstractmethod
    def find_by_message_and_reporter(self, message_id: str, reporter_id: str) -> Report | None:
        """특정 메시지에 대한 신고자의 신고를 조회한다 (중복 신고 체크용)"""
        pass

    @abstractmethod
    def get_reported_user_ids(self, reporter_id: str) -> list[str]:
        """신고자가 신고한 유저 id 목록을 조회한다"""
        pass
