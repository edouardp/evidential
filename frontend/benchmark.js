import { JSDOM } from "jsdom";
import { fileURLToPath } from "node:url";
import { EvidentialTableRenderer } from "./src/table.js";

export function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

export function benchmarkRenderer(counts = [10000, 50000, 100000], repeats = 5) {
  if (!counts.length || counts.some((count) => !Number.isInteger(count) || count < 1) || !Number.isInteger(repeats) || repeats < 1) {
    throw new Error("Dataset sizes and repetitions must be positive integers");
  }
  const dom = new JSDOM("<body></body>");
  Object.assign(globalThis, {
    window: dom.window, document: dom.window.document, Node: dom.window.Node,
    ResizeObserver: class { observe() {} disconnect() {} },
    requestAnimationFrame: () => 0, cancelAnimationFrame: () => {},
  });
  const results = [];
  try {
    for (const count of counts) {
      const columns = Array.from({ length: 8 }, (_, index) => ({
        name: `value${index}`, type: "number", fmt: "num", viz: index === 0 ? "color" : null,
      }));
      const rows = Array.from({ length: count }, (_, index) => Object.fromEntries(
        columns.map((column, number) => [column.name, (index + number) / 10]),
      ));
      const data = { rows, columns, options: { page_size: 20, column_stats: true, align_decimals: true } };
      const el = document.createElement("div");
      document.body.append(el);
      const start = performance.now();
      const renderer = new EvidentialTableRenderer({ get: (key) => data[key] }, el);
      const initial = performance.now() - start;
      const navigation = [];
      for (let index = 0; index < repeats; index++) {
        const begin = performance.now();
        renderer._gotoPage(index % 2);
        navigation.push(performance.now() - begin);
      }
      results.push({ rows: count, columns: columns.length, initial_ms: initial, navigation_ms: median(navigation) });
      renderer.destroy();
      el.remove();
    }
  } finally {
    dom.window.close();
  }
  return { runtime: process.version, environment: "jsdom, DOM construction without browser layout", results };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const counts = process.argv.slice(2).map(Number);
  process.stdout.write(JSON.stringify(benchmarkRenderer(counts.length ? counts : undefined), null, 2) + "\n");
}
