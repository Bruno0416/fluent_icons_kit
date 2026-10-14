import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:fluent_icons_kit/fluent_icons_kit.dart';

part 'icon_diagnostics.g.dart';

// ---------- modelos ----------

class DiagnosticSample {
  const DiagnosticSample({
    required this.name,
    required this.variant,
    required this.svgAsset,
    required this.official,
    required this.kit,
  });

  final String name;
  final String variant;
  final String svgAsset;
  final IconData official;
  final IconData kit;
}

// ---------- laboratorio de fuentes ----------

class IconDiagnosticsPage extends StatefulWidget {
  const IconDiagnosticsPage({super.key});

  @override
  State<IconDiagnosticsPage> createState() => _IconDiagnosticsPageState();
}

class _IconDiagnosticsPageState extends State<IconDiagnosticsPage> {
  double _size = 48;
  bool _showGuides = true;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('Font alignment laboratory')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text(
            'Original SVG vs Microsoft TTF vs Fluent Icons Kit TTF. '
            'All samples share the same 48 × 48 box, visible borders, and no padding '
            'or translation. The official font is loaded unchanged.',
          ),
          const SizedBox(height: 16),
          Wrap(
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 16,
            runSpacing: 8,
            children: [
              Text('Icon size: ${_size.round()} px'),
              SizedBox(
                width: 180,
                child: Slider(
                  min: 16,
                  max: 48,
                  divisions: 8,
                  value: _size,
                  onChanged: (v) => setState(() => _size = v),
                ),
              ),
              FilterChip(
                label: const Text('Center guides'),
                selected: _showGuides,
                onSelected: (v) => setState(() => _showGuides = v),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Row(
            children: [
              SizedBox(width: 166, child: Text('Icon')),
              SizedBox(width: 106, child: Text('Original SVG')),
              SizedBox(width: 106, child: Text('Microsoft TTF')),
              Text('Fluent Kit TTF'),
            ],
          ),
          const Divider(),
          for (final sample in diagnosticSamples)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 9),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    SizedBox(
                      width: 166,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(sample.name, maxLines: 2, overflow: TextOverflow.ellipsis),
                          Text(sample.variant, style: Theme.of(context).textTheme.labelSmall),
                        ],
                      ),
                    ),
                    // ---------- caja real de 48 px, centrada en columnas de 106 px ----------
                    // el Center libera las restricciones horizontales del SizedBox.
                    // sin esto, el AlignmentGuideBox se estira a 106 px.
                    SizedBox(
                      width: 106,
                      child: Center(
                        child: AlignmentGuideBox(
                          showGuides: _showGuides,
                          child: SvgPicture.asset(
                            sample.svgAsset,
                            width: _size,
                            height: _size,
                            colorFilter: ColorFilter.mode(scheme.onSurface, BlendMode.srcIn),
                          ),
                        ),
                      ),
                    ),
                    SizedBox(
                      width: 106,
                      child: Center(
                        child: AlignmentGuideBox(
                          showGuides: _showGuides,
                          child: Icon(sample.official, size: _size, color: scheme.onSurface),
                        ),
                      ),
                    ),
                    SizedBox(
                      width: 106,
                      child: Center(
                        child: AlignmentGuideBox(
                          showGuides: _showGuides,
                          child: Icon(sample.kit, size: _size, color: scheme.onSurface),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          const SizedBox(height: 16),
          Text(
            'Metric details: preview/assets/diagnostics/metrics.json. '
            'Visual differences do not automatically prove incorrect glyph metrics.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}

// ---------- marco de diagnostico reutilizable ----------

/// Dibuja la caja de 48x48 sin modificar la geometria del icono.
class AlignmentGuideBox extends StatelessWidget {
  const AlignmentGuideBox({
    super.key,
    required this.child,
    this.showGuides = true,
  });

  static const double boxSize = 48;

  final Widget child;
  final bool showGuides;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return SizedBox(
      width: boxSize,
      height: boxSize,
      child: Stack(
        fit: StackFit.expand,
        clipBehavior: Clip.none,
        children: [
          Center(child: child),
          IgnorePointer(
            child: CustomPaint(
              painter: _AlignmentGridPainter(
                visible: showGuides,
                outline: colors.outline,
                center: colors.error,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _AlignmentGridPainter extends CustomPainter {
  const _AlignmentGridPainter({
    required this.visible,
    required this.outline,
    required this.center,
  });

  final bool visible;
  final Color outline;
  final Color center;

  @override
  void paint(Canvas canvas, Size size) {
    if (!visible) return;

    final gridPaint = Paint()
      ..color = outline.withValues(alpha: 0.30)
      ..strokeWidth = 0.5;
    final borderPaint = Paint()
      ..color = outline.withValues(alpha: 0.95)
      ..strokeWidth = 1
      ..style = PaintingStyle.stroke;
    final centerPaint = Paint()
      ..color = center.withValues(alpha: 0.9)
      ..strokeWidth = 0.8;

    // ---------- subdivisiones de 12 px ----------
    for (final fraction in <double>[0.25, 0.75]) {
      final x = size.width * fraction;
      final y = size.height * fraction;
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), gridPaint);
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }

    // ---------- ejes del centro exacto ----------
    canvas.drawLine(
      Offset(size.width / 2, 0),
      Offset(size.width / 2, size.height),
      centerPaint,
    );
    canvas.drawLine(
      Offset(0, size.height / 2),
      Offset(size.width, size.height / 2),
      centerPaint,
    );

    // ---------- borde real de la caja ----------
    canvas.drawRect(
      Rect.fromLTWH(0.5, 0.5, size.width - 1, size.height - 1),
      borderPaint,
    );
  }

  @override
  bool shouldRepaint(covariant _AlignmentGridPainter old) =>
      old.visible != visible || old.outline != outline || old.center != center;
}
