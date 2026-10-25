import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { assertNoDebugCollector } from "./assert-no-debug-collector.mjs";

function fixture(t, files = {}) {
  const dir = mkdtempSync(path.join(os.tmpdir(), "ux-privacy-"));
  mkdirSync(dir, { recursive: true });
  writeFileSync(path.join(dir, "index.html"), "<html><body>UX Academy</body></html>");
  for (const [name, content] of Object.entries(files)) {
    const dest = path.join(dir, name);
    mkdirSync(path.dirname(dest), { recursive: true });
    writeFileSync(dest, content);
  }
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return dir;
}

test("clean public site is accepted", (t) => {
  const dir = fixture(t, { "assets/app.abcdef.js": "console.info('ready')" });
  assert.equal(assertNoDebugCollector(dir), true);
});

test("collector nested outside legacy directory is rejected", (t) => {
  const dir = fixture(t, { "assets/nested/debug-collector.js": "session data" });
  assert.throws(() => assertNoDebugCollector(dir), /collector leaked/);
});

test("page that injects collector is rejected", (t) => {
  const dir = fixture(t, { "pages/about.html": '<script src="/__manus__/debug-collector.js"></script>' });
  assert.throws(() => assertNoDebugCollector(dir), /references debug-collector/);
});

test("hashed emitted JS bundle that sends logs is rejected", (t) => {
  const dir = fixture(t, { "assets/index.123abc.js": 'fetch("/__manus__/logs")' });
  assert.throws(() => assertNoDebugCollector(dir), /references \/__manus__\/logs/);
});

test("session replay marker is rejected even in inline JavaScript", (t) => {
  const dir = fixture(t, { "assets/index.js": 'const signal="__MANUS_DEBUG_COLLECTOR__"' });
  assert.throws(() => assertNoDebugCollector(dir), /references __MANUS/);
});

test("entry point must exist", (t) => {
  const dir = fixture(t);
  rmSync(path.join(dir, "index.html"));
  assert.throws(() => assertNoDebugCollector(dir), /missing dist\/public\/index\.html/);
});

test("symlinks in public output are rejected", async (t) => {
  const dir = fixture(t);
  const { symlinkSync } = await import("node:fs");
  try {
    symlinkSync(path.join(dir, "index.html"), path.join(dir, "linked.html"));
  } catch (e) {
    t.skip("symlink unavailable: " + e.message);
    return;
  }
  assert.throws(() => assertNoDebugCollector(dir), /Unexpected symlink/);
});
