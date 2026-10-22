import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

/** Fail a production build if instrumentation or session replay leaks into public output. */
export function assertNoDebugCollector(outputDirectory = path.resolve("dist", "public")) {
  const entryPoint = path.join(outputDirectory, "index.html");
  if (!fs.existsSync(entryPoint) || !fs.statSync(entryPoint).isFile()) {
    throw new Error("Production output is missing dist/public/index.html.");
  }

  const queue = [outputDirectory];
  while (queue.length > 0) {
    const directory = queue.pop();
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const file = path.join(directory, entry.name);
      if (entry.isSymbolicLink()) {
        throw new Error("Unexpected symlink in public output: " + file);
      }
      if (entry.isDirectory()) {
        queue.push(file);
        continue;
      }
      if (!entry.isFile()) continue;
      if (/debug-collector\.(?:m?js|cjs)$/i.test(entry.name)) {
        throw new Error("Session-debug collector leaked into production: " + file);
      }
      if (/\.(?:html|m?js|cjs)$/i.test(entry.name)) {
        const source = fs.readFileSync(file, "utf8");
        const dangerous = [
          "debug-collector.js",
          "/__manus__/logs",
          "__MANUS_DEBUG_COLLECTOR__",
          "sessionReplay.log",
        ];
        for (const marker of dangerous) {
          if (source.includes(marker)) {
            throw new Error("Production asset references " + marker + ": " + file);
          }
        }
      }
    }
  }
  return true;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    assertNoDebugCollector(path.resolve(process.argv[2] || "dist/public"));
    console.log("Production privacy check passed.");
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
