from app.chat.application.port.report_repository_port import ReportRepositoryPort
from app.chat.domain.report import Report


class FakeReportRepository(ReportRepositoryPort):
    """테스트용 Fake Report 저장소"""

    def __init__(self):
        self._reports: dict[str, Report] = {}

    def save(self, report: Report) -> None:
        """신고를 저장한다"""
        self._reports[report.id] = report

    def find_by_id(self, report_id: str) -> Report | None:
        """id로 신고를 조회한다"""
        return self._reports.get(report_id)

    def find_by_reporter_id(self, reporter_id: str) -> list[Report]:
        """신고자 id로 신고 목록을 조회한다"""
        return [
            report for report in self._reports.values()
            if report.reporter_id == reporter_id
        ]

    def find_by_message_and_reporter(self, message_id: str, reporter_id: str) -> Report | None:
        """특정 메시지에 대한 신고자의 신고를 조회한다"""
        for report in self._reports.values():
            if report.message_id == message_id and report.reporter_id == reporter_id:
                return report
        return None

    def get_reported_user_ids(self, reporter_id: str) -> list[str]:
        """신고자가 신고한 유저 id 목록을 조회한다"""
        reports = self.find_by_reporter_id(reporter_id)
        # 중복 제거
        return list(set([report.reported_user_id for report in reports]))
