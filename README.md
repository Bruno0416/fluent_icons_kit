# Fluent Icons Kit

A simpler way to use Microsoft's [Fluent UI System Icons](https://github.com/microsoft/fluentui-system-icons) in Flutter. The kit provides the complete available **Line (Regular)** and **Filled** icon sets through a clean `FluentIcons.line.name` / `FluentIcons.filled.name` API, without embedding pixel sizes in icon identifiers.

Choose the display size with Flutter's `Icon(size: ...)` instead of choosing a separate icon constant for every size. Icons are native `IconData` values, with no SVG rendering dependency.

## Features

- **5,899 glyphs:** 2,930 Line and 2,969 Filled icons.
- Two bundled TrueType fonts, with one chosen design size per icon and style. The generator prefers the 24 px artwork and falls back to the closest available size.
- Native `IconData` values and a concise `FluentIcons.line.name` / `FluentIcons.filled.name` API.
- Automatic Flutter font registration and support for icon color, size, and inherited icon themes.
- An interactive **web-only preview** with search, light/dark themes, size controls, and Line/Filled comparison.
- A reproducible Python source-normalization pipeline with stable Unicode assignments for future upstream updates.

> **Attribution:** The original icon artwork belongs to Microsoft and is distributed under the MIT license. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [LICENSE](LICENSE).

## Installation

Once published to pub.dev:

```sh
flutter pub add fluent_icons_kit
```

To use a local checkout during development:

```yaml
dependencies:
  fluent_icons_kit:
    path: ../fluent_icons_kit
```

## Usage

```dart
import 'package:flutter/material.dart';
import 'package:fluent_icons_kit/fluent_icons_kit.dart';

Icon(FluentIcons.line.search, size: 24);
Icon(FluentIcons.filled.home, color: Colors.pink);

IconButton(
  icon: Icon(FluentIcons.line.settings),
  onPressed: () {},
);

Icon(
  selected ? FluentIcons.filled.heart : FluentIcons.line.heart,
);
```

These values are `IconData`, not SVG widgets. `line` maps to the upstream *Regular* icon style; `filled` maps to *Filled*.

Every exported icon has one source design per style; this does **not** imply every glyph was originally designed at 24 px. Some icons do not have both variants. You can set `Icon(size: ...)` freely, as with other icon fonts.

## Web preview

The gallery lives in [`preview/`](https://github.com/Bruno4016/fluent_icons_kit/tree/main/preview), and is intentionally web-only.

```sh
# From the package root:
bash tool/setup_preview.sh
cd preview
flutter run -d chrome
```

For Firefox or another browser, start Flutter's web server and open the local URL:

```sh
cd preview
flutter run -d web-server --web-port 8080
# Open http://localhost:8080
```

See [preview/README.md](https://github.com/Bruno4016/fluent_icons_kit/blob/main/preview/README.md) for gallery features and local cleanup instructions.

## Updating the icons from Microsoft

The GitHub repository retains **one normalized SVG per icon/style** under `tool/source/svg/` to document how the font was built. The published pub.dev package excludes these intermediate SVGs; only the packaged TTF fonts are required to render icons.

Install Python dependencies **from the package root**:

```sh
python -m pip install -r tool/requirements.txt
```

Get the official upstream assets (skip this step if you already have them):

```sh
git clone --depth 1 https://github.com/microsoft/fluentui-system-icons.git ../fluentui-system-icons
```

Then regenerate and verify:

```sh
python tool/normalize_icons.py --input ../fluentui-system-icons/assets
python tool/validate.py
```

The `--input` parameter must refer to an **existing** upstream `assets` directory or to a ZIP archive containing the official assets. Do not copy example paths literally. The generator also updates the web preview's catalog when present.

**Important:** Keep `tool/codepoints.json` in source control. It reserves assigned codepoints so updates do not renumber previously published icons. Inspect generated diffs before releasing a new version.

## Technical notes

- Fonts are registered with `fontPackage: 'fluent_icons_kit'`, so application projects do not need to register these TTFs manually.
- Shape outlines are converted to monochrome TTF glyphs; partial opacity and multicolor variants are not preserved.
- Icons marked as mirrored in the upstream metadata use `matchTextDirection: true` for RTL layouts.
- Font tree-shaking in **release builds** has not yet been confirmed for the nested `FluentIcons.line.*`/`filled.*` accessors. Measure a release build before relying on reduced font size.

## Development and publishing

Run all publication checks from the **package root**, never from `preview/`:

```sh
# From the root of your fluent_icons_kit checkout:
bash tool/check_release.sh
```

This verifies the library, the 5,899 glyphs, and the web gallery, then executes `dart pub publish --dry-run` **from the package root**. To run the commands separately:

```sh
# Package root: fluent_icons_kit/
flutter pub get
flutter analyze
flutter test
python tool/validate.py

# Web preview: fluent_icons_kit/preview/
bash tool/setup_preview.sh
cd preview
flutter analyze
flutter test

# Return to the package root before checking publication
cd ..
dart pub publish --dry-run
```

`preview/` is an unpublished local application (`publish_to: none`). Do **not** run `dart pub publish` there: its path dependency and exclusion from the package make publication validation fail. The preview setup script removes the obsolete `MyApp` widget test generated by `flutter create`, while keeping the real gallery tests.

Flutter may report newer versions of SDK-pinned transitive dependencies during `pub get`; those informational messages are not analysis or test failures. Do not override Flutter SDK dependency constraints just to silence them.

The package targets Dart `^3.13.4` and Flutter `>=3.47.0` as declared in its [pubspec.yaml](pubspec.yaml). Review the dry-run file list and warnings before using `dart pub publish` once the GitHub repository is available.

Source code: <https://github.com/Bruno4016/fluent_icons_kit>
Issues: <https://github.com/Bruno4016/fluent_icons_kit/issues>

## License

MIT. See [LICENSE](LICENSE) for this package and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for Microsoft artwork attribution.
