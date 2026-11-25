import 'package:flutter_test/flutter_test.dart';
import '../lib/modules/tasks/create_task_use_case.dart';

void main() {
  test('CreateTaskUseCase creates task with trimmed title', () {
    final useCase = CreateTaskUseCase();
    final task = useCase.execute('  Write docs  ');
    expect(task.title, 'Write docs');
    expect(task.completed, false);
  });
}
