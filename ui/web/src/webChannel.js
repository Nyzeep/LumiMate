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

export async function createBridgeObjects() {
  await loadQtWebChannelScript();
  return new Promise((resolve) => {
    if (!window.qt?.webChannelTransport || !window.QWebChannel) {
      resolve(null);
      return;
    }

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
