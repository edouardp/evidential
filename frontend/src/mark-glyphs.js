// Per-kind glyphs share a coordinate/label context; no renderer state lives here.
import {h} from "./dom.js";
import {formatValue} from "./format.js";
import {formattedText} from "./formatted-text.js";
import {resolveColor} from "./color.js";
import {markColor, pointSeries} from "./mark-series.js";
import {numeric, observationValue} from "./mark-data.js";
import {renderDensityBand, readDensity} from "./density-band.js";
import {inspectable} from "./tooltips.js";
import {markTooltip, observationTooltip, tooltipValue, seriesName} from "./tooltip-data.js";
import {markLabelText, autoLabelColor, labelTextStyle} from "./mark-labels.js";

/** Inline top/bottom/transform for a mark's `valign` (default centred). */
function verticalStyle(valign, point = false) {
  if (valign === "top") return { top: "0", transform: point ? "translate(-50%, 0)" : "none" };
  if (valign === "bottom") return { top: "auto", bottom: "0", transform: point ? "translate(-50%, 0)" : "none" };
  return point
    ? { top: "50%", transform: "translate(-50%, -50%)" }
    : { top: "50%", transform: "translateY(-50%)" };
}

/** Preserve the theme ring unless a point explicitly hides or recolors it. */
function pointOutlineStyle(outline) {
  if (outline === false) return { boxShadow: "none" };
  if (typeof outline === "string") return { boxShadow: `0 0 0 1px ${resolveColor(outline) || outline}` };
  return {};
}

/** Direction follows projected endpoints; equality and fully clipped spans omit it. */
function rangeDirection(enc, start, end, color) {
  if (!enc.direction_marker || start === end) return null;
  return h("span", {
    class: "et-range-direction", "data-direction": end > start ? "right" : "left",
    "aria-hidden": "true", style: { color },
  });
}

/** An ordered categorical sequence: equal-width or positioned segments. */
function renderStrip(enc, row, lo, span, col, context) {
  const raw = row[enc.source];
  const items = Array.isArray(raw) ? raw : [];
  const colors = enc.colors || {};
  const colourOf = (category) => resolveColor(colors[String(category)]) || "var(--et-accent, #2563eb)";
  const named = (item) => (item && typeof item === "object" ? (item.category ?? item.state ?? item.value) : item);
  const inspect = (segment, item) => {
    const category = named(item);
    if (category != null) inspectable(segment, observationTooltip(
      seriesName(col, enc, String(category), context), "", null, item, colourOf(category), ["category", "state", "value"]), {priority: 2});
    return segment;
  };
  const positioned =
    span != null && items.some((item) => item && typeof item === "object" && (item.start != null || item.position != null));
  if (positioned) {
    const wrap = h("div", { class: `et-mark-strip et-mark-strip-positioned${enc.segmented === false ? " et-mark-strip-joined" : ""}` });
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
      const right = 100 - Math.max(left, at(Number(end)));
      const segment = h("div", {
        class: "et-strip-run",
        // Inset both edges so neighbouring intervals share one rounded boundary.
        // Rounding left + width independently can leave a visible hairline seam.
        style: { left: `${left}%`, right: `${right}%`, backgroundColor: colourOf(named(item)) },
      });
      if (enc.strip_labels && named(item) != null && String(named(item)) !== "") {
        segment.append(h("span", { class: "et-strip-label" }, String(named(item)).charAt(0)));
      }
      wrap.append(inspect(segment, item));
    });
    return wrap;
  }
  const wrap = h("div", { class: `et-mark-strip${enc.segmented === false ? " et-mark-strip-joined" : ""}` });
  for (const item of items) {
    const category = named(item);
    const segment = h("span", {
      class: `et-strip-seg${enc.segmented === false ? " et-strip-joined" : ""}`,
      style: { backgroundColor: category == null ? "transparent" : colourOf(category) },
    });
    if (enc.strip_labels && category != null && String(category) !== "") {
      segment.append(h("span", { class: "et-strip-label" }, String(category).charAt(0)));
    }
    wrap.append(inspect(segment, item));
  }
  return wrap;
}

/** One stack segment: an absolutely positioned coloured box with optional label. */
function stackSegment(enc, row, col, leftPct, widthPct, text = "", context = {}) {
  const left = Math.max(0, Math.min(100, leftPct));
  const right = Math.max(0, Math.min(100, leftPct + widthPct));
  const segment = h("div", {
    class: "et-mark-stack-seg",
    style: {
      left: `${left}%`,
      width: `${Math.max(0, right - left)}%`,
      backgroundColor: markColor(enc, row, "var(--et-accent, #2563eb)"),
    },
  });
  const total = (col.encodings || []).filter(item => item.kind === "stacked_bar")
    .reduce((sum, item) => sum + (Number(row[item.source]) > 0 ? Number(row[item.source]) : 0), 0);
  inspectable(segment, markTooltip(col, enc, row, {total, context}), {priority: 2});
  if (text) {
    const align = enc.label?.align || (enc.label?.position === "inside_start" ? "begin" : enc.label?.position === "center" ? "center" : "end");
    if (align === "begin") segment.style.justifyContent = "flex-start";
    else if (align === "end") segment.style.justifyContent = "flex-end";
    const spec = enc.label || {};
    const label = h("span", { class: "et-mark-stack-label", "data-mark-label": "",
      "data-overflow": spec.overflow || "hide", "data-min-width": spec.min_width || 0,
      style: labelTextStyle(spec),
    }, h("span", {class: "et-mark-label-text"}, formattedText(text)));
    if (!spec.color) autoLabelColor(label, markColor(enc, row, "var(--et-accent, #2563eb)"));
    segment.append(label);
  }
  return segment;
}

/** The stack's label text: its share of the row, or its own value. */
function stackLabelText(col, enc, row, value, total, normalize, format) {
  if (!enc.label) return "";
  if (enc.label.share) {
    const share = total ? value / total : 0;
    return formatValue(share, enc.label.format || "pct0", {
      type: "number",
      fallback: `${Math.round(share * 100)}%`,
    });
  }
  return markLabelText(col, enc, row, format);
}

/** The stack container, sized by the first segment's `size` (height fraction). */
function stackContainer(encodings) {
  const size = encodings[0].size != null ? Math.max(0.05, Math.min(1, Number(encodings[0].size))) : 0.7;
  const inset = ((1 - size) / 2) * 100;
  return h("div", { class: "et-mark et-mark-stack", style: { top: `${inset}%`, bottom: `${inset}%` } });
}

/** A diverging stack: categories either side of a split neutral segment. */
function renderDivergingStack(col, encodings, row, normalize, lo, hi, format, context) {
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
  const label = (index, value) => stackLabelText(col, encodings[index], row, value, total, normalize, format);
  // The neutral segment straddles the origin: half left, half right.
  let left = pv / 2;
  stack.append(stackSegment(encodings[pivot], row, col, 50 - at(left), at(pv / 2), label(pivot, values[pivot]), context));
  for (let index = pivot - 1; index >= 0; index -= 1) {
    const value = scaled[index];
    stack.append(stackSegment(encodings[index], row, col, 50 - at(left + value), at(value), label(index, values[index]), context));
    left += value;
  }
  let right = pv / 2;
  stack.append(stackSegment(encodings[pivot], row, col, 50, at(pv / 2), "", context));
  for (let index = pivot + 1; index < encodings.length; index += 1) {
    const value = scaled[index];
    stack.append(stackSegment(encodings[index], row, col, 50 + at(right), at(value), label(index, values[index]), context));
    right += value;
  }
  return stack;
}

/** A cumulative stack of segment magnitudes over the column's shared scale. */
function renderStack(col, encodings, row, lo, hi, format, context) {
  const normalize = (col.scale || {}).normalize === "percent";
  if (encodings[0].diverge_at) {
    return renderDivergingStack(col, encodings, row, normalize, lo, hi, format, context);
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
      stackSegment(enc, row, col, ((cursor - lo) / spanTotal) * 100, width, stackLabelText(col, enc, row, values[index], total, normalize, format), context),
    );
    cursor += magnitude;
  });
  return stack;
}

/** A precomputed five-number summary with optional outliers. */
function renderBox(col, enc, row, pos, context) {
  const parts = enc.parts || {};
  const value = (name) => numeric(row[parts[name]]);
  const [minimum, q1, median, q3, maximum] = ["minimum", "q1", "median", "q3", "maximum"].map(value);
  if ([minimum, q1, median, q3, maximum].some((number) => number == null)) {
    return h("span", { class: "et-null" }, "–");
  }
  const color = markColor(enc, row, "var(--et-accent, #2563eb)");
  const box = h("div", { class: "et-mark et-mark-box" });
  inspectable(box, markTooltip(col, enc, row, {context}));
  box.append(h("div", { class: "et-box-whisker", style: { left: `${pos(minimum)}%`, width: `${Math.max(0, pos(maximum) - pos(minimum))}%`, backgroundColor: color } }));
  box.append(h("div", { class: "et-box-cap", style: { left: `${pos(minimum)}%`, backgroundColor: color } }));
  box.append(h("div", { class: "et-box-cap", style: { left: `${pos(maximum)}%`, backgroundColor: color } }));
  box.append(h("div", { class: "et-box-iqr", style: { left: `${pos(q1)}%`, width: `${Math.max(0, pos(q3) - pos(q1))}%`, borderColor: color, backgroundColor: color } }));
  box.append(h("div", { class: "et-box-median", style: { left: `${pos(median)}%`, backgroundColor: color } }));
  const outliers = enc.outliers && Array.isArray(row[enc.outliers]) ? row[enc.outliers] : [];
  for (const outlier of outliers) {
    const number = numeric(outlier);
    if (number == null) continue;
    box.append(inspectable(h("div", { class: "et-box-outlier", style: { left: `${pos(number)}%`, backgroundColor: color } }),
      {name: "Outlier", value: tooltipValue(number, context.formatCode ?? col.fmt, col), color}, {priority: 3}));
  }
  return box;
}

function drawBar(enc, view) {
  const {col, row, track, clampPos, lo, hi, barCount, reverse, format, labelFor, context} = view;
  const value = numeric(row[enc.source]);
  if (value == null) return;
  const size = enc.size != null ? Number(enc.size) : barCount > 1 ? Math.max(0.25, 0.85 - view.barIndex * 0.3) : 1;
  view.barIndex += 1;
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
  if (enc.background) track.prepend(h("div", {class: "et-mark et-mark-background",
    style: {inset: "0", backgroundColor: resolveColor(enc.background) || enc.background}}));
  const pad = enc.pad == null ? null : typeof enc.pad === "number" ? `${enc.pad}px` : String(enc.pad);
  const height = pad ? (typeof enc.pad === "number" ? `calc(${size * 100}% - ${2 * enc.pad}px)` : `calc(${size * 100}% - ${pad} - ${pad})`) : `${size * 100}%`;
  track.append(
    inspectable(h("div", {
      class: `et-mark et-mark-bar${enc.side ? ` et-mark-bar-${enc.side}` : ""}`,
      style: {
        ...verticalStyle(enc.valign),
        left: `${leftPct}%`,
        width: `${Math.max(0, widthPct)}%`,
        height,
        backgroundColor: color,
      },
    }), markTooltip(col, enc, row, {context}), {priority: 2}),
  );
  if (!enc.hide_labels && enc.label) {
    const labelled = enc.center && !enc.label.position ? {...enc, label: {...enc.label, position: "outside_start"}} : enc;
    track.append(labelFor(col, labelled, row, { leftPct, widthPct, color, negative: reverse ? value >= 0 : value < 0 || enc.side === "left" }, format));
  }
}

function drawPoints(enc, view) {
  const {col, row, track, clampPos, format, labelFor, context} = view;
  const values = Array.isArray(row[enc.source]) ? row[enc.source] : [];
  const size = enc.size != null ? Number(enc.size) : enc.sources ? 9 : 6;
  const observations = enc.sources ? pointSeries(enc).map(point => ({point, raw: row[point.source]}))
    : values.map(item => ({point: enc, raw: observationValue(item), observation: item}));
  const projected = observations.map(item => ({...item, pct: clampPos(item.raw)})).filter(item => item.pct != null);
  if (enc.connect && projected.length > 1) {
    const positions = projected.map(item => item.pct);
    const left = Math.min(...positions), right = Math.max(...positions);
    if (right > left) track.append(h("div", {class: "et-mark et-mark-range et-point-connector",
      "aria-hidden": "true", style: {...verticalStyle(enc.valign), left: `${left}%`, width: `${right-left}%`,
        height: "1px", backgroundColor: "var(--et-muted, #94a3b8)"}}));
  }
  for (const {point, raw, pct, observation} of projected) {
    const data = enc.sources ? markTooltip(col, point, row, {value: raw, context})
      : observationTooltip(seriesName(col, enc, enc.source, context), raw, context.formatCode ?? col.fmt, observation,
        markColor(point, row), ["value", "y"]);
    data.xValue = Number(raw);
    track.append(
      inspectable(h("div", {
        class: "et-mark et-mark-point",
        style: { ...verticalStyle(enc.valign, true), ...pointOutlineStyle(enc.outline), left: `${pct}%`, width: `${size}px`, height: `${size}px`, backgroundColor: markColor(point, row) },
      }), data, {priority: 3}),
    );
    if (enc.label) track.append(labelFor(col, point, {...row, [point.source]: raw}, {pointPct: pct}, format));
  }
}

function drawPoint(enc, view) {
  const {col, row, track, clampPos, format, labelFor, context} = view;
  const value = numeric(row[enc.source]);
  if (value == null) return;
  const pct = clampPos(value);
  if (pct == null) return;
  const size = enc.size != null ? Number(enc.size) : 7;
  track.append(
    inspectable(h("div", {
      class: "et-mark et-mark-point",
      style: { ...verticalStyle(enc.valign, true), ...pointOutlineStyle(enc.outline), left: `${pct}%`, width: `${size}px`, height: `${size}px`, backgroundColor: markColor(enc, row, "var(--et-accent, #2563eb)") },
    }), markTooltip(col, enc, row, {context}), {priority: 3}),
  );
  if (enc.label) track.append(labelFor(col, enc, row, { pointPct: pct }, format));
}

function drawStrip(enc, view) {
  const {col, row, track, lo, span, format, labelFor, context} = view;
  track.append(renderStrip(enc, row, lo, span, col, context));
  if (enc.label) track.append(labelFor(col, enc, row, {pointPct: 50}, format));
}

function drawRange(enc, view) {
  const {col, row, track, pos, format, labelFor, context} = view;
  const value = numeric(row[enc.source]);
  if (value == null) return;
  const low = value;
  const high = numeric(row[enc.high]);
  if (high == null) return;
  let start = pos(low);
  let end = pos(high);
  const offScale = (value) => value == null || value < 0 || value > 100;
  const arrowStart = (enc.overflow === "arrow" || enc.cap === "arrow") && offScale(start);
  const arrowEnd = (enc.overflow === "arrow" || enc.cap === "arrow") && offScale(end);
  if (arrowStart) start = start != null && start > 100 ? 100 : 0;
  if (arrowEnd) end = end != null && end < 0 ? 0 : 100;
  if (start == null || end == null) return;
  start = Math.max(0, Math.min(100, start));
  end = Math.max(0, Math.min(100, end));
  const left = Math.min(start, end);
  const right = Math.max(start, end);
  const size = enc.size != null ? Number(enc.size) : 4;
  const color = markColor(enc, row, "var(--et-accent, #2563eb)", high < low);
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
    track.append(inspectable(band, markTooltip(col, enc, row, {context})));
    const direction = rangeDirection(enc, start, end, color);
    if (direction) {
      direction.style.left = `${(left + right) / 2}%`;
      track.append(direction);
    }
    if (enc.label) track.append(labelFor(col, enc, row, { pointPct: left }, format));
    return;
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
  const direction = rangeDirection(enc, start, end, color);
  if (direction) line.append(direction);
  track.append(inspectable(line, markTooltip(col, enc, row, {context})));
  if (enc.label) track.append(labelFor(col, enc, row, { pointPct: left }, format));
}

function drawBoxplot(enc, view) {
  const {col, row, track, clampPos, format, labelFor, context} = view;
  track.append(renderBox(col, enc, row, clampPos, context));
  const median = clampPos(row[enc.source]);
  if (enc.label && median != null) track.append(labelFor(col, enc, row, {pointPct: median}, format));
}

function drawDistribution(enc, view) {
  const {col, row, track, pos, format, labelFor, context} = view;
  const node = renderDensityBand(enc, row, pos, markColor(enc, row, "var(--et-accent, #2563eb)"));
  if (node) {
    const runs = readDensity(row[enc.source], enc.distribution);
    let count = 0, peak = 0;
    for (const run of runs) for (const sample of run) { count++; peak = Math.max(peak, sample.density); }
    const inspect = value => tooltipValue(value, context.formatCode ?? col.fmt, col);
    inspectable(node, {name: seriesName(col, enc, enc.source, context), value: "Density band",
      color: markColor(enc, row), details: [
        {name: "Support start", value: inspect(runs[0][0].x)},
        {name: "Support end", value: inspect(runs.at(-1).at(-1).x)},
        {name: "Peak density", value: tooltipValue(peak)},
        {name: "Samples", value: tooltipValue(count)},
      ]});
    track.append(node);
    if (enc.label) track.append(labelFor(col, enc, row, {pointPct: 50}, format));
  }
}

function drawStackedBar(enc, view) {
  if (enc === view.stack[0]) view.track.append(renderStack(view.col, view.stack, view.row, view.lo, view.hi, view.format, view.context));
}

const glyphs = {bar: drawBar, points: drawPoints, point: drawPoint, range: drawRange,
  strip: drawStrip, boxplot: drawBoxplot, distribution: drawDistribution, stacked_bar: drawStackedBar};

export function renderGlyph(encoding, view) {
  glyphs[encoding.kind]?.(encoding, view);
}
