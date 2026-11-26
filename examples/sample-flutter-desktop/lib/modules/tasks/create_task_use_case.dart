class TaskEntity {
  final int id;
  final String title;
  final bool completed;

  const TaskEntity({
    required this.id,
    required this.title,
    this.completed = false,
  });
}

class CreateTaskUseCase {
  TaskEntity execute(String title) {
    final trimmed = title.trim();
    if (trimmed.isEmpty) {
      throw ArgumentError('Task title cannot be empty');
    }
    return TaskEntity(id: 1, title: trimmed);
  }
}
