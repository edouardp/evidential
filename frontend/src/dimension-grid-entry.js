/* global EVIDENTIAL_GRID_CSS */
import grid from "./dimension-grid.js";
import {widgetSurface} from "./widget-surface.js";

export default {
  render({el, model}) {
    const surface = widgetSurface(el, EVIDENTIAL_GRID_CSS, model);
    const dispose = grid.render({el: surface.mount, model});
    return () => { dispose(); surface.destroy(); };
  },
};
