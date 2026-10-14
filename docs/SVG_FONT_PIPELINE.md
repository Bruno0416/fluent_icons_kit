# SVG-first font generation

Fluent Icons Kit preserves the original Microsoft icon designs without applying
manual optical offsets. Each selected SVG determines the glyph's actual outline
and its position in the SVG `viewBox`.

## Sources

- `tool/source/svg/line/` and `tool/source/svg/filled/`: canonical geometry.
- `tool/manifest.json`: selected source size for each icon.
- `tool/codepoints.json`: stable, public Unicode mappings; **never renumber**.
- Microsoft's official `fonts/` TTF/JSON: upstream identifiers, units per em,
  and vertical font metrics. The original TTF glyph outlines are not used.

## Pipeline

1. Resolve the upstream identifier using the icon name, source size and style.
2. Parse SVG paths and the `viewBox`, preserving aspect ratio and converting
   from SVG y-down coordinates to TrueType y-up coordinates.
3. Assign each icon a separate glyph even when multiple upstream names share
   one TTF glyph.
4. Set advance width to one em and left-side bearing to the outline's `xMin`.
5. Build standalone TrueType fonts using `fontTools.fontBuilder.FontBuilder`,
   without inheriting hinting instructions intended for different outlines.
6. Re-open the output fonts and validate Unicode coverage, metrics, and
   glyph-bearing consistency; unit tests also compare every outline against
   the original SVG.

The resulting alignment preserves each SVG's coordinate system; it does **not**
force an icon's optical center of mass to the middle of the box. This distinction
matters for intentionally asymmetric glyphs (e.g., search or checkmarks).

## Rebuild and test

```bash
source .venv/bin/activate
bash tool/fix_font_alignment.sh ../fluentui-system-icons/fonts
```

For a deliberate upstream refresh using the official icons assets from the same
checkout:

```bash
bash tool/fix_font_alignment.sh \
  ../fluentui-system-icons/fonts \
  ../fluentui-system-icons/assets
```

**The second command may update the icon catalog.** Review generated diffs and
avoid inadvertently changing already-published codepoints. The script generates
an `alignment_report.png` to inspect symmetric and asymmetric sample glyphs.
Validate the final render inside Flutter Web's Alignment Lab before releasing.

## Limitations

The current SVG converter supports Fluent's `path` and `rect` geometry. It
represents SVG shapes as monochrome font glyphs, so any alpha differences in a
source SVG cannot be reproduced exactly by a traditional TrueType icon font.
