# Fluent Icons Kit — Web Preview

A browser-based Flutter gallery for browsing all Line and Filled icons, searching names, comparing styles, changing icon size, switching light/dark themes, and copying Dart icon references.

## Run locally

From the package root:

```sh
bash tool/setup_preview.sh ../fluentui-system-icons/fonts
cd preview
flutter run -d chrome
```

If you prefer Firefox, or do not have Chrome set up as a Flutter target:

```sh
cd preview
flutter run -d web-server --web-port 8080
```

Open <http://localhost:8080> in your browser. You can also run `flutter run -d web-server --web-port 8080` from inside `preview/` after dependencies are installed.

## Alignment diagnostics

The **48px alignment grid** in the gallery overlays the icon box and center guides on both Line and Filled variants. The **Alignment Lab** compares original SVG, Microsoft's unmodified TTF, and the rebuilt Kit TTF at the same size. Both help identify baseline issues without modifying the artwork.

`tool/setup_preview.sh` generates the diagnostic references using `../fluentui-system-icons/fonts` by default (or a directory passed as its first argument). Clone [Microsoft Fluent UI System Icons](https://github.com/microsoft/fluentui-system-icons) alongside this repository before setting up the preview. Generated reference TTFs and SVGs under `preview/assets/diagnostics/` are local developer assets, not published package contents.

## Web-only structure

The preview intentionally uses only `preview/web/` and does **not** require Android, iOS, or desktop hosts. If an older preview was generated with Android support, remove the unused folder from the package root:

```sh
rm -rf preview/android
```

`tool/setup_preview.sh` only generates web host files and will not recreate Android. The root `.gitignore` prevents accidental commits of generated non-web platform folders.

## Run the preview tests

The gallery includes its own widget tests. From the package root:

```sh
bash tool/setup_preview.sh ../fluentui-system-icons/fonts
cd preview
flutter analyze
flutter test
```

`flutter create` may generate a stale `test/widget_test.dart` referring to `MyApp`, which does not exist in the preview. `tool/setup_preview.sh` removes that template test and preserves the actual gallery tests. The preview is **not** intended for publication; return to the package root for `dart pub publish --dry-run`.

## Using the package

```dart
import 'package:fluent_icons_kit/fluent_icons_kit.dart';

Icon(FluentIcons.line.search);
Icon(FluentIcons.filled.home);
```

The gallery intentionally references the entire catalog for searching. This is not representative of how much font data a production app that uses only a subset of icons will retain. Verify font tree-shaking in a release build.
