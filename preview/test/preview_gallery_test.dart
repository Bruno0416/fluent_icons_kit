import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fluent_icons_preview/main.dart';

void main() {
  // ---------- pruebas de la galeria web ----------

  testWidgets('muestra el buscador y las variantes de iconos', (tester) async {
    // 1. iniciar la galeria
    await tester.pumpWidget(const FluentPreviewApp());

    // 2. comprobar que los controles principales estan disponibles
    expect(find.text('Fluent Icons Kit'), findsOneWidget);
    expect(find.byType(TextField), findsOneWidget);
    expect(find.text('Line'), findsOneWidget);
    expect(find.text('Filled'), findsOneWidget);
    expect(find.text('Compare'), findsOneWidget);
  });

  testWidgets('permite introducir texto de busqueda', (tester) async {
    // 1. iniciar la galeria y escribir una consulta
    await tester.pumpWidget(const FluentPreviewApp());
    await tester.enterText(find.byType(TextField), 'home');
    await tester.pump();

    // 2. conservar el texto introducido en el campo
    expect(tester.widget<TextField>(find.byType(TextField)).controller?.text, 'home');
  });
}
