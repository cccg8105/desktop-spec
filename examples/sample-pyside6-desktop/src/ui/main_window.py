from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.tasks import TasksFacade


class MainWindow(QMainWindow):
    """Main desktop window for UF-TASKS-001 using QPalette/semantic roles."""

    def __init__(self, facade: TasksFacade | None = None) -> None:
        super().__init__()
        self._facade = facade or TasksFacade()
        self.setWindowTitle("Tasks Desktop Pilot")
        self.setMinimumSize(640, 420)

        central = QWidget(self)
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("New task title...")
        self.title_input.setAccessibleName("Task title")

        self.create_button = QPushButton("Create Task", self)
        self.create_button.setAccessibleName("Create task")
        self.create_button.clicked.connect(self._on_create_clicked)

        input_row.addWidget(self.title_input)
        input_row.addWidget(self.create_button)

        self.status_label = QLabel("Ready", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.task_list = QListWidget(self)
        self.task_list.setAccessibleName("Task list")

        root_layout.addLayout(input_row)
        root_layout.addWidget(self.status_label)
        root_layout.addWidget(self.task_list)

    def _on_create_clicked(self) -> None:
        try:
            task = self._facade.create_task(self.title_input.text())
        except ValueError as exc:
            self.status_label.setText(str(exc))
            return

        self.task_list.addItem(f"[{task.task_id}] {task.title}")
        self.title_input.clear()
        self.status_label.setText(f"Created {task.task_id}")
