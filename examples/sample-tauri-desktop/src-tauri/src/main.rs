#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct TaskDto {
    pub id: i64,
    pub title: String,
    pub completed: bool,
}

#[tauri::command]
fn create_task(title: String) -> Result<TaskDto, String> {
    let trimmed = title.trim();
    if trimmed.is_empty() {
        return Err("Task title cannot be empty".to_string());
    }
    Ok(TaskDto {
        id: 1,
        title: trimmed.to_string(),
        completed: false,
    })
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![create_task])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
