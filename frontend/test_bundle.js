import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { ASSETS, buildAssets } from "./build.js";
import { staleAssets } from "./check_bundle.js";

test("bundle check detects changed and missing assets without rewriting them", async (t) => {
  const first = await mkdtemp(join(tmpdir(), "evidential-build-a-"));
  const second = await mkdtemp(join(tmpdir(), "evidential-build-b-"));
  t.after(async () => {
    await rm(first, { recursive: true, force: true });
    await rm(second, { recursive: true, force: true });
  });
  await buildAssets(first);
  await buildAssets(second);
  assert.deepEqual(await staleAssets(first, second), []);
  for (const name of ASSETS) {
    const original = await readFile(join(first, name));
    await writeFile(join(first, name), "stale");
    assert.deepEqual(await staleAssets(first, second), [name]);
    assert.equal(await readFile(join(first, name), "utf8"), "stale");
    await rm(join(first, name));
    assert.deepEqual(await staleAssets(first, second), [name]);
    await writeFile(join(first, name), original);
  }
});
