import { h } from "./dom.js";
import { formatValue } from "./format.js";
import { resolveColor } from "./color.js";
import { numeric, observationValue } from "./mark-data.js";
import { markLabelText, renderMarkLabel, autoLabelColor } from "./mark-labels.js";

/** Inline top/bottom/transform for a mark's `valign` (default centred). */
function verticalStyle(valign, point = false) {
  if (valign === "top") return { top: "0", transform: point ? "translate(-50%, 0)" : "none" };
  if (valign === "bottom") return { top: "auto", bottom: "0", transform: point ? "translate(-50%, 0)" : "none" };
  return point
    ? { top: "50%", transform: "translate(-50%, -50%)" }
    : { top: "50%", transform: "translateY(-50%)" };
}

/** Resolve a mark's colour: an explicit colour, a per-row column, or a default. */
function markColor(enc, row, fallback) {
  if (row && Number(row[enc.source]) < 0) {
    const negative = resolveColor(enc.color_negative) || resolveColor(row[enc.color_negative_column]);
    if (negative) return negative;
  }
  if (enc.color_column && row) {
    const resolved = resolveColor(row[enc.color_column]);
    if (resolved) return resolved;
  }
  return resolveColor(enc.color) || fallback;
}

/** An ordered categorical sequence: equal-width or positioned segments. */
function renderStrip(enc, row, lo, span) {
  const raw = row[enc.source];
  const items = Array.isArray(raw) ? raw : [];
  const colors = enc.colors || {};
  const colourOf = (category) => resolveColor(colors[String(category)]) || "var(--et-accent, #2563eb)";
  const named = (item) => (item && typeof item === "object" ? (item.category ?? item.state ?? item.value) : item);
  const positioned =
    span != null && items.some((item) => item && typeof item === "object" && (item.start != null || item.position != null));
  if (positioned) {
    const wrap = h("div", { class: "et-mark-strip et-mark-strip-positioned" });
    const at = (value) => Math.max(0, Math.min(100, ((value - lo) / span) * 100));
    items.forEach((item, index) => {
      if (!item || typeof item !== "object") return;
      const start = Number(item.start ?? item.position);
      if (!isFinite(start)) return;
      let end = item.end ?? item.finish;
      if (end == null) {
        // A change-point list fills to the next position; the last to the bound.
        const next = items[index + 1];
        end = next && typeof next === "object" && next.position != null ? next.position : lo + span;
      }
      const left = at(start);
      const width = Math.max(0, at(Number(end)) - left);
      const segment = h("div", {
        class: "et-strip-run",
        style: { left: `${left}%`, width: `${width}%`, backgroundColor: colourOf(named(item)) },
      });
      if (enc.strip_labels && named(item) != null && String(named(item)) !== "") {
        segment.append(h("span", { class: "et-strip-label" }, String(named(item)).charAt(0)));
      }
      wrap.append(segment);
    });
    return wrap;
  }
  const wrap = h("div", { class: "et-mark-strip" });
  for (const item of items) {
    const category = named(item);
    const segment = h("span", {
      class: `et-strip-seg${enc.segmented === false ? " et-strip-joined" : ""}`,
      style: { backgroundColor: category == null ? "transparent" : colourOf(category) },
    });
    if (enc.strip_labels && category != null && String(category) !== "") {
      segment.append(h("span", { class: "et-strip-label" }, String(category).charAt(0)));
    }
    wrap.append(segment);
  }
  return wrap;
}

/** One stack segment: an absolutely positioned coloured box with optional label. */
function stackSegment(enc, row, col, leftPct, widthPct, text = "") {
  const segment = h("div", {
    class: "et-mark-stack-seg",
    style: {
      left: `${leftPct}%`,
      width: `${Math.max(0, widthPct)}%`,
      backgroundColor: markColor(enc, row, "var(--et-accent, #2563eb)"),
    },
  });
  if (text) {
    const align = (enc.label || {}).align;
    if (align === "begin") segment.style.justifyContent = "flex-start";
    else if (align === "end") segment.style.justifyContent = "flex-end";
    const spec = enc.label || {};
    segment.title = text;
    const label = h("span", { class: "et-mark-stack-label", "data-mark-label": "",
      "data-overflow": spec.overflow || "hide", "data-min-width": spec.min_width || 0,
      style: spec.color ? {color: resolveColor(spec.color)} : {},
    }, h("span", {class: "et-mark-label-text"}, text));
    if (!spec.color) autoLabelColor(label, markColor(enc, row, "var(--et-accent, #2563eb)"));
    segment.append(label);
  }
  return segment;
}

/** The stack's label text: its share of the row, or its own value. */
function stackLabelText(col, enc, row, value, total, normalize) {
  if (!enc.label) return "";
  if (enc.label.share) {
    const share = total ? value / total : 0;
    return formatValue(share, enc.label.format || "pct0", {
      type: "number",
      fallback: `${Math.round(share * 100)}%`,
    });
  }
  return markLabelText(col, enc, row);
}

/** The stack container, sized by the first segment's `size` (height fraction). */
function stackContainer(encodings) {
  const size = encodings[0].size != null ? Math.max(0.05, Math.min(1, Number(encodings[0].size))) : 0.7;
  const inset = ((1 - size) / 2) * 100;
  return h("div", { class: "et-mark et-mark-stack", style: { top: `${inset}%`, bottom: `${inset}%` } });
}

/** A diverging stack: categories either side of a split neutral segment. */
function renderDivergingStack(col, encodings, row, normalize, lo, hi) {
  const values = encodings.map((enc) => {
    const num = Number(row[enc.source]);
    return isFinite(num) && num > 0 ? num : 0;
  });
  const total = values.reduce((sum, value) => sum + value, 0);
  const scaled = normalize ? values.map((value) => (total ? (value / total) * 100 : 0)) : values;
  const pivot = encodings.findIndex((enc) => enc.source === encodings[0].diverge_at);
  const maxArm = Math.max(Math.abs(lo), Math.abs(hi), 1e-9);
  const at = (value) => (value / maxArm) * 50;
  const stack = stackContainer(encodings);
  const pv = scaled[pivot];
  const label = (index, value) => stackLabelText(col, encodings[index], row, value, total, normalize);
  // The neutral segment straddles the origin: half left, half right.
  let left = pv / 2;
  stack.append(stackSegment(encodings[pivot], row, col, 50 - at(left), at(pv / 2), label(pivot, values[pivot])));
  for (let index = pivot - 1; index >= 0; index -= 1) {
    const value = scaled[index];
    stack.append(stackSegment(encodings[index], row, col, 50 - at(left + value), at(value), label(index, values[index])));
    left += value;
  }
  let right = pv / 2;
  stack.append(stackSegment(encodings[pivot], row, col, 50, at(pv / 2), ""));
  for (let index = pivot + 1; index < encodings.length; index += 1) {
    const value = scaled[index];
    stack.append(stackSegment(encodings[index], row, col, 50 + at(right), at(value), label(index, values[index])));
    right += value;
  }
  return stack;
}

/** A cumulative stack of segment magnitudes over the column's shared scale. */
function renderStack(col, encodings, row, lo, hi) {
  const normalize = (col.scale || {}).normalize === "percent";
  if (encodings[0].diverge_at) {
    return renderDivergingStack(col, encodings, row, normalize, lo, hi);
  }
  const values = encodings.map((enc) => {
    const num = Number(row[enc.source]);
    return isFinite(num) && num > 0 ? num : 0;
  });
  const total = values.reduce((sum, value) => sum + value, 0);
  const stack = stackContainer(encodings);
  // Percent stacks always span 0..100; raw stacks share the column's domain.
  const spanTotal = (hi - lo) || 1;
  let cursor = 0;
  encodings.forEach((enc, index) => {
    const magnitude = normalize ? (total ? (values[index] / total) * 100 : 0) : values[index];
    const width = (magnitude / spanTotal) * 100;
    stack.append(
      stackSegment(enc, row, col, ((cursor - lo) / spanTotal) * 100, width, stackLabelText(col, enc, row, values[index], total, normalize)),
    );
    cursor += magnitude;
  });
  return stack;
}

/** A precomputed five-number summary with optional outliers. */
function renderBox(col, enc, row, pos) {
  const parts = enc.parts || {};
  const value = (name) => numeric(row[parts[name]]);
  const [minimum, q1, median, q3, maximum] = ["minimum", "q1", "median", "q3", "maximum"].map(value);
  if ([minimum, q1, median, q3, maximum].some((number) => number == null)) {
    return h("span", { class: "et-null" }, "–");
  }
  const color = markColor(enc, row, "var(--et-accent, #2563eb)");
  const box = h("div", { class: "et-mark et-mark-box" });
  box.append(h("div", { class: "et-box-whisker", style: { left: `${pos(minimum)}%`, width: `${Math.max(0, pos(maximum) - pos(minimum))}%`, backgroundColor: color } }));
  box.append(h("div", { class: "et-box-cap", style: { left: `${pos(minimum)}%`, backgroundColor: color } }));
  box.append(h("div", { class: "et-box-cap", style: { left: `${pos(maximum)}%`, backgroundColor: color } }));
  box.append(h("div", { class: "et-box-iqr", style: { left: `${pos(q1)}%`, width: `${Math.max(0, pos(q3) - pos(q1))}%`, borderColor: color, backgroundColor: color } }));
  box.append(h("div", { class: "et-box-median", style: { left: `${pos(median)}%`, backgroundColor: color } }));
  const outliers = enc.outliers && Array.isArray(row[enc.outliers]) ? row[enc.outliers] : [];
  for (const outlier of outliers) {
    const number = numeric(outlier);
    if (number == null) continue;
    box.append(h("div", { class: "et-box-outlier", style: { left: `${pos(number)}%`, backgroundColor: color } }));
  }
  return box;
}

/** A density band from a precomputed ordered ``[{x, y}]`` series. */
function renderDistribution(enc, row, pos, color) {
  const raw = row[enc.source];
  const items = Array.isArray(raw) ? raw : [];
  const points = [];
  for (const item of items) {
    if (!item) continue;
    const x = Number(item[enc.x]);
    const y = Number(item[enc.y]);
    if (isFinite(x) && isFinite(y) && y >= 0) points.push([x, y]);
  }
  if (points.length < 2) return null;
  const maxY = Math.max(...points.map((point) => point[1])) || 1;
  const coords = points.map(([x, y]) => {
    const left = pos(x);
    return [Math.max(0, Math.min(100, left == null ? 0 : left)), 100 - (y / maxY) * 100];
  });
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("class", "et-mark et-mark-distribution");
  svg.setAttribute("viewBox", "0 0 100 100");
  svg.setAttribute("preserveAspectRatio", "none");
  const polygon = document.createElementNS(ns, "polygon");
  polygon.setAttribute(
    "points",
    `${coords.map((point) => point.join(",")).join(" ")} ${coords[coords.length - 1][0]},100 ${coords[0][0]},100`,
  );
  polygon.setAttribute("fill", color);
  polygon.setAttribute("opacity", "0.35");
  svg.append(polygon);
  const line = document.createElementNS(ns, "polyline");
  line.setAttribute("points", coords.map((point) => point.join(",")).join(" "));
  line.setAttribute("fill", "none");
  line.setAttribute("stroke", color);
  line.setAttribute("stroke-width", "1");
  svg.append(line);
  return svg;
}

/**
 * Render a column's ordered encodings over one shared scale. Bars, points and
 * ranges are positioned absolutely in a full-height track; the shared domain
 * comes from the column's own ``scale`` or the data range across every source.
 */
/**
 * The shared {lo, hi, span, transform} of a marks column: an explicit
 * ``scale.domain`` wins, otherwise the data range (zero included for bars).
 */
export function marksDomain(col, range) {
  const scale = col.scale || {};
  let lo = scale.domain && scale.domain[0] != null ? Number(scale.domain[0]) : (range?.min ?? 0);
  let hi = scale.domain && scale.domain[1] != null ? Number(scale.domain[1]) : (range?.max ?? 1);
  const hasBar = (col.encodings || []).some((enc) => enc.kind === "bar" || enc.kind === "stacked_bar");
  if (scale.include_zero !== false && hasBar && scale.transform !== "log") {
    if (scale.domain?.[0] == null) lo = Math.min(0, lo);
    if (scale.domain?.[1] == null) hi = Math.max(0, hi);
  }
  // Two-sided layouts accept a 0..magnitude domain or an explicit symmetric
  // signed domain. Their axes, references and overlay points use signed x.
  if ((col.encodings || []).some(enc => enc.side || enc.diverge_at) && (!scale.domain || lo >= 0)) {
    hi = Math.max(Math.abs(lo), Math.abs(hi));
    lo = -hi;
  }
  return { lo, hi, span: (hi - lo) || 1, transform: scale.transform };
}

/** Round tick values spanning ``lo..hi`` (for an axis or gridlines). */
export function niceTicks(lo, hi, count = 4, transform = null) {
  if (!isFinite(lo) || !isFinite(hi) || hi <= lo) return [];
  if (transform === "log" && lo > 0) {
    // A power-of-ten ladder (with 2x and 5x subdivisions) for a log axis.
    const ticks = [];
    for (let exp = Math.floor(Math.log10(lo)) - 1; exp <= Math.ceil(Math.log10(hi)); exp += 1) {
      for (const multiple of [1, 2, 5]) {
        const value = multiple * Math.pow(10, exp);
        if (value >= lo && value <= hi) ticks.push(Number(value.toPrecision(12)));
      }
    }
    if (ticks.length) return ticks;
  }
  const step0 = (hi - lo) / Math.max(1, count);
  const magnitude = Math.pow(10, Math.floor(Math.log10(step0)));
  const normalized = step0 / magnitude;
  const step = (normalized >= 5 ? 5 : normalized >= 2.5 ? 2.5 : normalized >= 2 ? 2 : 1) * magnitude;
  const ticks = [];
  for (let value = Math.ceil(lo / step) * step; value <= hi + step * 1e-6; value += step) {
    ticks.push(Number(value.toFixed(10)));
  }
  return ticks;
}

/** A position function mapping a value in ``lo..hi`` to 0..100 (percent). */
export function scalePosition(lo, hi, transform) {
  return markScale(lo, hi, transform);
}

function markScale(lo, hi, transform) {
  if (transform === "log" && lo > 0 && hi > lo) {
    const l0 = Math.log(lo);
    const lspan = (Math.log(hi) - l0) || 1;
    return (value) => {
      const num = numeric(value);
      if (num == null || num <= 0) return null;
      return ((Math.log(num) - l0) / lspan) * 100;
    };
  }
  const span = (hi - lo) || 1;
  return (value) => {
    const num = numeric(value);
    return num != null ? ((num - lo) / span) * 100 : null;
  };
}

export function renderMarks(col, row, range) {
  const encodings = col.encodings || [];
  const scale = col.scale || {};
  const {lo, hi, span} = marksDomain(col, range);
  const pos = markScale(lo, hi, scale.transform);
  const clampPos = (value) => {
    const pct = pos(value);
    return pct == null ? null : Math.max(0, Math.min(100, pct));
  };
  const track = h("div", { class: "et-marks" });
  const description = encodings.map(enc => [enc.source, enc.high, ...Object.values(enc.parts || {})]
    .filter(field => field && row[field] != null).map(field => `${field}: ${JSON.stringify(row[field])}`).join(", "))
    .filter(Boolean).join("; ");
  track.title = description;
  track.setAttribute("role", "img");
  track.setAttribute("aria-label", description || "No observations");
  if (encodings.some(enc => ["above", "below"].includes(enc.label?.position))) track.classList.add("et-marks-tall");

  // Faint vertical lines at round values help read a mark against the scale.
  if (scale.gridlines) {
    for (const tick of niceTicks(lo, hi, 4, scale.transform)) {
      const pct = pos(tick);
      if (pct == null) continue;
      track.append(
        h("div", { class: "et-mark-gridline", style: { left: `${Math.max(0, Math.min(100, pct))}%` } }),
      );
    }
  }

  // Column-wide reference rules paint behind the marks.
  for (const ref of col.references || []) {
    if (ref.value == null || !isFinite(Number(ref.value))) continue;
    const raw = pos(Number(ref.value));
    if (raw == null) continue;
    const pct = raw;
    if (ref.high != null && isFinite(Number(ref.high))) {
      const rawHigh = pos(Number(ref.high));
      if (rawHigh == null) continue;
      const left = Math.max(0, Math.min(100, Math.min(pct, rawHigh)));
      const right = Math.max(0, Math.min(100, Math.max(pct, rawHigh)));
      if (right <= left) continue;
      track.append(
        h("div", {
          class: "et-mark-band",
          style: {
            left: `${left}%`,
            width: `${right - left}%`,
            backgroundColor: resolveColor(ref.color) || "var(--et-reference, #0f766e)",
          },
        }),
      );
      if (ref.label) {
        track.append(
          h("span", { class: "et-mark-reference-label", style: { left: `${left}%` } }, String(ref.label)),
        );
      }
      continue;
    }
    if (pct < 0 || pct > 100) continue;
    track.append(
      h("div", {
        class: "et-mark-reference",
        style: {
          left: `${pct}%`,
          backgroundColor: resolveColor(ref.color) || "var(--et-reference, #0f766e)",
        },
      }),
    );
    if (ref.label) {
      track.append(
        h("span", { class: "et-mark-reference-label", style: { left: `${pct}%` } }, String(ref.label)),
      );
    }
  }

  const barCount = encodings.filter((enc) => enc.kind === "bar").length;
  const stack = encodings.filter((enc) => enc.kind === "stacked_bar");
  let barIndex = 0;
  for (const enc of encodings) {
    if (enc.kind === "stacked_bar") {
      if (enc === stack[0]) track.append(renderStack(col, stack, row, lo, hi));
      continue;
    }
    if (enc.kind === "boxplot") {
      track.append(renderBox(col, enc, row, clampPos));
      continue;
    }
    if (enc.kind === "distribution") {
      const node = renderDistribution(enc, row, clampPos, markColor(enc, row, "var(--et-accent, #2563eb)"));
      if (node) track.append(node);
      continue;
    }
    const value = numeric(row[enc.source]);
    if (["bar", "point", "range"].includes(enc.kind) && value == null) continue;
    if (enc.kind === "bar") {
      const size = enc.size != null ? Number(enc.size) : barCount > 1 ? Math.max(0.25, 0.85 - barIndex * 0.3) : 1;
      barIndex += 1;
      const color = markColor(enc, row, "var(--et-accent, #2563eb)");
      let leftPct;
      let widthPct;
      if (enc.side === "left" || enc.side === "right") {
        const maxAbs = Math.max(Math.abs(lo), Math.abs(hi), 1e-9);
        const width = Math.max(0, Math.min(50, (Math.abs(value) / maxAbs) * 50));
        widthPct = width;
        leftPct = enc.side === "left" ? 50 - width : 50;
      } else {
        const origin = clampPos(0);
        const end = clampPos(value);
        leftPct = origin != null ? origin : 0;
        widthPct = end != null ? end - leftPct : 0;
        if (widthPct < 0) {
          leftPct += widthPct;
          widthPct = -widthPct;
        }
      }
      track.append(
        h("div", {
          class: `et-mark et-mark-bar${enc.side ? ` et-mark-bar-${enc.side}` : ""}`,
          style: {
            ...verticalStyle(enc.valign),
            left: `${leftPct}%`,
            width: `${Math.max(0, widthPct)}%`,
            height: `${Math.max(0, Math.min(1, size)) * 100}%`,
            backgroundColor: color,
          },
        }),
      );
      if (enc.label) track.append(renderMarkLabel(col, enc, row, { leftPct, widthPct, color, negative: value < 0 || enc.side === "left" }));
    } else if (enc.kind === "points") {
      const values = Array.isArray(row[enc.source]) ? row[enc.source] : [];
      const size = enc.size != null ? Number(enc.size) : 6;
      const color = markColor(enc, row, "var(--et-accent, #2563eb)");
      for (const item of values) {
        const raw = observationValue(item);
        const pct = clampPos(raw);
        if (pct == null) continue;
        track.append(
          h("div", {
            class: "et-mark et-mark-point",
            style: { ...verticalStyle(enc.valign, true), left: `${pct}%`, width: `${size}px`, height: `${size}px`, backgroundColor: color },
          }),
        );
      }
    } else if (enc.kind === "point") {
      const pct = clampPos(value);
      if (pct == null) continue;
      const size = enc.size != null ? Number(enc.size) : 7;
      track.append(
        h("div", {
          class: "et-mark et-mark-point",
          style: { ...verticalStyle(enc.valign, true), left: `${pct}%`, width: `${size}px`, height: `${size}px`, backgroundColor: markColor(enc, row, "var(--et-accent, #2563eb)") },
        }),
      );
      if (enc.label) track.append(renderMarkLabel(col, enc, row, { pointPct: pct }));
    } else if (enc.kind === "strip") {
      track.append(renderStrip(enc, row, lo, span));
    } else if (enc.kind === "range") {
      const low = value;
      const high = numeric(row[enc.high]);
      if (high == null) continue;
      let start = pos(low);
      let end = pos(high);
      const offScale = (value) => value == null || value < 0 || value > 100;
      const arrowStart = (enc.overflow === "arrow" || enc.cap === "arrow") && offScale(start);
      const arrowEnd = (enc.overflow === "arrow" || enc.cap === "arrow") && offScale(end);
      if (arrowStart) start = start != null && start > 100 ? 100 : 0;
      if (arrowEnd) end = end != null && end < 0 ? 0 : 100;
      if (start == null || end == null) continue;
      start = Math.max(0, Math.min(100, start));
      end = Math.max(0, Math.min(100, end));
      const left = Math.min(start, end);
      const right = Math.max(start, end);
      const size = enc.size != null ? Number(enc.size) : 4;
      const color = markColor(enc, row, "var(--et-accent, #2563eb)");
      if (enc.fill) {
        // A translucent band, e.g. a forecast or uncertainty range.
        const band = h("div", {
            class: "et-mark et-mark-range-fill",
            style: {
              top: "15%",
              bottom: "15%",
              transform: "none",
              left: `${left}%`,
              width: `${Math.max(0, right - left)}%`,
              backgroundColor: color,
            },
          });
        if (arrowStart) band.append(h("span", { class: "et-mark-cap et-mark-arrow et-mark-arrow-start", style: { borderRightColor: color } }));
        if (arrowEnd) band.append(h("span", { class: "et-mark-cap et-mark-arrow et-mark-arrow-end", style: { borderLeftColor: color } }));
        track.append(band);
        if (enc.label) track.append(renderMarkLabel(col, enc, row, { pointPct: left }));
        continue;
      }
      const line = h("div", {
        class: "et-mark et-mark-range",
        style: { ...verticalStyle(enc.valign), left: `${left}%`, width: `${Math.max(0, right - left)}%`, height: `${size}px`, backgroundColor: color },
      });
      if (enc.cap === "line" || enc.cap === "dot") {
        const capClass = `et-mark-cap${enc.cap === "dot" ? " et-mark-cap-dot" : ""}`;
        if (!arrowStart) line.append(h("span", { class: `${capClass} et-mark-cap-start`, style: { backgroundColor: color } }));
        if (!arrowEnd) line.append(h("span", { class: `${capClass} et-mark-cap-end`, style: { backgroundColor: color } }));
      }
      if (arrowStart) line.append(h("span", { class: "et-mark-cap et-mark-arrow et-mark-arrow-start", style: { borderRightColor: color } }));
      if (arrowEnd) line.append(h("span", { class: "et-mark-cap et-mark-arrow et-mark-arrow-end", style: { borderLeftColor: color } }));
      track.append(line);
      if (enc.label) track.append(renderMarkLabel(col, enc, row, { pointPct: left }));
    }
  }
  return track;
}

export function renderBar(col, value, formatted, range, row) {
  const opts = col.bar_options || {};
  const num = Number(value);
  const min = opts.fit_to_data ? (range?.min ?? 0) : Math.min(0, range?.min ?? 0);
  const max = opts.fit_to_data ? (range?.max ?? 0) : Math.max(0, range?.max ?? 0);
  const negative = num < 0;
  // A leftward bar fills from the right edge — the mirror of the default, for a
  // back-to-back ("tornado") league table.
  const leftward = opts.direction === "left";
  // A per-row colour column (`bar(color="@column")`) wins over a fixed colour.
  const rowColor =
    opts.bar_color_column && row ? resolveColor(row[opts.bar_color_column]) : null;
  const color = negative
    ? (rowColor || resolveColor(opts.bar_color_negative) || resolveColor(opts.bar_color) || "var(--et-negative, #dc2626)")
    : (rowColor || resolveColor(opts.bar_color) || "var(--et-accent, #2563eb)");
  const label = h(
    "span",
    { class: `et-bar-label${opts.hide_labels ? " et-hidden" : ""}` },
    formatted,
  );
  const background = opts.background_color ? { backgroundColor: opts.background_color } : {};
  // `pad` insets the bar — and, in centred mode, the centre line's ends on the
  // first/last row — from the top and bottom (a px number or a CSS length).
  const pad =
    opts.pad == null ? null : typeof opts.pad === "number" ? `${opts.pad}px` : String(opts.pad);

  let cell;
  if (opts.center) {
    // A zero-centred "diverging" bar: the bar grows left (negative) or right
    // (positive) from a centre line by its magnitude, and the value sits on the
    // opposite side of the line.
    const maxAbs = Math.max(Math.abs(min), Math.abs(max), 1e-9);
    const width = Math.max(0, Math.min(100, (Math.abs(num) / maxAbs) * 100)) / 2;
    const bar = h("div", {
      class: `et-bar et-bar-${negative ? "left" : "right"}`,
      style: { width: `${width}%`, backgroundColor: color },
    });
    const axis = h("div", { class: "et-bar-axis" });
    const wrap = h("div", { class: "et-bar-wrap" }, [axis, bar]);
    label.classList.add(negative ? "et-bar-label-right" : "et-bar-label-left");
    cell = h("div", { class: "et-bar-cell et-bar-center", style: background }, [wrap, label]);
  } else {
    const span = max - min || 1;
    const pct = Math.max(0, Math.min(100, ((num - min) / span) * 100));
    const bar = h("div", {
      class: `et-bar${leftward ? " et-bar-fill-left" : ""}`,
      style: { width: `${pct}%`, backgroundColor: color },
    });
    const marks = referenceMarks(opts, min, span, leftward);
    const wrap = h("div", { class: `et-bar-wrap${negative ? " et-bar-negative" : ""}` }, [bar, ...marks]);
    cell = h("div", { class: "et-bar-cell", style: background }, [wrap, label]);
  }
  if (pad) cell.style.setProperty("--et-bar-pad", pad);
  return cell;
}

/** A vertical benchmark rule (and its caption) for a bar column. */
function referenceMarks(opts, min, span, leftward) {
  if (opts.reference == null || !isFinite(Number(opts.reference))) return [];
  const pct = Math.max(0, Math.min(100, ((Number(opts.reference) - min) / span) * 100));
  // A leftward bar mirrors the scale, so its rule mirrors with it.
  const left = leftward ? 100 - pct : pct;
  const color = resolveColor(opts.reference_color) || "var(--et-reference, #0f766e)";
  const marks = [
    h("div", { class: "et-bar-reference", style: { left: `${left}%`, backgroundColor: color } }),
  ];
  if (opts.reference_label) {
    // Keep the caption inside the column: centre it on the rule, but anchor it
    // to the nearer edge when the rule sits near one end.
    const anchor =
      left > 60 ? "translateX(-100%)" : left < 40 ? "translateX(0)" : "translateX(-50%)";
    marks.push(
      h(
        "span",
        { class: "et-bar-reference-label", style: { left: `${left}%`, color, transform: anchor } },
        String(opts.reference_label),
      ),
    );
  }
  return marks;
}

/** A numeric value as that many repeated symbols — glyphs, emoji or images. */
export function renderSymbols(col, value, formatted) {
  const opts = col.symbol_options || {};
  const num = Number(value);
  if (value === null || value === undefined || value === "" || Number.isNaN(num)) {
    return h("span", { class: "et-null" }, formatted ?? "–");
  }
  const filled = Math.max(0, Math.round(num));
  const total = opts.max != null ? Math.max(filled, Math.round(Number(opts.max))) : filled;
  const wrap = h("span", { class: "et-symbols" });
  if (opts.size != null) wrap.style.fontSize = `${opts.size}em`;
  if (opts.gap != null) wrap.style.gap = `${opts.gap}em`;
  for (let i = 0; i < total; i++) {
    const on = i < filled;
    if (opts.image) {
      wrap.append(
        h("img", {
          class: `et-symbol-image${on ? "" : " et-symbol-empty"}`,
          src: String(opts.image),
          alt: "",
          loading: "lazy",
        }),
      );
      continue;
    }
    if (opts.shape) {
      // A CSS-drawn box: pixel-exact and font-independent (unlike a glyph).
      const box = h("span", {
        class: `et-symbol-box et-symbol-box-${opts.shape}${on ? "" : " et-symbol-empty"}`,
      });
      const side = opts.size != null ? `${opts.size}em` : null;
      if (side) box.style.width = box.style.height = side;
      const fill = on ? opts.color : opts.empty_color;
      if (fill) box.style.backgroundColor = resolveColor(fill);
      wrap.append(box);
      continue;
    }
    const node = h(
      "span",
      { class: `et-symbol${on ? "" : " et-symbol-empty"}` },
      on ? (opts.symbol || "●") : (opts.empty || opts.symbol || "●"),
    );
    const colour = on ? opts.color : opts.empty_color;
    if (colour) node.style.color = resolveColor(colour);
    wrap.append(node);
  }
  return wrap;
}

/** Resolve a neutral band from a string, pair, symmetric bound or explicit min/max. */
export function neutralBounds(opts) {
  const range = opts.neutral_range;
  if (typeof range === "string") {
    const match = range.match(/^\s*(-?\d+(?:\.\d+)?)\s*(?::|\.\.)\s*(-?\d+(?:\.\d+)?)\s*$/);
    if (match) return [Number(match[1]), Number(match[2])];
  }
  if (Array.isArray(range) && range.length === 2) return [Number(range[0]), Number(range[1])];
  if (typeof range === "number" && isFinite(range)) return [-Math.abs(range), Math.abs(range)];
  return [opts.neutral_min ?? 0, opts.neutral_max ?? 0];
}

export function renderDelta(col, value) {
  const opts = col.delta_options || {};
  const isMissing = value === null || value === undefined;
  const num = isMissing ? 0 : Number(value);
  const [lo, hi] = neutralBounds(opts);
  const isNeutral =
    isMissing || ((lo == null || num >= lo) && (hi == null || num <= hi));
  const positive = num > 0;
  const good = isNeutral ? false : opts.down_is_good ? !positive : positive;
  const cls = isNeutral ? "et-delta-neutral" : good ? "et-delta-good" : "et-delta-bad";
  // The indicator is a dash for a neutral value, otherwise an up/down arrow.
  const indicator =
    opts.show_symbol === false ? "" : isNeutral ? "–" : positive ? "▲" : num < 0 ? "▼" : "–";
  // A `pct`-formatted delta holds a fraction, so always show it as a
  // percentage — even above 100% (e.g. a 307% change) — rather than falling
  // back to a bare number.
  const pct =
    col.fmt && col.fmt.startsWith("pct")
      ? formatValue(Math.abs(num), col.fmt, {
          type: "number",
          fallback: String(Math.abs(num)),
        })
      : Math.abs(num).toLocaleString(undefined, { maximumFractionDigits: 1 });
  const valueText = opts.show_value === false || isMissing ? "" : pct;
  const valueNode = valueText ? h("span", { class: "et-delta-value" }, valueText) : null;
  const indicatorNode = indicator
    ? h("span", { class: "et-delta-indicator" }, indicator)
    : null;
  // The indicator follows the value by default (e.g. "12.0% ▲").
  const ordered =
    opts.symbol_position === "left" ? [indicatorNode, valueNode] : [valueNode, indicatorNode];
  const content = [];
  for (const node of ordered) {
    if (!node) continue;
    if (content.length) content.push(" ");
    content.push(node);
  }
  const classes = ["et-delta", cls, opts.chip ? "et-delta-chip" : ""].filter(Boolean).join(" ");
  return h("span", { class: classes }, content.length ? content : "–");
}

export { renderSparkline, sparklinePoints } from "./sparkline.js";
