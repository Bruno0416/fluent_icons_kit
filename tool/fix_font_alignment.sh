#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Uso: bash tool/fix_font_alignment.sh /ruta/fluentui-system-icons/fonts [ruta/assets]" >&2
  echo "Clona primero: git clone --depth 1 https://github.com/microsoft/fluentui-system-icons.git" >&2
  exit 2
fi

# 1. reconstruir contornos desde SVG; consultar las TTF para Unicode/metricas
if [[ $# -eq 2 ]]; then
  # fuentes y SVGs del mismo checkout: opcion recomendada para actualizar
  python tool/normalize_icons.py --input "$2" --upstream-fonts "$1"
else
  # reutilizar los SVG normalizados sin cambiar los identificadores
  python tool/normalize_icons.py --input tool/source/svg --upstream-fonts "$1" --no-sources
fi

# 2. validar catalogo y los contornos, bearings y codigo Unicode
python tool/validate.py
python -m unittest discover -s tool -p 'test_font_alignment.py' -v
python -m unittest discover -s tool -p 'test_official_font_builder.py' -v

# 3. emitir el reporte visual sin offsets por nombre de icono
python tool/render_alignment_report.py --output alignment_report.png
