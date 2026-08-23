// Spike 工具：复刻 build-exe-for-python-sdk.ts 的 restoreLegacyHoists +
// materializeStagedLinks，修复 Windows 上 pnpm deploy 产出的 node 载体闭包。
import { existsSync } from "node:fs";
import {
  cp,
  lstat,
  mkdir,
  readFile,
  readdir,
  realpath,
  rm,
} from "node:fs/promises";
import { dirname, join, sep } from "node:path";

const root = "D:/DeepSeek Harness/deepseek-harness";
const staging = join(
  root,
  "python/sdk-runtime/src/deepseek_harness_runtime/runtime/node",
);
const sourceNodeModules = join(root, "python/sdk-runtime/node_modules");

async function restoreLegacyHoists() {
  const manifest = JSON.parse(await readFile(join(staging, "package.json"), "utf8"));
  for (const dependency of Object.keys(manifest.dependencies ?? {}).sort()) {
    const destination = join(staging, "node_modules", dependency);
    if (existsSync(destination)) continue;
    const source = join(sourceNodeModules, dependency);
    if (!existsSync(source)) {
      throw new Error(
        `staged dependency ${dependency} absent from both ${destination} and ${source}`,
      );
    }
    await mkdir(dirname(destination), { recursive: true });
    const nested = join(source, "node_modules");
    await cp(source, destination, {
      recursive: true,
      dereference: true,
      filter: (path) =>
        path !== nested && !path.startsWith(nested + sep),
    });
    console.log("restored", dependency);
  }
}

async function findSymlink(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    const metadata = await lstat(path);
    if (metadata.isSymbolicLink()) return path;
    if (metadata.isDirectory()) {
      const nested = await findSymlink(path);
      if (nested !== undefined) return nested;
    }
  }
  return undefined;
}

async function materializeStagedLinks() {
  const nodeModules = join(staging, "node_modules");
  let remaining = await findSymlink(nodeModules);
  while (remaining !== undefined) {
    const segments = remaining.slice(nodeModules.length + 1).split(sep);
    const binIndex = segments.lastIndexOf(".bin");
    if (binIndex >= 0) {
      await rm(join(nodeModules, ...segments.slice(0, binIndex + 1)), {
        recursive: true,
        force: true,
      });
      remaining = await findSymlink(nodeModules);
      continue;
    }
    const destination = remaining;
    const source = await realpath(destination);
    const nested = join(source, "node_modules");
    await rm(destination, { recursive: true, force: true });
    await cp(source, destination, {
      recursive: true,
      dereference: true,
      filter: (path) =>
        path !== nested && !path.startsWith(nested + sep),
    });
    console.log("materialized", destination);
    remaining = await findSymlink(nodeModules);
  }
}

await restoreLegacyHoists();
await materializeStagedLinks();
for (const name of ["README.md", "README.zh.md", "README.i18n.yaml"]) {
  await rm(join(staging, name), { force: true });
}
console.log("node carrier repaired");
