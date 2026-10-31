// Measured pages use record offsets: changing a page's capacity must not move
// its first record. Only visited page boundaries are known, so the expanded
// pager shows the current page and exact record range, not an estimated count.
export class ExpandedPages {
  constructor() { this.reset(); }

  reset() {
    this.pages = [];
    this.current = null;
  }

  project(total, capacity, requestedPage) {
    const size = Math.max(1, Math.floor(Number(capacity) || 10));
    if (!this.pages.length) this.pages.push({start: 0, size});
    const page = Math.max(0, Math.min(requestedPage, this.pages.length - 1));
    const entry = this.pages[page];
    entry.size = size;
    const start = Math.min(entry.start, total);
    const end = Math.min(total, start + size);
    if (this.pages[page + 1]?.start !== end) this.pages.length = page + 1;
    this.current = {page, start, end, total, size};
    return {page, start, end, total, variable: true,
      // This is a navigation bound, never displayed as a total page count.
      pageCount: page + (end < total ? 2 : 1)};
  }

  move(requestedPage) {
    if (!this.current) return null;
    const {page, end, total, size} = this.current;
    if (requestedPage === page + 1 && end < total && !this.pages[requestedPage]) {
      this.pages.push({start: end, size});
    }
    return this.pages[requestedPage] ? {page: requestedPage, size: this.pages[requestedPage].size} : null;
  }
}
