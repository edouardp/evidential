import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { ASSET_DIR, ASSETS, buildAssets } from "./build.js";

export async function staleAssets(committedDirectory, builtDirectory) {
  const stale = [];
  for (const name of ASSETS) {
    const built = await readFile(join(builtDirectory, name));
    let committed;
    try {
      committed = await readFile(join(committedDirectory, name));
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
    if (!committed || !committed.equals(built)) stale.push(name);
  }
  return stale;
}

export async function checkBundle() {
  const directory = await mkdtemp(join(tmpdir(), "evidential-bundle-"));
  try {
    await buildAssets(directory);
    const stale = await staleAssets(ASSET_DIR, directory);
    if (stale.length) throw new Error(`Stale renderer assets: ${stale.join(", ")}. Run make frontend-build.`);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) await checkBundle();
