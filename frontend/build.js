import { build } from "esbuild";
import { copyFile, mkdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const FRONTEND_DIR = dirname(fileURLToPath(import.meta.url));
export const ASSET_DIR = join(FRONTEND_DIR, "../src/evidential/static");
export const ASSETS = ["table.js", "table.css", "dimension-grid.js", "dimension-grid.css"];

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
  await build({
    absWorkingDir: FRONTEND_DIR,
    entryPoints: ["src/dimension-grid.js"],
    bundle: true,
    format: "esm",
    minify: true,
    legalComments: "linked",
    outfile: join(outputDirectory, "dimension-grid.js"),
  });
  await copyFile(join(FRONTEND_DIR, "src/dimension-grid.css"), join(outputDirectory, "dimension-grid.css"));
}

if (process.argv[1] === fileURLToPath(import.meta.url)) await buildAssets();
