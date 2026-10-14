#!/usr/bin/env bash
set -euo pipefail

# ---------- validacion previa a publicacion ----------
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# 0. impedir publicar una version sin entrada equivalente en CHANGELOG
VERSION="$(sed -n 's/^version: //p' pubspec.yaml | head -n 1)"
if [[ -z "$VERSION" ]] || ! grep -Fq "## [$VERSION] - " CHANGELOG.md; then
  echo "ERROR: pubspec.yaml y CHANGELOG.md no coinciden ($VERSION)" >&2
  exit 1
fi

# 1. preparar la galeria y eliminar pruebas de plantilla obsoletas
bash tool/setup_preview.sh
cd "$ROOT"

# 2. comprobar el paquete principal y los glifos
flutter pub get
flutter analyze
flutter test
python tool/validate.py
python -m unittest discover -s tool -p 'test_font_alignment.py' -v
python -m unittest discover -s tool -p 'test_official_font_builder.py' -v
python -m unittest discover -s tool -p 'test_icon_diagnostics.py' -v

# 3. comprobar la galeria web
cd "$ROOT/preview"
flutter analyze
flutter test

# 4. validar la publicacion desde el paquete principal
cd "$ROOT"
dart pub publish --dry-run
