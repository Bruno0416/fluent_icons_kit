#!/usr/bin/env bash
set -euo pipefail

# ---------- preparar galeria web ----------

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/preview"

# 1. crear exclusivamente los archivos de plataforma web
flutter create --platforms=web .

# 2. eliminar el test generado por flutter create si usa la clase MyApp inexistente
if [[ -f test/widget_test.dart ]] && grep -q 'MyApp' test/widget_test.dart; then
  rm test/widget_test.dart
fi

# 3. resolver la dependencia local del paquete
flutter pub get

printf '\nWeb preview is ready. Run:\n'
printf '  cd "%s/preview"\n' "$ROOT"
printf '  flutter run -d chrome\n'
printf '  # Or: flutter run -d web-server --web-port 8080\n'
