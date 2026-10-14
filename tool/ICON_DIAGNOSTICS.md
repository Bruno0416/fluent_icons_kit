# Icon rendering diagnostics

This is a **diagnostic**, not a font fix. It compares seven icon names in both Line and Filled variations.

Three renderers are shown side by side inside identical 48 × 48 boxes:

- **Original SVG:** the normalized local SVG, whose SHA-256 must match `tool/manifest.json`, rendered by `flutter_svg`.
- **Microsoft TTF:** the exact official Microsoft font file, copied byte-for-byte; the codepoint is looked up using Microsoft's JSON map and the selected `source_size` from our manifest.
- **Fluent Kit TTF:** the current package font using the already-published `FluentIcons.line.*` or `FluentIcons.filled.*` accessor.

No font coordinates, bearings, outlines, SVG paths, or public icon codepoints are changed.

## Run

Install Python tooling from the root package:

```bash
python -m pip install -r tool/requirements.txt
bash tool/setup_preview.sh ../fluentui-system-icons/fonts
cd preview
flutter run -d web-server --web-port 8080
```

Open **Alignment lab** in the app bar. Toggle the center guides and compare Heart, Checkmark, Search, Add, Chevron Down, Dismiss, and Access Time. You can also change the displayed icon size without changing the box.

To run only the Python checks:

```bash
cd ..
python -m unittest discover -s tool -p 'test_icon_diagnostics.py' -v
```

The machine-readable metrics are generated at `preview/assets/diagnostics/metrics.json` and contain `advance_width`, `left_bearing`, `units_per_em`, ascent/descent and bounding boxes for each source. These values can explain some differences, but they **do not determine perceptual/optical centering by themselves**.

**Important:** The diagnostic copies Microsoft's complete original TTFs only to a local preview folder. Do not publish them as assets of the main package or commit the generated resources accidentally. Add these lines to your local Git exclude configuration if needed:

```text
preview/assets/diagnostics/
preview/lib/icon_diagnostics.g.dart
```

For a local-only exclude without editing project `.gitignore`:

```bash
printf '\npreview/assets/diagnostics/\npreview/lib/icon_diagnostics.g.dart\n' >> .git/info/exclude
```

`flutter_svg` is a **preview-only** dependency. The `fluent_icons_kit` package keeps its native `IconData` API with no runtime SVG dependency.
