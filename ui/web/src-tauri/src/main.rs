use serde::Serialize;
use std::net::TcpListener;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::{Manager, WebviewUrl, WebviewWindowBuilder, Window};

#[derive(Default)]
struct BackendState {
    child: Mutex<Option<BackendProcess>>,
}

struct BackendProcess {
    child: Child,
    port: u16,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct BackendInfo {
    api_base: String,
    ws_url: String,
}

fn project_root() -> Result<PathBuf, String> {
    if let Ok(value) = std::env::var("LUMIMATE_PROJECT_ROOT") {
        let path = PathBuf::from(value);
        if path.join("launcher.py").exists() {
            return Ok(path);
        }
    }

    if let Ok(exe) = std::env::current_exe() {
        for ancestor in exe.ancestors() {
            if ancestor.join("launcher.py").exists() {
                return Ok(ancestor.to_path_buf());
            }
        }
    }

    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let root = manifest_dir
        .parent()
        .and_then(Path::parent)
        .and_then(Path::parent)
        .map(Path::to_path_buf)
        .ok_or_else(|| "Unable to resolve LumiMate project root.".to_string())?;
    if root.join("launcher.py").exists() {
        Ok(root)
    } else {
        Err("Unable to find launcher.py for LumiMate Python runtime.".to_string())
    }
}

fn python_executable(root: &Path) -> PathBuf {
    let local = if cfg!(windows) {
        root.join(".venv").join("Scripts").join("python.exe")
    } else {
        root.join(".venv").join("bin").join("python")
    };
    if local.exists() {
        local
    } else {
        PathBuf::from(if cfg!(windows) { "python" } else { "python3" })
    }
}

fn reserve_port() -> Result<u16, String> {
    let listener = TcpListener::bind("127.0.0.1:0").map_err(|error| error.to_string())?;
    listener
        .local_addr()
        .map(|address| address.port())
        .map_err(|error| error.to_string())
}

fn spawn_backend() -> Result<BackendProcess, String> {
    let root = project_root()?;
    let port = reserve_port()?;
    let python = python_executable(&root);
    let child = Command::new(python)
        .arg("launcher.py")
        .arg("--api")
        .arg("--host")
        .arg("127.0.0.1")
        .arg("--port")
        .arg(port.to_string())
        .current_dir(root)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|error| format!("Unable to start LumiMate Python runtime: {error}"))?;

    Ok(BackendProcess { child, port })
}

fn stop_backend(state: &BackendState) -> Result<(), String> {
    let mut guard = state
        .child
        .lock()
        .map_err(|_| "Backend lock is unavailable.".to_string())?;
    if let Some(mut process) = guard.take() {
        let _ = process.child.kill();
        let _ = process.child.wait();
    }
    Ok(())
}

#[tauri::command]
fn backend_info(state: tauri::State<BackendState>) -> Result<BackendInfo, String> {
    let mut guard = state
        .child
        .lock()
        .map_err(|_| "Backend lock is unavailable.".to_string())?;

    let restart = match guard.as_mut() {
        Some(process) => process.child.try_wait().map_err(|error| error.to_string())?.is_some(),
        None => true,
    };

    if restart {
        *guard = Some(spawn_backend()?);
    }

    let port = guard
        .as_ref()
        .map(|process| process.port)
        .ok_or_else(|| "Backend runtime is not available.".to_string())?;

    Ok(BackendInfo {
        api_base: format!("http://127.0.0.1:{port}"),
        ws_url: format!("ws://127.0.0.1:{port}/ws/runtime"),
    })
}

#[tauri::command]
fn shutdown_backend(state: tauri::State<BackendState>) -> Result<(), String> {
    stop_backend(&state)
}

#[tauri::command]
fn minimize_window(window: Window) -> Result<(), String> {
    window.minimize().map_err(|error| error.to_string())
}

#[tauri::command]
fn toggle_window_mode(window: Window) -> Result<(), String> {
    let fullscreen = window.is_fullscreen().map_err(|error| error.to_string())?;
    window
        .set_fullscreen(!fullscreen)
        .map_err(|error| error.to_string())
}

#[tauri::command]
fn close_window(window: Window) -> Result<(), String> {
    window.close().map_err(|error| error.to_string())
}

fn main() {
    tauri::Builder::default()
        .manage(BackendState::default())
        .setup(|app| {
            if app.get_webview_window("main").is_none() {
                let window = WebviewWindowBuilder::new(app, "main", WebviewUrl::App("index.html".into()))
                    .title("LumiMate")
                    .inner_size(1440.0, 900.0)
                    .min_inner_size(1280.0, 720.0)
                    .resizable(true)
                    .center()
                    .decorations(true)
                    .visible(true)
                    .build()?;
                window.show()?;
                window.set_focus()?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            backend_info,
            shutdown_backend,
            minimize_window,
            toggle_window_mode,
            close_window
        ])
        .on_window_event(|window, event| {
            if matches!(event, tauri::WindowEvent::CloseRequested { .. }) {
                let state = window.state::<BackendState>();
                let _ = stop_backend(&state);
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running LumiMate");
}
