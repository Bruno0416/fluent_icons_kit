import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fluent_icons_kit/fluent_icons_kit.dart';

void main() {
  group('catalogo fluent', () {
    test('ambas variantes exponen icon data con la familia correcta', () {
      final line = FluentIcons.line.home;
      final filled = FluentIcons.filled.home;
      expect(line, isA<IconData>());
      expect(filled, isA<IconData>());
      expect(line.fontFamily, 'FluentKitLine');
      expect(filled.fontFamily, 'FluentKitFilled');
      expect(line.fontPackage, 'fluent_icons_kit');
      expect(filled.fontPackage, 'fluent_icons_kit');
    });

    test('las variantes y los iconos tienen códigos validos', () {
      expect(FluentIcons.line.search.codePoint, greaterThanOrEqualTo(0xe000));
      expect(FluentIcons.filled.search.codePoint, greaterThanOrEqualTo(0xe000));
      expect(FluentIcons.line.home, isNot(FluentIcons.line.search));
    });
  });
}
