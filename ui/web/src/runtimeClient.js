const DEFAULT_API_BASE = "http://127.0.0.1:8765";

let backendInfoPromise = null;
let websocket = null;

function trimSlash(value) {
  return String(value || "").replace(/\/+$/, "");
}

function resolveWsUrl(apiBase) {
  return trimSlash(apiBase).replace(/^http:/, "ws:").replace(/^https:/, "wss:") + "/ws/runtime";
}

async function invokeTauri(command, args = {}) {
  const invoke = window.__TAURI__?.core?.invoke;
  if (typeof invoke !== "function") {
    return null;
  }
  return invoke(command, args);
}

export async function backendInfo() {
  if (backendInfoPromise) {
    return backendInfoPromise;
  }

  backendInfoPromise = (async () => {
    const params = new URLSearchParams(window.location.search);
    const queryApi = params.get("apiBase") || params.get("api");
    if (queryApi) {
      const apiBase = trimSlash(queryApi);
      return { apiBase, wsUrl: resolveWsUrl(apiBase) };
    }

    try {
      const info = await invokeTauri("backend_info");
      if (info?.apiBase) {
        return { apiBase: trimSlash(info.apiBase), wsUrl: info.wsUrl || resolveWsUrl(info.apiBase) };
      }
    } catch (error) {
      console.warn("Tauri backend_info unavailable, falling back to local runtime.", error);
    }

    return { apiBase: DEFAULT_API_BASE, wsUrl: resolveWsUrl(DEFAULT_API_BASE) };
  })();

  return backendInfoPromise;
}

export async function runtimeRequest(path, body) {
  const info = await backendInfo();
  const attempts = body === undefined ? 120 : 3;
  let response = null;
  let lastError = null;

  for (let index = 0; index < attempts; index += 1) {
    try {
      response = await fetch(`${info.apiBase}${path}`, {
        method: body === undefined ? "GET" : "POST",
        headers: body === undefined ? undefined : { "Content-Type": "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body)
      });
      break;
    } catch (error) {
      lastError = error;
      await new Promise((resolve) => window.setTimeout(resolve, 500));
    }
  }

  if (!response) {
    throw lastError || new Error(`Runtime request failed: ${path}`);
  }
  if (!response.ok) {
    throw new Error(`Runtime request failed: ${response.status} ${path}`);
  }
  return response.json();
}

export async function getRuntimeState() {
  return runtimeRequest("/api/state");
}

export async function runtimeCommand(path, body = {}) {
  const result = await runtimeRequest(path, body);
  return Boolean(result?.ok);
}

export async function connectRuntimeEvents(onEvent) {
  const info = await backendInfo();
  if (websocket && websocket.readyState <= WebSocket.OPEN) {
    return websocket;
  }

  websocket = new WebSocket(info.wsUrl);
  websocket.addEventListener("message", (event) => {
    try {
      onEvent(JSON.parse(event.data));
    } catch (error) {
      console.warn("Ignored malformed runtime event.", error);
    }
  });
  websocket.addEventListener("close", () => {
    window.setTimeout(() => {
      websocket = null;
      connectRuntimeEvents(onEvent).catch(() => {});
    }, 1200);
  });
  return websocket;
}

export async function minimizeWindow() {
  try {
    await invokeTauri("minimize_window");
    return true;
  } catch {
    return false;
  }
}

export async function toggleWindowMode() {
  try {
    await invokeTauri("toggle_window_mode");
    return true;
  } catch {
    return false;
  }
}

export async function closeWindow() {
  try {
    await invokeTauri("close_window");
    return true;
  } catch {
    return false;
  }
}

export async function shutdownBackend() {
  try {
    await invokeTauri("shutdown_backend");
    return true;
  } catch {
    return false;
  }
}
