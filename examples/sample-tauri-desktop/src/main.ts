import { invoke } from "@tauri-apps/api/core";

export interface TaskDto {
  id: number;
  title: string;
  completed: boolean;
}

export async function createTask(title: string): Promise<TaskDto> {
  return invoke<TaskDto>("create_task", { title });
}
