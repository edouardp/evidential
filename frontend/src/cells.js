import { alignStyle, h, optString, inlineMarkdown, withFigure } from "./dom.js";
import { formatValue } from "./format.js";
import { withDecimals, indentForCell } from "./rows.js";
import { calculateColorStyles, contrastTextColor } from "./color.js";
import { renderBar, renderDelta, renderSparkline } from "./visualizations.js";

/** Return the first matching substitution text, or null. */
export function matchSubstitution(col, row, value, options) {
  const rules = options.rules;
  if (!rules) return null;
  for (const rule of rules) {
    if (rule.type !== "substitute") continue;
    if (rule.columns !== "*" && !rule.columns.includes(col.name)) continue;
    if (rule.rows && !rule.rows.includes(row.__row_id)) continue;
    if (rule.kind === "missing") {
      if (value === null || value === undefined) return rule.text;
      continue;
    }
    if (value === null || value === undefined) continue;
    if (rule.kind === "zero" && Number(value) === 0) return rule.text;
    if (rule.kind === "values" && (rule.values || []).includes(value)) return rule.text;
    if (!isNaN(Number(value))) {
      const numeric = Number(value);
      if (rule.kind === "small" && numeric < rule.threshold) return rule.text;
      if (rule.kind === "large" && numeric > rule.threshold) return rule.text;
    }
  }
  return null;
}

/** Merge matching format/style rules in order; later rules win. */
export function matchingRules(col, row, options) {
  const rules = options.rules;
  if (!rules || !rules.length) return { fmt: null, style: null };
  let fmt = null;
  let style = null;
  for (const rule of rules) {
    if (rule.columns !== "*" && !rule.columns.includes(col.name)) continue;
    if (rule.rows && !rule.rows.includes(row.__row_id)) continue;
    if (rule.fmt != null) fmt = rule.fmt;
    if (rule.style) style = { ...(style || {}), ...rule.style };
  }
  return { fmt, style };
}

/** Apply effects shared by ordinary, null, substituted and template cells. */
export function decorateCell(td, col, row, ctx, rowIndex, style, includeFootnote, options) {
  if (col.font_color) td.style.color = col.font_color;
  if (col.font_weight) td.style.fontWeight = col.font_weight;
  if (col.font_style) td.style.fontStyle = col.font_style;
  const footnoteColumn = col.footnote || options.footnote_column;
  if (includeFootnote && footnoteColumn && row[footnoteColumn]) {
    const noteText = String(row[footnoteColumn]).trim();
    if (noteText) {
      let note = ctx.footnotes.find((item) => item.text === noteText);
      if (!note) {
        note = { text: noteText, index: ctx.footnotes.length + 1, rows: new Set() };
        ctx.footnotes.push(note);
      }
      note.rows.add((ctx.rowNumberBase || 0) + rowIndex + 1);
      td.append(
        h("sup", { class: "et-footnote-mark", title: noteText,
          "data-footnote-index": note.index }),
      );
    }
  }
  if (style) {
    for (const [property, propertyValue] of Object.entries(style)) {
      td.style.setProperty(property, propertyValue);
    }
  }
}

export function renderCell({row, col, index, ctx, rowIndex, options: opts, toggleGroup, isCollapsed, rowColorStyles}) {
  const isTotal = row.render_type === "row_total";
  const isSubtotal = row.render_type === "row_subtotal";
  const hidden = row.__hide_cell || {};
  const tdStyle = withFigure(alignStyle(col), col, opts);
  // In accordion mode, indent dimension cells so children read as nested.
  const indent = ctx.accordion ? indentForCell(row, index, ctx) : 0;
  if (indent > 0) {
    const base = index === 0 && !ctx.rowNumbers ? "0.25rem" : "0.375rem";
    tdStyle.paddingLeft = `calc(${base} + ${indent}rem)`;
  }
  const td = h("td", { class: `et-td${opts.stub === col.name ? " et-stub" : ""}`, style: tdStyle });
  const matched = matchingRules(col, row, opts);
  const finish = (includeFootnote = true) => {
    decorateCell(td, col, row, ctx, rowIndex, matched.style, includeFootnote, opts);
    return td;
  };
  if (ctx.section && index < ctx.dimCount) {
    // Section mode merges each dimension cell vertically. A data row renders
    // only its leaf dimension (the rest sit under ancestor rowSpans); a
    // subtotal renders its own dimension cell; the total renders the first.
    // Columns to the *right* of that cell are not covered by any rowSpan,
    // so they must still occupy their place — blank — or the measure cells
    // slide one column early.
    const dimIndex = isTotal
      ? 0
      : isSubtotal
        ? (row.__level ?? ctx.dimCount) - 1
        : ctx.dimCount - 1;
    if (index === dimIndex) {
      if (isSubtotal) td.rowSpan = ctx.rowspans?.[rowIndex] ?? 1;
    } else if (index > dimIndex) {
      return finish(false);
    } else {
      return null;
    }
  }
  if (rowColorStyles) {
    td.style.backgroundColor = rowColorStyles.backgroundColor;
    td.style.color = rowColorStyles.color;
  }
  // A column highlight is a vertical band: it wins over row colours.
  if (col.highlight) td.style.backgroundColor = col.highlight;
  if (col.viz_include_subtotals === false && isSubtotal && col.viz) td.classList.add("et-no-viz");

  // Collapsible chevron in the subtotal's own dimension column.
  const dimIndex = (row.__level ?? 0) - 1;
  if (isSubtotal && index === dimIndex && !ctx.section) {
    const chev = h("button", {
      class: `et-chevron${isCollapsed ? "" : " et-chevron-open"}`,
      type: "button", "aria-label": `Toggle group ${row[col.name] ?? ""}`,
      "aria-expanded": String(!isCollapsed),
      onclick: (event) => {
        event.stopPropagation();
        toggleGroup(row.__group_key, true);
      },
    }, "▶");
    td.append(chev);
    td.dataset.groupKey = row.__group_key;
    td.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleGroup(row.__group_key, false);
    });
  }

  if (hidden[col.name]) {
    return finish(false);
  }

  // Data-driven column merge / template (e.g. "10–20", "5 ± 0.2").
  if (col.template) {
    const merged = String(col.template).replace(/\{(\w+)\}/g, (_, field) => {
      const fieldValue = row[field];
      if (fieldValue === null || fieldValue === undefined) return "";
      const fieldFormat = (col.template_fmt || {})[field];
      return formatValue(fieldValue, fieldFormat, {
        type: col.type,
        fallback: optString(fieldValue),
      });
    });
    td.append(h("span", { class: "et-cell-value" }, merged));
    return finish();
  }

  let value = row[col.name];
  const substituted = matchSubstitution(col, row, value, opts);
  if (substituted != null) {
    td.append(h("span", { class: "et-cell-value et-substituted" }, substituted));
    return finish();
  }
  // Optional cutoffs: values outside the range are treated as blank.
  if (
    value !== null &&
    value !== undefined &&
    (typeof value === "number" ||
      (typeof value === "string" && value.trim() !== "" && !isNaN(Number(value))))
  ) {
    const numeric = Number(value);
    if (col.blank_below != null && numeric < col.blank_below) value = null;
    if (col.blank_above != null && numeric > col.blank_above) value = null;
  }
  if (value === null || value === undefined) {
    // A missing delta reads as the same neutral dash as a value inside
    // `neutral_range`; other columns use the generic null text.
    if (col.viz === "delta") {
      td.append(renderDelta(col, value));
    } else {
      const nullText = col.null_text ?? opts.null_text ?? "–";
      td.append(h("span", { class: "et-null" }, String(nullText)));
    }
    return finish();
  }

  const baseFormat =
    col.fmt_column && row[col.fmt_column] != null ? String(row[col.fmt_column]) : col.fmt;
  const alignDecimals =
    (col.align_decimals ?? opts.align_decimals) && ctx.decimals.has(col.name);
  const alignedBase = alignDecimals
    ? withDecimals(baseFormat || "num", ctx.decimals.get(col.name))
    : baseFormat;
  const formatCode =
    matched.fmt != null
      ? matched.fmt
      : isTotal && col.total_fmt
        ? col.total_fmt
        : isSubtotal && col.subtotal_fmt
          ? col.subtotal_fmt
          : alignedBase;
  const formatted = formatValue(value, formatCode, {
    type: col.type,
    range: ctx.formatRanges.get(col.name),
    fallback: optString(value),
    relative: col.relative,
  });

  // Conditional color background.
  let vizStyles = null;
  if (col.viz === "color" && !(isTotal) && !(isSubtotal && col.viz_include_subtotals === false)) {
    const range = ctx.ranges.get(col.name);
    // `conditional_colors` needs no numeric range (the hex column may be
    // the only colour source, e.g. a text status column).
    if (range || (col.color_options || {}).conditional_colors) {
      vizStyles = calculateColorStyles(col, row, range || { min: 0, max: 0 }, ctx.colorScales.get(col.name));
    }
  }

  const negative =
    (col.red_negatives || col.negative_color) && !isNaN(Number(value)) && Number(value) < 0;
  // Accounting-style brackets replace the sign: -$1,234 -> ($1,234).
  const display =
    negative && col.bracket_negatives ? `(${String(formatted).replace(/^-/, "")})` : formatted;

  const content = renderContent(col, value, display, ctx, row);

  if (negative) {
    content.classList?.add("et-negative");
    if (col.negative_color) content.style.color = col.negative_color;
  }

  const link = col.link ? row[col.link] : null;
  if (link && row.render_type !== "row_total") {
    td.append(h("a", {
      class: "et-cell-link", href: String(link),
      target: col.link_new_tab ? "_blank" : null,
      rel: col.link_new_tab ? "noopener noreferrer" : null,
    }, col.link_label ? col.link_label : content));
  } else {
    td.append(content);
  }

  if (vizStyles) {
    td.style.backgroundColor = vizStyles.backgroundColor;
    td.style.color = vizStyles.color;
    td.classList.add("et-color-cell");
  }

  return finish();
}

function renderContent(col, value, formatted, ctx, row) {
  const isSubtotal = row.render_type === "row_subtotal";
  let content;
  if (col.viz === "bar" && !(isSubtotal && col.viz_include_subtotals === false) && row.render_type !== "row_total") {
    content = renderBar(col, value, formatted, ctx.ranges.get(col.name));
  } else if (col.viz === "delta") {
    content = renderDelta(col, value);
  } else if (col.viz === "sparkline") {
    content = renderSparkline(col, value);
  } else if (col.html) {
    content = h("span", { html: String(value) });
  } else if (col.markdown) {
    content = h("span", { class: "et-cell-value" });
    content.append(inlineMarkdown(String(value)));
  } else if (col.logo && row[col.logo]) {
    const domain = String(row[col.logo]);
    const logoOptions = col.logo_options || {};
    content = h("span", { class: "et-cell-media" }, [
      h("img", {
        class: "et-cell-logo",
        src: `https://img.logo.dev/${encodeURIComponent(domain)}`,
        alt: domain,
        loading: "lazy",
        style: logoOptions.height ? { height: `${logoOptions.height}px` } : {},
      }),
      h("span", { class: "et-cell-media-label" }, formatted),
    ]);
  } else if (col.image && row[col.image]) {
    const imageOptions = col.image_options || {};
    content = h("span", { class: "et-cell-media" }, [
      h("img", {
        class: "et-cell-image",
        src: String(row[col.image]),
        alt: String(imageOptions.alt || ""),
        style: {
          ...(imageOptions.height ? { height: `${imageOptions.height}px` } : {}),
          ...(imageOptions.width ? { width: `${imageOptions.width}px` } : {}),
        },
      }),
      h("span", { class: "et-cell-media-label" }, formatted),
    ]);
  } else if (col.viz === "chip") {
    const chipRange = ctx.ranges.get(col.name);
    const chipStyles =
      chipRange || (col.color_options || {}).conditional_colors
        ? calculateColorStyles(col, row, chipRange || { min: 0, max: 0 }, ctx.colorScales.get(col.name))
        : null;
    const chip = h("span", { class: "et-chip" }, formatted);
    // An optional minimum width; the chip still grows for wider content.
    const minWidth = (col.chip_options || {}).min_width;
    if (minWidth != null) {
      chip.style.minWidth = typeof minWidth === "number" ? `${minWidth}px` : String(minWidth);
    }
    if (chipStyles) {
      chip.style.backgroundColor = chipStyles.backgroundColor;
      chip.style.color = contrastTextColor(chipStyles.backgroundColor);
    }
    content = chip;
  } else {
    content = h("span", { class: "et-cell-value" }, formatted);
  }

  return content;
}
