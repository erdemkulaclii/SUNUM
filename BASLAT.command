#!/usr/bin/env bash
# Tek komut: sunucu + tarayıcı (tam ekran) + otomatik oynatma. Ek seçenekler: --elle, --pptx, --pdf, --yeniden-uret
set -euo pipefail
cd -- "$(dirname -- "$0")"
exec python3 sunum.py "$@"
