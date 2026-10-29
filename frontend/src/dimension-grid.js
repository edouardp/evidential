import { h } from "./dom.js";
import { formatTitle, formatValue } from "./format.js";

export const ROW_HEIGHT = 20;
const OVERSCAN = 4;
const key = value => JSON.stringify(value);
const label = value => value === null ? "(Missing)" : String(value);

/** A bounded window, rather than thousands of off-screen category buttons. */
export function windowRange(length, scrollTop, height) {
  const start = Math.max(0, Math.floor(scrollTop / ROW_HEIGHT) - OVERSCAN);
  return [Math.min(start, length), Math.min(length, start + Math.ceil(height / ROW_HEIGHT) + 2 * OVERSCAN)];
}

export default {
  render({ model, el }) {
    const options = model.get("options");
    const columns = new Map();
    const root = h("section", { class: "edg-root", "aria-label": options.title || "Dimension filters" });
    root.style.setProperty("--edg-color", options.color);
    root.style.setProperty("--edg-height", `${options.height}px`);
    root.style.setProperty("--edg-width", `${options.dimension_width}px`);
    root.style.setProperty("--edg-row-height", `${ROW_HEIGHT}px`);
    const titles = h("div", { class: "edg-titles" });
    if (options.title) titles.append(h("h3", { class: "edg-title" }, options.title));
    if (options.subtitle) titles.append(h("p", { class: "edg-subtitle" }, options.subtitle));
    const track = h("div", { class: "edg-track", tabindex: "0", "aria-label": "Scrollable dimensions" });
    const previous = h("button", { type: "button", "aria-label": "Previous dimensions" }, "←");
    const next = h("button", { type: "button", "aria-label": "Next dimensions" }, "→");
    const reset = h("button", { type: "button", class: "edg-reset" }, "Clear selections");
    const nav = h("div", { class: "edg-nav" }, [reset, previous, next]);
    root.append(h("div", { class: "edg-toolbar" }, [titles, nav]), track);
    el.append(root);

    function navigation() {
      const overflow = track.scrollWidth > track.clientWidth + 1;
      previous.hidden = next.hidden = !overflow;
      previous.disabled = track.scrollLeft < 1;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 1;
      reset.disabled = !Object.keys(model.get("selected") || {}).length;
    }
    function move(direction) {
      track.scrollBy({ left: direction * Math.max(options.dimension_width, track.clientWidth * 0.8), behavior: "smooth" });
    }
    previous.onclick = () => move(-1);
    next.onclick = () => move(1);
    track.addEventListener("scroll", navigation);
    function select(name, value) {
      const selected = { ...(model.get("selected") || {}) };
      const values = selected[name] || [];
      const exists = values.some(item => key(item) === key(value));
      const updated = exists ? values.filter(item => key(item) !== key(value)) : options.multiple ? [...values, value] : [value];
      if (updated.length) selected[name] = updated;
      else delete selected[name];
      model.set("selected", selected);
      model.save_changes();
    }
    reset.onclick = () => { model.set("selected", {}); model.save_changes(); };

    function createColumn(facet) {
      const title = facet.title || formatTitle(facet.name);
      const heading = h("span", { class: "edg-heading" }, title);
      const search = h("input", { type: "search", class: "edg-search", "aria-label": `Search ${title}`, placeholder: title, hidden: true });
      const toggle = h("button", { type: "button", class: "edg-search-toggle", "aria-label": `Search ${title}`, "aria-expanded": "false" }, "⌕");
      const header = h("div", { class: "edg-header" }, [heading, search, toggle]);
      const viewport = h("div", { class: "edg-list", role: "group", "aria-label": `${title} categories`, tabindex: "0" });
      const content = h("div", { class: "edg-content" });
      viewport.append(content);
      const status = h("div", { class: "edg-status", "aria-live": "polite" });
      const column = h("section", { class: "edg-dimension", "aria-label": title }, [header, viewport, status]);
      track.append(column);
      const state = { facet, title, column, heading, search, toggle, viewport, content, status, query: "", items: [], selected: new Set(), maximum: 1 };
      function close() {
        search.hidden = true;
        heading.hidden = false;
        toggle.textContent = "⌕";
        toggle.classList.toggle("edg-filtered", Boolean(state.query));
        toggle.setAttribute("aria-label", `${state.query ? "Edit search" : "Search"} ${title}${state.query ? `: ${search.value}` : ""}`);
        toggle.setAttribute("aria-expanded", "false");
      }
      toggle.addEventListener("mousedown", event => event.preventDefault());
      toggle.onclick = () => {
        if (!search.hidden) {
          search.value = "";
          state.query = "";
          close();
          updateColumn(state);
          toggle.focus();
        } else {
          heading.hidden = true;
          search.hidden = false;
          toggle.textContent = "×";
          toggle.setAttribute("aria-label", `Clear search ${title}`);
          toggle.setAttribute("aria-expanded", "true");
          search.focus();
          search.select();
        }
      };
      search.addEventListener("blur", close);
      search.addEventListener("keydown", event => {
        if (event.key === "Escape" || event.key === "Enter") { close(); toggle.focus(); }
      });
      search.addEventListener("input", () => {
        state.query = search.value.trim().toLocaleLowerCase();
        viewport.scrollTop = 0;
        updateColumn(state);
      });
      viewport.addEventListener("scroll", () => drawWindow(state));
      viewport.addEventListener("keydown", event => {
        const index = Number(document.activeElement?.dataset.index ?? -1);
        let target;
        if (event.key === "ArrowDown") target = Math.min(state.items.length - 1, index + 1);
        if (event.key === "ArrowUp") target = Math.max(0, index - 1);
        if (event.key === "Home") target = 0;
        if (event.key === "End") target = state.items.length - 1;
        if (target === undefined || target < 0) return;
        event.preventDefault();
        viewport.scrollTop = target * ROW_HEIGHT;
        drawWindow(state);
        content.querySelector(`[data-index="${target}"]`)?.focus({ preventScroll: true });
      });
      return state;
    }

    function rowButton(state, item, selected, index) {
      const metric = item.metric;
      const full = metric === null ? "Unavailable for these selections" : new Intl.NumberFormat("en", { maximumFractionDigits: 20 }).format(metric);
      const button = h("button", {
        type: "button", class: "edg-row", "aria-pressed": String(selected),
        tabindex: selected ? "0" : "-1",
        "aria-label": `${state.title}: ${label(item.value)}, ${full}`,
        title: `${label(item.value)}: ${full}`,
        dataset: { key: key(item.value), index },
      }, [
        h("span", { class: "edg-bar", "aria-hidden": "true", style: { width: `${Math.abs(metric || 0) / state.maximum * 100}%` } }),
        h("span", { class: "edg-category" }, label(item.value)),
        h("span", { class: "edg-value" }, metric === null ? "—" : formatValue(metric, options.format)),
      ]);
      button.onclick = () => {
        select(state.facet.name, item.value);
        // Rendering replaces the row buttons. Keep focus on the same category.
        [...state.column.querySelectorAll(".edg-row")].find(row => row.dataset.key === key(item.value))?.focus({ preventScroll: true });
      };
      return button;
    }

    function drawWindow(state) {
      const { viewport, content, items } = state;
      const [start, end] = windowRange(items.length, viewport.scrollTop, viewport.clientHeight || options.height);
      const focusKey = content.contains(document.activeElement) ? document.activeElement.dataset.key : null;
      content.style.paddingTop = `${start * ROW_HEIGHT}px`;
      content.style.paddingBottom = `${(items.length - end) * ROW_HEIGHT}px`;
      content.replaceChildren(...items.slice(start, end).map((item, offset) => rowButton(state, item, state.selected.has(key(item.value)), start + offset)));
      if (!items.length) content.append(h("div", { class: "edg-empty" }, "No matching categories"));
      if (focusKey !== null) [...content.children].find(row => row.dataset.key === focusKey)?.focus({ preventScroll: true });
    }

    function updateColumn(state) {
      const selected = new Set((model.get("selected")?.[state.facet.name] || []).map(key));
      state.selected = selected;
      state.maximum = state.facet.items.reduce((maximum, item) => Math.max(maximum, Math.abs(item.metric || 0)), 1e-30);
      let matches = 0;
      state.items = state.facet.items.filter(item => {
        const match = label(item.value).toLocaleLowerCase().includes(state.query);
        if (match) matches++;
        return match || selected.has(key(item.value));
      });
      state.status.textContent = `${matches.toLocaleString("en")} ${state.query ? "matching" : "available"}${selected.size ? ` · ${selected.size} selected` : ""}`;
      state.viewport.scrollTop = Math.min(state.viewport.scrollTop, Math.max(0, state.items.length * ROW_HEIGHT - (state.viewport.clientHeight || options.height)));
      drawWindow(state);
    }

    function update() {
      const focused = document.activeElement;
      const focusedColumn = [...columns.values()].find(state => state.column.contains(focused));
      const focusKey = focused?.dataset.key;
      for (const facet of model.get("facets") || []) {
        let state = columns.get(facet.name);
        if (!state) { state = createColumn(facet); columns.set(facet.name, state); }
        state.facet = facet;
        updateColumn(state);
      }
      if (focusedColumn && focusKey !== undefined) {
        [...focusedColumn.column.querySelectorAll(".edg-row")].find(row => row.dataset.key === focusKey)?.focus({ preventScroll: true });
      }
      navigation();
    }
    model.on("change:facets", update);
    model.on("change:selected", update);
    const resize = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(() => {
      navigation();
      for (const state of columns.values()) drawWindow(state);
    });
    resize?.observe(track);
    update();
    return () => {
      model.off("change:facets", update);
      model.off("change:selected", update);
      resize?.disconnect();
      root.remove();
    };
  },
};
