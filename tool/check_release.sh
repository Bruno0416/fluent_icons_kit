#!/usr/bin/env bash
set -euo pipefail

# ---------- validacion previa a publicacion ----------
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# 1. preparar la galeria y eliminar pruebas de plantilla obsoletas
bash tool/setup_preview.sh
cd "$ROOT"

# 2. comprobar el paquete principal y los glifos
flutter pub get
flutter analyze
flutter test
python tool/validate.py

# 3. comprobar la galeria web
cd "$ROOT/preview"
flutter analyze
flutter test

# 4. validar la publicacion desde el paquete principal
cd "$ROOT"
dart pub publish --dry-run
