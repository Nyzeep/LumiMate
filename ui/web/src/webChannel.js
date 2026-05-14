function loadQtWebChannelScript() {
  if (window.QWebChannel) {
    return Promise.resolve(true);
  }

  return new Promise((resolve) => {
    const existing = document.querySelector("script[data-lumimate-qwebchannel]");
    if (existing) {
      existing.addEventListener("load", () => resolve(Boolean(window.QWebChannel)), { once: true });
      existing.addEventListener("error", () => resolve(false), { once: true });
      return;
    }

    const script = document.createElement("script");
    script.src = "qrc:///qtwebchannel/qwebchannel.js";
    script.dataset.lumimateQwebchannel = "true";
    script.onload = () => resolve(Boolean(window.QWebChannel));
    script.onerror = () => resolve(false);
    document.head.appendChild(script);
  });
}

function waitForTransport(timeoutMs = 4000, intervalMs = 48) {
  return new Promise((resolve) => {
    const startedAt = Date.now();

    function poll() {
      if (window.qt?.webChannelTransport && window.QWebChannel) {
        resolve(true);
        return;
      }
      if (Date.now() - startedAt >= timeoutMs) {
        resolve(false);
        return;
      }
      window.setTimeout(poll, intervalMs);
    }

    poll();
  });
}

export async function createBridgeObjects() {
  const scriptReady = await loadQtWebChannelScript();
  if (!scriptReady) {
    return null;
  }

  const transportReady = await waitForTransport();
  if (!transportReady) {
    return null;
  }

  return new Promise((resolve) => {
    new window.QWebChannel(window.qt.webChannelTransport, (channel) => {
      resolve(channel.objects);
    });
  });
}

export function connectSignal(signal, callback) {
  if (signal?.connect) {
    signal.connect(callback);
  }
}

export function callQt(object, methodName, ...args) {
  const method = object?.[methodName];
  if (typeof method !== "function") {
    return Promise.resolve(undefined);
  }

  return new Promise((resolve) => {
    method(...args, resolve);
  });
}
