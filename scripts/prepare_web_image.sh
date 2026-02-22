#!/usr/bin/env bash
set -euo pipefail

# Prepare a web-friendly image copy for this site (macOS-friendly via `sips`).
# Keeps the original untouched.
#
# Usage:
#   ./scripts/prepare_web_image.sh <input> <output> [max_width] [jpeg_quality]
#
# Example:
#   ./scripts/prepare_web_image.sh ~/Pictures/acadia.jpg \
#     mysite/static/images/travel/pins/acadia-sunrise.jpg 1800 82

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <input> <output> [max_width] [jpeg_quality]" >&2
  exit 1
fi

INPUT="$1"
OUTPUT="$2"
MAX_WIDTH="${3:-1800}"
JPEG_QUALITY="${4:-82}"

if [[ ! -f "$INPUT" ]]; then
  echo "Input file not found: $INPUT" >&2
  exit 1
fi

if ! command -v sips >/dev/null 2>&1; then
  echo "This script requires 'sips' (available on macOS)." >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"

EXTENSION="${OUTPUT##*.}"
EXTENSION_LOWER="$(printf '%s' "$EXTENSION" | tr '[:upper:]' '[:lower:]')"

case "$EXTENSION_LOWER" in
  jpg|jpeg)
    FORMAT="jpeg"
    ;;
  png)
    FORMAT="png"
    ;;
  *)
    echo "Unsupported output extension: .$EXTENSION (use .jpg/.jpeg/.png)" >&2
    exit 1
    ;;
esac

cp "$INPUT" "$OUTPUT"

# Resize only if the image is wider than MAX_WIDTH.
CURRENT_WIDTH="$(sips -g pixelWidth "$OUTPUT" 2>/dev/null | awk '/pixelWidth:/{print $2}')"
if [[ -n "${CURRENT_WIDTH:-}" ]] && [[ "$CURRENT_WIDTH" =~ ^[0-9]+$ ]] && (( CURRENT_WIDTH > MAX_WIDTH )); then
  sips --resampleWidth "$MAX_WIDTH" "$OUTPUT" >/dev/null
fi

# Convert format if needed (based on extension).
sips -s format "$FORMAT" "$OUTPUT" >/dev/null

# JPEG quality tuning (ignored by png).
if [[ "$FORMAT" == "jpeg" ]]; then
  sips -s formatOptions "$JPEG_QUALITY" "$OUTPUT" >/dev/null
fi

FINAL_SIZE_KB="$(du -k "$OUTPUT" | awk '{print $1}')"
echo "Saved: $OUTPUT (${FINAL_SIZE_KB} KB, max width ${MAX_WIDTH}px)"
