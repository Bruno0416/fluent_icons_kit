import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:fluent_icons_kit/fluent_icons_kit.dart';
import 'package:fluent_icons_preview/icon_diagnostics.dart';

void main() {
  testWidgets('diagnostic screen contains all three rendering paths', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: IconDiagnosticsPage()));

    expect(find.text('Original SVG'), findsOneWidget);
    expect(find.text('Microsoft TTF'), findsOneWidget);
    expect(find.text('Fluent Kit TTF'), findsOneWidget);
    expect(find.byType(SvgPicture), findsWidgets);
    final guides = find.byType(AlignmentGuideBox);
    expect(guides, findsAtLeastNWidgets(3));

    // ---------- validar cada fuente, no el ancho de su columna ----------
    for (var i = 0; i < 3; i++) {
      expect(tester.getSize(guides.at(i)), const Size(48, 48));
    }

    // el svg y ambas fuentes deben estar centrados en su respectiva caja.
    final svg = find.descendant(of: guides.at(0), matching: find.byType(SvgPicture));
    expect(tester.getCenter(svg), tester.getCenter(guides.at(0)));

    for (var i = 1; i < 3; i++) {
      final icon = find.descendant(of: guides.at(i), matching: find.byType(Icon));
      expect(tester.getSize(icon), const Size(48, 48));
      expect(tester.getCenter(icon), tester.getCenter(guides.at(i)));
    }

    expect(find.byIcon(FluentIcons.line.heart), findsOneWidget);
  });
}
