from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CreateTaskRequest:
    title: str


@dataclass(frozen=True)
class CreateTaskResult:
    task_id: str
    title: str
    completed: bool = False


class TaskRepository(Protocol):
    def save(self, task: CreateTaskResult) -> None:
        ...

    def list_all(self) -> list[CreateTaskResult]:
        ...


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._items: list[CreateTaskResult] = []

    def save(self, task: CreateTaskResult) -> None:
        self._items.append(task)

    def list_all(self) -> list[CreateTaskResult]:
        return list(self._items)


class CreateTaskUseCase:
    """Use case UC-TASKS-001: Create a new desktop task."""

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, request: CreateTaskRequest) -> CreateTaskResult:
        normalized = request.title.strip()
        if not normalized:
            raise ValueError("Task title cannot be empty [BR-01]")
        if len(normalized) > 120:
            raise ValueError("Task title cannot exceed 120 characters [BR-01]")

        task_id = f"task-{len(self._repository.list_all()) + 1:03d}"
        task = CreateTaskResult(task_id=task_id, title=normalized, completed=False)
        self._repository.save(task)
        return task
