from .create_task_use_case import (
    CreateTaskRequest,
    CreateTaskResult,
    CreateTaskUseCase,
    InMemoryTaskRepository,
)


class TasksFacade:
    """Public module facade for tasks."""

    def __init__(self) -> None:
        self._repository = InMemoryTaskRepository()
        self._create_task = CreateTaskUseCase(self._repository)

    def create_task(self, title: str) -> CreateTaskResult:
        return self._create_task.execute(CreateTaskRequest(title=title))

    def list_tasks(self) -> list[CreateTaskResult]:
        return self._repository.list_all()
