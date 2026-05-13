#!/bin/bash
PORT=${1:-8080}
DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Klipr landing page → http://localhost:$PORT"
python3 -m http.server "$PORT" --directory "$DIR"
