library fluent_icons_kit;

import 'package:flutter/widgets.dart';

part 'src/generated/line_icons.g.dart';
part 'src/generated/filled_icons.g.dart';

// ---------- acceso a iconos ----------

/// Iconos de Fluent UI, disponibles como [IconData] nativo.
///
/// Uso: `Icon(FluentIcons.line.search)` o `Icon(FluentIcons.filled.home)`.
abstract final class FluentIcons {
  const FluentIcons._();

  static const line = _FluentLineIcons();
  static const filled = _FluentFilledIcons();
}
