import { build } from "esbuild";
import { copyFile, mkdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const FRONTEND_DIR = dirname(fileURLToPath(import.meta.url));
export const ASSET_DIR = join(FRONTEND_DIR, "../src/evidential/static");
export const ASSETS = ["table.js", "table.css"];

export async function buildAssets(outputDirectory = ASSET_DIR) {
  await mkdir(outputDirectory, { recursive: true });
  await build({
    absWorkingDir: FRONTEND_DIR,
    entryPoints: ["src/index.js"],
    bundle: true,
    format: "esm",
    minify: true,
    legalComments: "linked",
    outfile: join(outputDirectory, "table.js"),
  });
  await copyFile(join(FRONTEND_DIR, "src/table.css"), join(outputDirectory, "table.css"));
}

if (process.argv[1] === fileURLToPath(import.meta.url)) await buildAssets();
