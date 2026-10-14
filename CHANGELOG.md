# Changelog

All notable changes to Fluent Icons Kit will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this package follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2026-10-13

### Fixed

- Fixed systematic glyph displacement inside Flutter `Icon` widgets by rebuilding both TrueType fonts from the original SVG `viewBox` coordinates, rather than copying outlines with incompatible metrics from upstream font files.
- Corrected horizontal bearings and em-size metrics without introducing icon-specific positional offsets.

### Changed

- Regenerated all **2,930 Line** and **2,969 Filled** glyphs from their selected Microsoft Fluent UI System Icons SVG designs, preserving the previously published icon names and Unicode codepoints.
- Kept Microsoft's original font files and JSON maps as references for identifiers and vertical metrics; the generated glyph outlines now come directly from SVG.

### Added

- Regression tests for font geometry, glyph bearings, Unicode coverage, and SVG-outline fidelity across all **5,899 icons**.
- A developer-only web alignment grid and a three-way comparison of SVG, original Microsoft TTF, and Fluent Icons Kit TTF.
- Documentation for rebuilding fonts from canonical SVG sources.

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