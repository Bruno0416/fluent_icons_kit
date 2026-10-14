import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'generated_catalog.dart';
import 'icon_diagnostics.dart';

void main() => runApp(const FluentPreviewApp());

enum _PreviewVariant { line, filled, compare }

class FluentPreviewApp extends StatefulWidget {
  const FluentPreviewApp({super.key});

  @override
  State<FluentPreviewApp> createState() => _FluentPreviewAppState();
}

class _FluentPreviewAppState extends State<FluentPreviewApp> {
  ThemeMode _themeMode = ThemeMode.dark;

  @override
  Widget build(BuildContext context) {
    final scheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFFF0335F),
      brightness: Brightness.light,
    );
    final darkScheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFFF0335F),
      brightness: Brightness.dark,
    );

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Fluent Icons Kit',
      themeMode: _themeMode,
      theme: ThemeData(useMaterial3: true, colorScheme: scheme),
      darkTheme: ThemeData(useMaterial3: true, colorScheme: darkScheme),
      home: PreviewHome(
        onToggleTheme: () {
          setState(() {
            _themeMode = _themeMode == ThemeMode.dark
                ? ThemeMode.light
                : ThemeMode.dark;
          });
        },
        isDark: _themeMode == ThemeMode.dark,
      ),
    );
  }
}

class PreviewHome extends StatefulWidget {
  const PreviewHome({
    super.key,
    required this.isDark,
    required this.onToggleTheme,
  });

  final bool isDark;
  final VoidCallback onToggleTheme;

  @override
  State<PreviewHome> createState() => _PreviewHomeState();
}

class _PreviewHomeState extends State<PreviewHome> {
  final TextEditingController _searchController = TextEditingController();
  String _search = '';
  _PreviewVariant _variant = _PreviewVariant.compare;
  double _iconSize = 28;
  bool _showAlignmentGrid = false;

  @override
  void initState() {
    super.initState();
    _searchController.addListener(() {
      if (mounted) {
        setState(() => _search = _searchController.text.trim().toLowerCase());
      }
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  // ---------- detalles ----------

  void _openDetails(PreviewIcon entry) {
    showDialog<void>(
      context: context,
      builder: (dialogContext) {
        final scheme = Theme.of(dialogContext).colorScheme;
        return AlertDialog(
          title: Text(entry.name.replaceAll('_', ' ')),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _iconDetail(entry.line, 'Line', scheme),
                  _iconDetail(entry.filled, 'Filled', scheme),
                ],
              ),
              const SizedBox(height: 24),
              Text(
                'Icon(FluentIcons.line.${entry.name})',
                style: Theme.of(dialogContext).textTheme.bodySmall,
              ),
              const SizedBox(height: 6),
              Text(
                'Icon(FluentIcons.filled.${entry.name})',
                style: Theme.of(dialogContext).textTheme.bodySmall,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Close'),
            ),
            FilledButton.icon(
              onPressed: () async {
                final variant = entry.line != null ? 'line' : 'filled';
                final code = 'Icon(FluentIcons.$variant.${entry.name})';
                await Clipboard.setData(ClipboardData(text: code));
                if (dialogContext.mounted) Navigator.pop(dialogContext);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Copied: $code')),
                  );
                }
              },
              icon: const Icon(Icons.copy_outlined),
              label: const Text('Copy code'),
            ),
          ],
        );
      },
    );
  }

  Widget _iconDetail(IconData? data, String title, ColorScheme scheme) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(data, size: 52, color: scheme.primary),
        const SizedBox(height: 8),
        Text(data == null ? '$title: not available' : title),
      ],
    );
  }

  // ---------- vista del icono ----------

  Widget _galleryGlyph(IconData data, Color color) {
    final icon = Icon(data, size: _iconSize, color: color);
    if (!_showAlignmentGrid) return icon;
    return AlignmentGuideBox(child: icon);
  }

  // ---------- galeria ----------

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final visible = previewIcons.where((entry) {
      if (!entry.name.contains(_search.replaceAll(' ', '_'))) return false;
      switch (_variant) {
        case _PreviewVariant.line:
          return entry.line != null;
        case _PreviewVariant.filled:
          return entry.filled != null;
        case _PreviewVariant.compare:
          return true;
      }
    }).toList(growable: false);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Fluent Icons Kit'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute<void>(builder: (_) => const IconDiagnosticsPage()),
            ),
            child: const Text('Alignment lab'),
          ),
          IconButton(
            tooltip: widget.isDark ? 'Light theme' : 'Dark theme',
            onPressed: widget.onToggleTheme,
            icon: Icon(widget.isDark ? Icons.light_mode_outlined : Icons.dark_mode_outlined),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Available icons: ${visible.length} / ${previewIcons.length}',
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 12),
                TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    labelText: 'Search icons',
                    hintText: 'search, home, video, arrow...',
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: _search.isEmpty
                        ? null
                        : IconButton(
                            onPressed: _searchController.clear,
                            icon: const Icon(Icons.close),
                          ),
                    border: const OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 10),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      ChoiceChip(
                        label: const Text('Line'),
                        selected: _variant == _PreviewVariant.line,
                        onSelected: (_) => setState(() => _variant = _PreviewVariant.line),
                      ),
                      const SizedBox(width: 8),
                      ChoiceChip(
                        label: const Text('Filled'),
                        selected: _variant == _PreviewVariant.filled,
                        onSelected: (_) => setState(() => _variant = _PreviewVariant.filled),
                      ),
                      const SizedBox(width: 8),
                      ChoiceChip(
                        label: const Text('Compare'),
                        selected: _variant == _PreviewVariant.compare,
                        onSelected: (_) => setState(() => _variant = _PreviewVariant.compare),
                      ),
                      const SizedBox(width: 12),
                      Text('${_iconSize.round()} px'),
                      SizedBox(
                        width: 134,
                        child: Slider(
                          value: _iconSize,
                          min: 16,
                          max: 48,
                          divisions: 8,
                          onChanged: (value) => setState(() => _iconSize = value),
                        ),
                      ),
                      const SizedBox(width: 12),
                      FilterChip(
                        label: const Text('48px alignment grid'),
                        selected: _showAlignmentGrid,
                        onSelected: (value) =>
                            setState(() => _showAlignmentGrid = value),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: LayoutBuilder(
              builder: (context, constraints) {
                final columns = (constraints.maxWidth / 158).floor().clamp(2, 10).toInt();
                return GridView.builder(
                  padding: const EdgeInsets.fromLTRB(14, 4, 14, 24),
                  itemCount: visible.length,
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: columns,
                    crossAxisSpacing: 10,
                    mainAxisSpacing: 10,
                    childAspectRatio: _variant == _PreviewVariant.compare ? 1.12 : 1.28,
                  ),
                  itemBuilder: (context, index) {
                    final entry = visible[index];
                    return Card(
                      clipBehavior: Clip.antiAlias,
                      color: scheme.surfaceContainerLow,
                      margin: EdgeInsets.zero,
                      child: InkWell(
                        onTap: () => _openDetails(entry),
                        child: Padding(
                          padding: const EdgeInsets.all(8),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  if (_variant != _PreviewVariant.filled && entry.line != null)
                                    _galleryGlyph(entry.line!, scheme.onSurface),
                                  if (_variant == _PreviewVariant.compare &&
                                      entry.line != null && entry.filled != null)
                                    SizedBox(width: _showAlignmentGrid ? 12 : 18),
                                  if (_variant != _PreviewVariant.line && entry.filled != null)
                                    _galleryGlyph(entry.filled!, scheme.primary),
                                ],
                              ),
                              const SizedBox(height: 12),
                              Text(
                                entry.name,
                                textAlign: TextAlign.center,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: Theme.of(context).textTheme.labelSmall,
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
