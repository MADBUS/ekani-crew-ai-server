from app.mbti_test.application.port.output.mbti_test_session_repository import MBTITestSessionRepositoryPort


class FindInProgressTestUseCase:
    def __init__(self, repository: MBTITestSessionRepositoryPort):
        self.repository = repository

    def execute(self, user_id: str):
        return self.repository.find_by_user_id_and_status(user_id, "IN_PROGRESS")
