import pytest

from modules.tasks import TasksFacade


def test_create_task_success() -> None:
    facade = TasksFacade()
    created = facade.create_task("  Prepare release notes  ")
    assert created.task_id == "task-001"
    assert created.title == "Prepare release notes"
    assert created.completed is False
    assert len(facade.list_tasks()) == 1


def test_create_task_rejects_empty_title() -> None:
    facade = TasksFacade()
    with pytest.raises(ValueError, match="BR-01"):
        facade.create_task("   ")


def test_create_task_rejects_overlong_title() -> None:
    facade = TasksFacade()
    with pytest.raises(ValueError, match="BR-01"):
        facade.create_task("x" * 121)
