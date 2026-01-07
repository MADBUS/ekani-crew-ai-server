from app.mbti_test.application.port.output.mbti_test_session_repository import MBTITestSessionRepositoryPort


class DeleteInProgressTestUseCase:
    def __init__(self, repository: MBTITestSessionRepositoryPort):
        self.repository = repository

    def execute(self, user_id: str):
        session = self.repository.find_by_user_id_and_status(user_id, "IN_PROGRESS")
        if session:
            self.repository.delete(session)
