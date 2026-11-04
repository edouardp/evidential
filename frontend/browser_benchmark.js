// Real browser workload: keep ResizeObserver, animation frames and layout active.
export async function benchmarkTable(data, samples = 5) {
  const {default: widget} = await import("/src/evidential/static/table.js");
  const frame = () => new Promise(resolve => requestAnimationFrame(resolve));
  const settle = async () => { await frame(); await frame(); await frame(); };
  const el = document.createElement("div");
  el.className = "evidential-widget";
  document.body.replaceChildren(el);
  const start = performance.now();
  const cleanup = widget.render({el, model: {get: key => data[key], on() {}, off() {}, save_changes() {}}});
  try {
    await settle();
    const initial = performance.now() - start;
    const durations = [];
    for (let index = 0; index < samples; index++) {
      const button = el.querySelector('button[aria-label="Next page"]');
      if (!button || button.disabled) throw new Error("Benchmark needs enough records for every navigation sample");
      const before = performance.now();
      button.click();
      await settle();
      durations.push(performance.now() - before);
    }
    durations.sort((a, b) => a - b);
    return {
      rows: data.rows.length,
      initial_ms: initial,
      navigation_median_ms: durations[Math.floor(durations.length / 2)],
      visible_rows: el.querySelectorAll("tbody tr").length,
      fitted_labels: el.querySelectorAll("[data-label-position]").length,
      point_clusters: el.querySelectorAll(".et-point-composite").length,
    };
  } finally { cleanup(); }
}
