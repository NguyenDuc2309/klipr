#!/usr/bin/env bash
PORT=${1:-8080}
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "----------------------------------------"
echo "  Klipr Landing Page Local Server"
echo "  → URL: http://localhost:$PORT"
echo "----------------------------------------"

python3 -m http.server "$PORT" --directory "$DIR"
