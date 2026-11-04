#!/bin/bash
# Scarica i dati del Ministero dal Mac e li pubblica su GitHub se sono cambiati.
export PATH="/opt/homebrew/bin:/usr/bin:/bin:$PATH"
cd "$(dirname "$0")" || exit 1
echo "=== $(date '+%d/%m/%Y %H:%M') ==="
python3 build.py || exit 1
git add data.json
if ! git diff --staged --quiet; then
  git commit -q -m "Aggiorna prezzi GPL $(date '+%d/%m/%Y')" && git push -q origin main && echo "Pubblicato."
else
  echo "Nessuna novità."
fi
