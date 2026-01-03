import json
from sqlalchemy.orm import Session

from app.chat.application.port.report_repository_port import ReportRepositoryPort
from app.chat.domain.report import Report, ReportReason
from app.chat.infrastructure.model.report_model import ReportModel


class MySQLReportRepository(ReportRepositoryPort):
    """MySQL 기반 신고 저장소"""

    def __init__(self, db_session: Session):
        self._db = db_session

    def save(self, report: Report) -> None:
        """신고를 저장한다"""
        # reasons를 JSON 문자열로 변환
        reasons_json = json.dumps([reason.value for reason in report.reasons])

        report_model = ReportModel(
            id=report.id,
            reporter_id=report.reporter_id,
            reported_user_id=report.reported_user_id,
            room_id=report.room_id,
            message_id=report.message_id,
            reasons=reasons_json,
            created_at=report.created_at
        )
        self._db.merge(report_model)
        self._db.commit()

    def find_by_id(self, report_id: str) -> Report | None:
        """id로 신고를 조회한다"""
        report_model = self._db.query(ReportModel).filter(
            ReportModel.id == report_id
        ).first()

        if report_model is None:
            return None

        return self._to_domain(report_model)

    def find_by_reporter_id(self, reporter_id: str) -> list[Report]:
        """신고자 id로 신고 목록을 조회한다"""
        report_models = self._db.query(ReportModel).filter(
            ReportModel.reporter_id == reporter_id
        ).all()

        return [self._to_domain(model) for model in report_models]

    def find_by_message_and_reporter(self, message_id: str, reporter_id: str) -> Report | None:
        """특정 메시지에 대한 신고자의 신고를 조회한다"""
        report_model = self._db.query(ReportModel).filter(
            ReportModel.message_id == message_id,
            ReportModel.reporter_id == reporter_id
        ).first()

        if report_model is None:
            return None

        return self._to_domain(report_model)

    def get_reported_user_ids(self, reporter_id: str) -> list[str]:
        """신고자가 신고한 유저 id 목록을 조회한다"""
        # DISTINCT를 사용하여 중복 제거
        reported_user_ids = self._db.query(ReportModel.reported_user_id).filter(
            ReportModel.reporter_id == reporter_id
        ).distinct().all()

        return [user_id[0] for user_id in reported_user_ids]

    def _to_domain(self, model: ReportModel) -> Report:
        """ORM 모델을 도메인 엔티티로 변환한다"""
        # JSON 문자열을 reasons 리스트로 변환
        reasons_list = json.loads(model.reasons)
        reasons = [ReportReason(reason) for reason in reasons_list]

        return Report(
            id=model.id,
            reporter_id=model.reporter_id,
            reported_user_id=model.reported_user_id,
            room_id=model.room_id,
            message_id=model.message_id,
            reasons=reasons,
            created_at=model.created_at
        )
