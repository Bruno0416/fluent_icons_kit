#!/usr/bin/env python3
"""Prepara una comparacion Flutter de SVG, TTF oficial y TTF del kit.

No modifica las fuentes publicables ni las coordenadas de los glifos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from fontTools.ttLib import TTFont

from official_font_builder import FONT_FILES, upstream_identifier

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ('add', 'heart', 'checkmark', 'search', 'chevron_down', 'dismiss', 'access_time')
FAMILIES = {'line': ('FluentOfficialLine', 'FluentKitLine'),
            'filled': ('FluentOfficialFilled', 'FluentKitFilled')}


def _metrics(font: TTFont, cp: int) -> dict:
    cmap = font.getBestCmap() or {}
    glyph_name = cmap.get(cp)
    if not glyph_name:
        raise ValueError(f'Glifo Unicode U+{cp:04X} ausente en la fuente')
    glyph = font['glyf'][glyph_name]
    bounds = [getattr(glyph, k) for k in ('xMin', 'yMin', 'xMax', 'yMax')]
    return {
        'codepoint': cp,
        'glyph_name': glyph_name,
        'bounds': bounds,
        'advance_width': font['hmtx'][glyph_name][0],
        'left_bearing': font['hmtx'][glyph_name][1],
        'units_per_em': font['head'].unitsPerEm,
        'ascent': font['hhea'].ascent,
        'descent': font['hhea'].descent,
    }


def prepare(upstream_fonts: Path, *, root: Path = ROOT, names: tuple[str, ...] = SAMPLES) -> list[dict]:
    """Genera assets de diagnostico sin alterar el paquete principal."""
    upstream_fonts = upstream_fonts.resolve()
    manifest = json.loads((root / 'tool/manifest.json').read_text(encoding='utf-8'))['icons']
    published = json.loads((root / 'tool/codepoints.json').read_text(encoding='utf-8'))
    assets = root / 'preview/assets/diagnostics'
    assets.mkdir(parents=True, exist_ok=True)
    rows = []
    dart = [
        '// Generated diagnostic references. Do not edit.',
        "part of 'icon_diagnostics.dart';",
        '',
        'final diagnosticSamples = <DiagnosticSample>[',
    ]
    for variant in ('line', 'filled'):
        ttf, mapping_file, style = FONT_FILES[variant]
        official_family, kit_family = FAMILIES[variant]
        font_path = upstream_fonts / ttf
        mapping_path = upstream_fonts / mapping_file
        if not font_path.is_file() or not mapping_path.is_file():
            raise FileNotFoundError(f'Faltan las fuentes oficiales: {font_path} / {mapping_path}')
        official_map = json.loads(mapping_path.read_text(encoding='utf-8'))
        reference_font = TTFont(font_path, recalcTimestamp=False)
        kit_font = TTFont(root / 'assets/fonts' / f'{kit_family}.ttf', recalcTimestamp=False)
        try:
            # La fuente original se copia sin subsetting ni conversion para mantener
            # sus metricas exactamente como las publica Microsoft.
            font_output = assets / 'fonts' / ttf
            font_output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(font_path, font_output)
            for name in names:
                record = manifest[variant].get(name)
                if record is None or name not in published[variant]:
                    raise ValueError(f'{variant}/{name}: icono ausente del catalogo local')
                size = record['source_size']
                key = upstream_identifier(name, size, style)
                official_cp = official_map.get(key)
                if official_cp is None:
                    raise ValueError(f'{variant}/{name}: el JSON oficial no tiene {key}')
                kit_cp = published[variant][name]
                svg_path = root / 'tool/source/svg' / variant / f'{name}.svg'
                if not svg_path.is_file():
                    raise FileNotFoundError(svg_path)
                contents = svg_path.read_bytes()
                if hashlib.sha256(contents).hexdigest() != record['sha256']:
                    raise ValueError(f'{variant}/{name}: el SVG no coincide con manifest.json')
                dest_svg = assets / 'svg' / variant / f'{name}.svg'
                dest_svg.parent.mkdir(parents=True, exist_ok=True)
                dest_svg.write_bytes(contents)
                official_metrics = _metrics(reference_font, official_cp)
                kit_metrics = _metrics(kit_font, kit_cp)
                rows.append({
                    'variant': variant,
                    'name': name,
                    'source_size': size,
                    'svg_sha256': hashlib.sha256(contents).hexdigest(),
                    'upstream_identifier': key,
                    'official': official_metrics,
                    'kit': kit_metrics,
                })
                dart.extend([
                    '  DiagnosticSample(',
                    f"    name: '{name}', variant: '{variant}',",
                    f"    svgAsset: 'assets/diagnostics/svg/{variant}/{name}.svg',",
                    f"    official: const IconData(0x{official_cp:X}, fontFamily: '{official_family}'),",
                    f'    kit: FluentIcons.{variant}.{name},',
                    '  ),',
                ])
        finally:
            reference_font.close()
            kit_font.close()
    dart.extend(['];', ''])
    (root / 'preview/lib/icon_diagnostics.g.dart').write_text('\n'.join(dart), encoding='utf-8')
    (assets / 'metrics.json').write_text(json.dumps({
        'purpose': 'Diagnostic only; no changes to published fonts',
        'source': str(upstream_fonts),
        'samples': rows,
    }, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description='Prepare a triple-rendering font comparison for Flutter Web')
    parser.add_argument('--upstream-fonts', type=Path, required=True,
                        help='Microsoft fluentui-system-icons/fonts directory')
    args = parser.parse_args()
    rows = prepare(args.upstream_fonts)
    print(f'Icon diagnostic: {len(rows)} samples prepared (SVG, original TTF, kit TTF).')
    print('View: preview/lib/icon_diagnostics.dart (button in preview app bar).')
    print('Metrics: preview/assets/diagnostics/metrics.json')


if __name__ == '__main__':
    main()
