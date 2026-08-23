// LumiMate 审批桥 cordis 插件（Spike 自研方案，ADR 0001 回退路径）。
// 行为：审批问询写入 DSH_APPROVAL_OUTBOX/<key>.ask.json；
// 轮询 DSH_APPROVAL_INBOX/<key>.decision.json 直到 LumiMate 写入决定；
// allow -> allowed-once，reject -> rejected，超时/异常 -> next()（fail-closed）。
import { access, mkdir, readFile, unlink, writeFile } from "node:fs/promises";
import { join } from "node:path";

const ASK_TIMEOUT_MS = 90_000;
const POLL_INTERVAL_MS = 200;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fileExists(path) {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

function safeKey(sessionId, callId) {
  const base = String(callId || "")
    .replace(/[^A-Za-z0-9_-]/g, "_");
  return base ? `${sessionId}__${base}` : String(sessionId);
}

export default function apply(ctx, _config) {
  const inbox = process.env.DSH_APPROVAL_INBOX;
  const outbox = process.env.DSH_APPROVAL_OUTBOX;
  if (!inbox || !outbox) return;

  ctx.on("approval/request", async (request, next) => {
    const sessionId = request.agent?.session?.id ?? "unknown";
    const callId = request.callId ?? "";
    const key = safeKey(sessionId, callId);
    const askPath = join(outbox, `${key}.ask.json`);
    const decisionPath = join(inbox, `${key}.decision.json`);
    try {
      await mkdir(outbox, { recursive: true });
      await mkdir(inbox, { recursive: true });
      await writeFile(
        askPath,
        JSON.stringify({
          sessionId,
          toolName: request.toolName,
          callId,
          reason: request.reason ?? null,
          askedAt: new Date().toISOString(),
        }),
        "utf8",
      );
      const deadline = Date.now() + ASK_TIMEOUT_MS;
      while (Date.now() < deadline) {
        if (await fileExists(decisionPath)) {
          const decision = JSON.parse(await readFile(decisionPath, "utf8"));
          await unlink(decisionPath);
          if (decision.decision === "allow") return "allowed-once";
          if (decision.decision === "reject") return "rejected";
          return next();
        }
        await sleep(POLL_INTERVAL_MS);
      }
      return next();
    } catch {
      return next();
    }
  });
}
