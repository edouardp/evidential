#!/usr/bin/env bash
# Capture frontend/preview.html to a PNG using a headless Chromium browser.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-8765}"
HOST="${HOST:-127.0.0.1}"
OUT="${OUT:-/tmp/evidential_preview.png}"

find_browser() {
  for candidate in \
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium" \
    "$(command -v chromium || true)" \
    "$(command -v chromium-browser || true)" \
    "$(command -v google-chrome || true)"; do
    if [ -n "${candidate}" ] && [ -x "${candidate}" ]; then
      echo "${candidate}"
      return 0
    fi
  done
  return 1
}

if ! BROWSER="$(find_browser)"; then
  echo "error: no Chromium-based browser found (Edge/Chrome/Chromium)." >&2
  exit 1
fi

cd "${ROOT}"
python3 -m http.server "${PORT}" --bind "${HOST}" >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill "${SERVER_PID}" 2>/dev/null || true' EXIT
sleep 1

"${BROWSER}" \
  --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --window-size=1280,1100 \
  --screenshot="${OUT}" \
  "http://${HOST}:${PORT}/frontend/preview.html" >/dev/null 2>&1 || true

sleep 1
if [ -f "${OUT}" ]; then
  echo "Wrote ${OUT}"
else
  echo "error: screenshot was not produced" >&2
  exit 1
fi
