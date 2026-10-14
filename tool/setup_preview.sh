#!/usr/bin/env bash
set -euo pipefail

# ---------- preparar galeria web ----------

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# 1. preparar referencias de tres fuentes a partir del checkout oficial
UPSTREAM_FONTS="${1:-$ROOT/../fluentui-system-icons/fonts}"
cd "$ROOT"
if [[ ! -f "$UPSTREAM_FONTS/FluentSystemIcons-Regular.ttf" ]]; then
  echo "Missing Microsoft fonts: $UPSTREAM_FONTS" >&2
  echo "Run: bash tool/setup_preview.sh ../fluentui-system-icons/fonts" >&2
  exit 2
fi
python "$ROOT/tool/build_icon_diagnostics.py" --upstream-fonts "$UPSTREAM_FONTS"
cd "$ROOT/preview"

# 2. crear exclusivamente los archivos de plataforma web
flutter create --platforms=web .

# 3. eliminar el test generado por flutter create si usa la clase MyApp inexistente
if [[ -f test/widget_test.dart ]] && grep -q 'MyApp' test/widget_test.dart; then
  rm test/widget_test.dart
fi

# 4. resolver la dependencia local del paquete
flutter pub get

printf '\nWeb preview is ready. Run:\n'
printf '  cd "%s/preview"\n' "$ROOT"
printf '  flutter run -d chrome\n'
printf '  # Or: flutter run -d web-server --web-port 8080\n'
