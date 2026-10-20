import { h } from "./dom.js";
import { formatValue } from "./format.js";
import { resolveColor } from "./color.js";

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

/** The label text for a mark: a literal, another field, or the mark's value. */
function markLabelText(col, enc, row) {
  const spec = enc.label || {};
  const raw = spec.source != null ? row[spec.source] : row[enc.source];
  if (spec.text != null) return String(spec.text);
  if (raw === null || raw === undefined) return "";
  return formatValue(raw, spec.format || col.fmt, {
    type: col.type,
    fallback: String(raw),
  });
}

/** A mark-owned label, positioned relative to its bar or point. */
function renderMarkLabel(col, enc, row, geometry) {
  const spec = enc.label || {};
  const text = markLabelText(col, enc, row);
  if (!text) return h("span", { class: "et-mark-label et-mark-label-empty" });
  const position = spec.position || (enc.kind === "bar" ? "outside_end" : "center");
  const node = h("span", { class: `et-mark-label et-mark-label-${position}` }, text);
  if (geometry.leftPct != null) {
    const inside = ["inside_start", "inside_end", "center"].includes(position);
    if (inside) {
      node.style.left = `${geometry.leftPct}%`;
      node.style.width = `${Math.max(0, geometry.widthPct)}%`;
      node.classList.add("et-mark-label-inside");
      if (position === "inside_start") node.classList.add("et-mark-label-start");
    } else {
      node.style.left = `${geometry.leftPct + geometry.widthPct}%`;
    }
  } else if (geometry.pointPct != null) {
    node.style.left = `${geometry.pointPct}%`;
  }
  return node;
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
      style: { backgroundColor: colourOf(category) },
    });
    if (enc.strip_labels && category != null && String(category) !== "") {
      segment.append(h("span", { class: "et-strip-label" }, String(category).charAt(0)));
    }
    wrap.append(segment);
  }
  return wrap;
}

/** One stack segment: an absolutely positioned coloured box with optional label. */
function stackSegment(enc, row, col, leftPct, widthPct, showLabel = true) {
  const segment = h("div", {
    class: "et-mark-stack-seg",
    style: {
      left: `${leftPct}%`,
      width: `${Math.max(0, widthPct)}%`,
      backgroundColor: markColor(enc, row, "var(--et-accent, #2563eb)"),
    },
  });
  if (showLabel && enc.label) {
    const text = markLabelText(col, enc, row);
    if (text) segment.append(h("span", { class: "et-mark-stack-label" }, text));
  }
  return segment;
}

/** A diverging stack: categories either side of a split neutral segment. */
function renderDivergingStack(col, encodings, row, maxAbs) {
  const pivot = encodings.findIndex((enc) => enc.source === encodings[0].diverge_at);
  const magnitude = (enc) => {
    const num = Number(row[enc.source]);
    return isFinite(num) && num > 0 ? num : 0;
  };
  const at = (value) => (maxAbs ? (value / maxAbs) * 50 : 0);
  const stack = h("div", { class: "et-mark et-mark-stack" });
  const pv = magnitude(encodings[pivot]);
  // The neutral segment straddles the origin: half left, half right.
  let left = pv / 2;
  stack.append(stackSegment(encodings[pivot], row, col, 50 - at(left), at(pv / 2)));
  for (let index = pivot - 1; index >= 0; index -= 1) {
    const value = magnitude(encodings[index]);
    stack.append(stackSegment(encodings[index], row, col, 50 - at(left + value), at(value)));
    left += value;
  }
  let right = pv / 2;
  stack.append(stackSegment(encodings[pivot], row, col, 50, at(pv / 2), false));
  for (let index = pivot + 1; index < encodings.length; index += 1) {
    const value = magnitude(encodings[index]);
    stack.append(stackSegment(encodings[index], row, col, 50 + at(right), at(value)));
    right += value;
  }
  return stack;
}

/** A cumulative stack of segment magnitudes over the column's shared scale. */
function renderStack(col, encodings, row, lo, hi) {
  if (encodings[0].diverge_at) {
    return renderDivergingStack(col, encodings, row, Math.max(Math.abs(lo), Math.abs(hi)) || 1);
  }
  const values = encodings.map((enc) => {
    const num = Number(row[enc.source]);
    return isFinite(num) && num > 0 ? num : 0;
  });
  const total = values.reduce((sum, value) => sum + value, 0);
  const normalize = (col.scale || {}).normalize === "percent";
  const spanTotal = normalize ? 1 : (hi - lo) || 1;
  const stack = h("div", { class: "et-mark et-mark-stack" });
  let cursor = 0;
  encodings.forEach((enc, index) => {
    const magnitude = normalize ? (total ? values[index] / total : 0) : values[index];
    stack.append(stackSegment(enc, row, col, (cursor / spanTotal) * 100, (magnitude / spanTotal) * 100));
    cursor += magnitude;
  });
  return stack;
}

/** A precomputed five-number summary with optional outliers. */
function renderBox(col, enc, row, pos) {
  const parts = enc.parts || {};
  const value = (name) => Number(row[parts[name]]);
  const [minimum, q1, median, q3, maximum] = ["minimum", "q1", "median", "q3", "maximum"].map(value);
  if ([minimum, q1, median, q3, maximum].some((number) => !isFinite(number))) {
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
    const number = Number(outlier);
    if (!isFinite(number)) continue;
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
function markScale(lo, hi, transform) {
  if (transform === "log" && lo > 0 && hi > lo) {
    const l0 = Math.log(lo);
    const lspan = (Math.log(hi) - l0) || 1;
    return (value) => {
      const num = Number(value);
      if (!isFinite(num) || num <= 0) return null;
      return ((Math.log(num) - l0) / lspan) * 100;
    };
  }
  const span = (hi - lo) || 1;
  return (value) => {
    const num = Number(value);
    return isFinite(num) ? ((num - lo) / span) * 100 : null;
  };
}

export function renderMarks(col, row, range) {
  const encodings = col.encodings || [];
  const scale = col.scale || {};
  let lo = scale.domain && scale.domain[0] != null ? Number(scale.domain[0]) : (range?.min ?? 0);
  let hi = scale.domain && scale.domain[1] != null ? Number(scale.domain[1]) : (range?.max ?? 1);
  const hasBar = encodings.some((enc) => enc.kind === "bar" || enc.kind === "stacked_bar");
  if (scale.include_zero !== false && hasBar && scale.transform !== "log") {
    lo = Math.min(0, lo);
    hi = Math.max(0, hi);
  }
  const span = (hi - lo) || 1;
  const pos = markScale(lo, hi, scale.transform);
  const clampPos = (value) => {
    const pct = pos(value);
    return pct == null ? null : Math.max(0, Math.min(100, pct));
  };
  const track = h("div", { class: "et-marks" });

  // Column-wide reference rules paint behind the marks.
  for (const ref of col.references || []) {
    if (ref.value == null || !isFinite(Number(ref.value))) continue;
    const raw = pos(Number(ref.value));
    if (raw == null) continue;
    const pct = Math.max(0, Math.min(100, raw));
    if (ref.high != null && isFinite(Number(ref.high))) {
      const rawHigh = pos(Number(ref.high));
      if (rawHigh == null) continue;
      const left = Math.max(0, Math.min(100, Math.min(pct, rawHigh)));
      const right = Math.max(0, Math.min(100, Math.max(pct, rawHigh)));
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
  if (stack.length) track.append(renderStack(col, stack, row, lo, hi));
  for (const box of encodings.filter((enc) => enc.kind === "boxplot")) {
    track.append(renderBox(col, box, row, clampPos));
  }
  for (const dist of encodings.filter((enc) => enc.kind === "distribution")) {
    const node = renderDistribution(dist, row, clampPos, markColor(dist, row, "var(--et-accent, #2563eb)"));
    if (node) track.append(node);
  }
  let barIndex = 0;
  for (const enc of encodings) {
    if (enc.kind === "stacked_bar" || enc.kind === "boxplot" || enc.kind === "distribution") continue;
    const value = Number(row[enc.source]);
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
        const origin = pos(0);
        const end = pos(value);
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
            left: `${leftPct}%`,
            width: `${Math.max(0, widthPct)}%`,
            height: `${Math.max(0, Math.min(1, size)) * 100}%`,
            backgroundColor: color,
          },
        }),
      );
      if (enc.label) track.append(renderMarkLabel(col, enc, row, { leftPct, widthPct }));
    } else if (enc.kind === "points") {
      const values = Array.isArray(row[enc.source]) ? row[enc.source] : [];
      const size = enc.size != null ? Number(enc.size) : 6;
      const color = markColor(enc, row, "var(--et-accent, #2563eb)");
      for (const item of values) {
        const raw = item && typeof item === "object" ? (item.value ?? item.x ?? item.y) : item;
        const pct = clampPos(Number(raw));
        if (pct == null) continue;
        track.append(
          h("div", {
            class: "et-mark et-mark-point",
            style: { left: `${pct}%`, width: `${size}px`, height: `${size}px`, backgroundColor: color },
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
          style: { left: `${pct}%`, width: `${size}px`, height: `${size}px`, backgroundColor: markColor(enc, row, "var(--et-accent, #2563eb)") },
        }),
      );
      if (enc.label) track.append(renderMarkLabel(col, enc, row, { pointPct: pct }));
    } else if (enc.kind === "strip") {
      track.append(renderStrip(enc, row, lo, span));
    } else if (enc.kind === "range") {
      const low = Number(row[enc.source]);
      const high = Number(row[enc.high]);
      let start = pos(low);
      let end = pos(high);
      const offScale = (value) => value == null || value < 0 || value > 100;
      const arrowStart = enc.cap === "arrow" && offScale(start);
      const arrowEnd = enc.cap === "arrow" && offScale(end);
      if (arrowStart) start = start != null && start > 100 ? 100 : 0;
      if (arrowEnd) end = end != null && end < 0 ? 0 : 100;
      if (start == null || end == null) continue;
      start = Math.max(0, Math.min(100, start));
      end = Math.max(0, Math.min(100, end));
      const left = Math.min(start, end);
      const right = Math.max(start, end);
      const size = enc.size != null ? Number(enc.size) : 4;
      const color = markColor(enc, row, "var(--et-accent, #2563eb)");
      const line = h("div", {
        class: "et-mark et-mark-range",
        style: { left: `${left}%`, width: `${Math.max(0, right - left)}%`, height: `${size}px`, backgroundColor: color },
      });
      if (enc.cap === "line" || enc.cap === "dot") {
        line.append(h("span", { class: "et-mark-cap et-mark-cap-start", style: { backgroundColor: color } }));
        line.append(h("span", { class: "et-mark-cap et-mark-cap-end", style: { backgroundColor: color } }));
      }
      if (arrowStart) line.append(h("span", { class: "et-mark-cap et-mark-arrow et-mark-arrow-start", style: { borderColor: color } }));
      if (arrowEnd) line.append(h("span", { class: "et-mark-cap et-mark-arrow et-mark-arrow-end", style: { borderColor: color } }));
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

export function renderSparkline(col, value) {
  const opts = col.sparkline_options || {};
  const points = sparklinePoints(value, opts);
  if (!points.length) return h("span", { class: "et-null" }, "–");

  const width = opts.width || 64;
  const height = opts.height || 18;
  const pad = 1.5;
  const ys = points.map((point) => point[1]);
  let min = Math.min(...ys);
  let max = Math.max(...ys);
  if (!opts.fit_to_data) {
    min = Math.min(0, min);
    max = Math.max(0, max);
  }
  const span = max - min || 1;
  const step = points.length > 1 ? (width - pad * 2) / (points.length - 1) : 0;
  const baseline = pad + (height - pad * 2) * (1 - (Math.max(0, min) - min) / span);
  const scaled = points.map(([x, y], index) => ({
    x: points.length > 1 ? pad + index * step : width / 2,
    y: pad + (height - pad * 2) * (1 - (y - min) / span),
    raw: [x, y],
  }));

  const color = opts.color || "var(--et-accent, #2563eb)";
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("class", "et-sparkline");
  svg.setAttribute("width", String(width));
  svg.setAttribute("height", String(height));
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

  const tooltip = ([x, y]) => {
    const title = document.createElementNS(svgNS, "title");
    const yText = formatValue(y, opts.y_fmt, { type: "number", fallback: String(y) });
    title.textContent = x === undefined || x === null || x === "" ? yText : `${x}: ${yText}`;
    return title;
  };

  // Zero baseline when the scale crosses zero (matching Evidence's defaults).
  if (!opts.fit_to_data && min < 0 && max > 0) {
    const zero = document.createElementNS(svgNS, "line");
    zero.setAttribute("x1", "0");
    zero.setAttribute("x2", String(width));
    zero.setAttribute("y1", String(baseline));
    zero.setAttribute("y2", String(baseline));
    zero.setAttribute("stroke", "color-mix(in srgb, CanvasText 20%, transparent)");
    zero.setAttribute("stroke-width", "1");
    svg.append(zero);
  }

  const type = opts.type || "line";
  const showMarkers = !!opts.markers || type === "points";
  if (type === "bar") {
    const slot = width / scaled.length;
    const barWidth = Math.max(1, slot * 0.7);
    scaled.forEach((point) => {
      const top = Math.min(point.y, baseline);
      const rect = document.createElementNS(svgNS, "rect");
      rect.setAttribute("x", String(Math.max(0, point.x - barWidth / 2)));
      rect.setAttribute("y", String(top));
      rect.setAttribute("width", String(barWidth));
      rect.setAttribute("height", String(Math.max(1, Math.abs(baseline - point.y))));
      rect.setAttribute("rx", "0.5");
      rect.setAttribute("fill", color);
      rect.append(tooltip(point.raw));
      svg.append(rect);
    });
  } else if (type !== "points") {
    const linePoints = scaled.map((point) => `${point.x},${point.y}`).join(" ");
    if (type === "area") {
      if (opts.signed) {
        // Split the fill at the zero baseline: up and down get their own colour.
        addArea(svgNS, svg, scaled, baseline, (point) => Math.min(point.y, baseline), color);
        addArea(svgNS, svg, scaled, baseline, (point) => Math.max(point.y, baseline), "var(--et-negative, #dc2626)");
      } else {
        addArea(svgNS, svg, scaled, baseline, (point) => point.y, color);
      }
    }
    const poly = document.createElementNS(svgNS, "polyline");
    poly.setAttribute("points", linePoints);
    poly.setAttribute("fill", "none");
    poly.setAttribute("stroke", color);
    poly.setAttribute("stroke-width", "1.25");
    poly.setAttribute("stroke-linejoin", "round");
    poly.setAttribute("stroke-linecap", "round");
    svg.append(poly);
  }
  scaled.forEach((point) => {
    const dot = document.createElementNS(svgNS, "circle");
    dot.setAttribute("cx", String(point.x));
    dot.setAttribute("cy", String(point.y));
    dot.setAttribute("r", showMarkers ? "2.2" : "2.5");
    dot.setAttribute("fill", showMarkers ? color : "transparent");
    dot.append(tooltip(point.raw));
    svg.append(dot);
  });
  return svg;
}

/** Add an area polygon under a sparkline, following a per-point baseline clip. */
function addArea(svgNS, svg, scaled, baseline, clip, fill) {
  const area = document.createElementNS(svgNS, "polygon");
  const points = scaled.map((point) => `${point.x},${clip(point)}`).join(" ");
  area.setAttribute(
    "points",
    `${points} ${scaled[scaled.length - 1].x},${baseline} ${scaled[0].x},${baseline}`,
  );
  area.setAttribute("fill", fill);
  area.setAttribute("opacity", "0.22");
  svg.append(area);
}

/** Normalize numbers, [x, y] pairs or objects into sparkline points. */
export function sparklinePoints(value, opts) {
  if (!Array.isArray(value)) return [];
  const xKey = opts.x;
  const yKey = opts.y;
  const points = [];
  value.forEach((item, index) => {
    if (item === null || item === undefined) return;
    let x = index;
    let y;
    if (Array.isArray(item)) {
      x = item[0];
      y = Number(item[1]);
    } else if (typeof item === "object") {
      const keys = Object.keys(item);
      const yField = yKey && yKey in item ? yKey : keys.find((key) => _isNumeric(item[key]));
      const xField =
        xKey && xKey in item ? xKey : keys.find((key) => key !== yField && !_isNumeric(item[key]));
      x = xField ? item[xField] : index;
      y = Number(yField ? item[yField] : NaN);
    } else {
      y = Number(item);
    }
    if (y !== null && !isNaN(y)) points.push([x, y]);
  });
  return points;
}

function _isNumeric(value) {
  if (typeof value === "number") return Number.isFinite(value);
  if (typeof value === "string") return value.trim() !== "" && !isNaN(Number(value));
  return false;
}
