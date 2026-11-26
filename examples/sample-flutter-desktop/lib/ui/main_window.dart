import 'package:flutter/material.dart';
import '../modules/tasks/create_task_use_case.dart';

class MainWindow extends StatelessWidget {
  final CreateTaskUseCase useCase;

  const MainWindow({super.key, required this.useCase});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Sample Flutter Desktop')),
      body: const Center(child: Text('Ready')),
    );
  }
}
