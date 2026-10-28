import { h } from "./dom.js";
import { formatValue } from "./format.js";
import { formattedText } from "./formatted-text.js";
import { resolveColor } from "./color.js";
import { markColor, pointSeries } from "./mark-series.js";
import { numeric, observationValue } from "./mark-data.js";
import { renderDensityBand, readDensity } from "./density-band.js";
import { inspectable, inspectionData } from "./tooltips.js";
import { markTooltip, observationTooltip, tooltipText, tooltipValue, seriesName } from "./tooltip-data.js";
import { markLabelText, renderMarkLabel, autoLabelColor, labelTextStyle } from "./mark-labels.js";

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
      const width = Math.max(0, at(Number(end)) - left);
      const segment = h("div", {
        class: "et-strip-run",
        style: { left: `${left}%`, width: `${width}%`, backgroundColor: colourOf(named(item)) },
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
  if (range?.shared) return {lo: range.min, hi: range.max, span: (range.max - range.min) || 1, transform: scale.transform};
  let lo = scale.domain && scale.domain[0] != null ? Number(scale.domain[0]) : (range?.min ?? 0);
  let hi = scale.domain && scale.domain[1] != null ? Number(scale.domain[1]) : (range?.max ?? 1);
  const hasBar = (col.encodings || []).some((enc) => enc.kind === "bar" || enc.kind === "stacked_bar");
  const bars = (col.encodings || []).filter(enc => enc.kind === "bar");
  const fitToData = bars.length > 0 && bars.every(enc => enc.fit_to_data) && !(col.encodings || []).some(enc => enc.kind === "stacked_bar");
  if (scale.include_zero !== false && hasBar && !fitToData && scale.transform !== "log") {
    if (scale.domain?.[0] == null) lo = Math.min(0, lo);
    if (scale.domain?.[1] == null) hi = Math.max(0, hi);
  }
  // Two-sided layouts accept a 0..magnitude domain or an explicit symmetric
  // signed domain. Their axes, references and overlay points use signed x.
  if ((col.encodings || []).some(enc => enc.center || enc.side || enc.diverge_at) && (!scale.domain || lo >= 0)) {
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

/** Log decades/endpoints are labeled; subdivisions reveal logarithmic spacing. */
export function axisTicks(lo, hi, count = 4, transform = null) {
  if (transform !== "log") return niceTicks(lo, hi, count, transform).map(value => ({value, major: true}));
  if (!(lo > 0) || !Number.isFinite(hi) || hi <= lo) return [];
  const ticks = new Map([[lo, {value: lo, major: true}], [hi, {value: hi, major: true}]]);
  for (let exponent = Math.floor(Math.log10(lo)); exponent <= Math.ceil(Math.log10(hi)); exponent++) {
    for (let multiple = 1; multiple <= 9; multiple++) {
      const value = Number((multiple * Math.pow(10, exponent)).toPrecision(12));
      if (value >= lo && value <= hi && !ticks.has(value)) ticks.set(value, {value, major: multiple === 1});
    }
  }
  return [...ticks.values()].sort((a, b) => a.value - b.value);
}

/** A position function mapping a value in ``lo..hi`` to 0..100 (percent). */
export function scalePosition(lo, hi, transform, reverse = false) {
  const position = markScale(lo, hi, transform);
  return value => {
    const pct = position(value);
    return pct == null ? null : reverse ? 100 - pct : pct;
  };
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

export function renderMarks(col, row, range, format, context = {}) {
  const labelFor = (column, enc, record, geometry, formatter) => inspectable(
    renderMarkLabel(column, enc, record, geometry, formatter), markTooltip(column, enc, record, {context}),
    {priority: 1, navigate: false});
  const encodings = col.encodings || [];
  const scale = col.scale || {};
  const {lo, hi, span} = marksDomain(col, range);
  const reverse = encodings.some(enc => enc.kind === "bar" && enc.direction === "left");
  const pos = scalePosition(lo, hi, scale.transform, reverse);
  const clampPos = (value) => {
    const pct = pos(value);
    return pct == null ? null : Math.max(0, Math.min(100, pct));
  };
  const track = h("div", { class: "et-marks" });
  track.setAttribute("role", "img");
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
  const barReferences = encodings.filter(enc => enc.kind === "bar" && enc.reference != null)
    .map(enc => ({value: enc.reference, color: enc.reference_color, label: enc.reference_label}));
  const hasCenter = encodings.some(enc => enc.center);
  const references = [...(hasCenter ? [{value: 0}] : []), ...(col.references || []), ...barReferences];
  const referenceBands = document.createDocumentFragment();
  for (const ref of references) {
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
      referenceBands.append(
        h("div", {
          class: "et-mark-band",
          style: {
            left: `${left}%`,
            width: `${right - left}%`,
            backgroundColor: resolveColor(ref.color),
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

  // Bands form the background; even opaque fills must leave guides visible.
  track.prepend(referenceBands);
  const barCount = encodings.filter((enc) => enc.kind === "bar").length;
  const stack = encodings.filter((enc) => enc.kind === "stacked_bar");
  let barIndex = 0;
  for (const enc of encodings) {
    if (enc.kind === "stacked_bar") {
      if (enc === stack[0]) track.append(renderStack(col, stack, row, lo, hi, format, context));
      continue;
    }
    if (enc.kind === "boxplot") {
      track.append(renderBox(col, enc, row, clampPos, context));
      const median = clampPos(row[enc.source]);
      if (enc.label && median != null) track.append(labelFor(col, enc, row, {pointPct: median}, format));
      continue;
    }
    if (enc.kind === "distribution") {
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
    } else if (enc.kind === "points") {
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
    } else if (enc.kind === "point") {
      const pct = clampPos(value);
      if (pct == null) continue;
      const size = enc.size != null ? Number(enc.size) : 7;
      track.append(
        inspectable(h("div", {
          class: "et-mark et-mark-point",
          style: { ...verticalStyle(enc.valign, true), ...pointOutlineStyle(enc.outline), left: `${pct}%`, width: `${size}px`, height: `${size}px`, backgroundColor: markColor(enc, row, "var(--et-accent, #2563eb)") },
        }), markTooltip(col, enc, row, {context}), {priority: 3}),
      );
      if (enc.label) track.append(labelFor(col, enc, row, { pointPct: pct }, format));
    } else if (enc.kind === "strip") {
      track.append(renderStrip(enc, row, lo, span, col, context));
      if (enc.label) track.append(labelFor(col, enc, row, {pointPct: 50}, format));
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
      const direction = rangeDirection(enc, start, end, color);
      if (direction) line.append(direction);
      track.append(inspectable(line, markTooltip(col, enc, row, {context})));
      if (enc.label) track.append(labelFor(col, enc, row, { pointPct: left }, format));
    }
  }
  if (!track.querySelector(".et-mark, .et-mark-strip, .et-density-band")) {
    track.append(h("span", {class: "et-null"}, String(col.null_text ?? (format ? format(null) : "–"))));
  }
  const description = [...new Set([...track.querySelectorAll("[data-et-tooltip]:not([data-mark-label])")]
    .map(node => tooltipText(inspectionData(node))))].join("\n");
  track.setAttribute("aria-label", description || "No observations");
  return track;
}

export function renderBar(col, value, formatted, range, row) {
  const opts = col.bar_options || {};
  const num = Number(value);
  const min = range?.shared || opts.fit_to_data ? (range?.min ?? 0) : Math.min(0, range?.min ?? 0);
  const max = range?.shared || opts.fit_to_data ? (range?.max ?? 0) : Math.max(0, range?.max ?? 0);
  const negative = num < 0;
  // A leftward bar fills from the right edge — the mirror of the default, for a
  // back-to-back ("tornado") league table.
  const leftward = opts.direction === "left";
  // A per-row colour column (`bar(color="@column")`) wins over a fixed colour.
  const rowColor =
    opts.bar_color_column && row ? resolveColor(row[opts.bar_color_column]) : null;
  const color = negative
    ? (resolveColor(row?.[opts.bar_color_negative_column]) || rowColor || resolveColor(opts.bar_color_negative) || resolveColor(opts.bar_color) || "var(--et-negative, #dc2626)")
    : (rowColor || resolveColor(opts.bar_color) || "var(--et-accent, #2563eb)");
  const label = h(
    "span",
    { class: `et-bar-label${opts.hide_labels ? " et-hidden" : ""}` },
    formattedText(formatted),
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
