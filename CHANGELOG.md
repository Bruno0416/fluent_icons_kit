# Changelog

All notable changes to Fluent Icons Kit will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this package follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-10-13

### Fixed

- Corrected the GitHub repository, homepage, and issue tracker URLs.

## [0.1.0] - 2026-10-13

### Added

- Initial Flutter icon font package with **2,930 Line** and **2,969 Filled** glyphs from Microsoft Fluent UI System Icons.
- Native `IconData` API via `FluentIcons.line.*` and `FluentIcons.filled.*`, simplifying upstream size-specific icon identifiers.
- Two bundled TTF fonts with Flutter font package registration.
- Python tooling to select one SVG design per icon and variant, normalize it, generate fonts, and regenerate Dart catalogs.
- Stable codepoint mapping and source manifest for repeatable upstream updates.
- Web-only Flutter preview featuring icon search, theme switching, variant comparison, and size adjustment.
- Automated font and generated catalog validation scripts.
- MIT licensing and attribution notices for the upstream Microsoft artwork.