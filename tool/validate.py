#!/usr/bin/env python3
"""Valida fuentes, identificadores Dart, codepoints y SVGs normalizados."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
except ImportError:
    raise SystemExit('Falta fonttools. Ejecuta: python -m pip install fonttools')

ROOT = Path(__file__).resolve().parent.parent


def main(package: Path):
    # 1. comprobar la paridad entre manifest, codigo dart y fuentes
    manifest = json.loads((package / 'tool/manifest.json').read_text('utf-8'))['icons']
    codepoints = json.loads((package / 'tool/codepoints.json').read_text('utf-8'))
    total = 0
    for variant, font_name in (('line', 'FluentKitLine'), ('filled', 'FluentKitFilled')):
        entries = manifest[variant]
        registry = codepoints[variant]
        font = TTFont(package / 'assets/fonts' / f'{font_name}.ttf')
        cmap = font.getBestCmap()
        dart = (package / 'lib/src/generated' / f'{variant}_icons.g.dart').read_text('utf-8')
        sources = package / 'tool/source/svg' / variant
        assert len(entries) == len(set(entries)), f'Entradas repetidas: {variant}'
        assert all(name in registry for name in entries), f'Faltan codepoints: {variant}'
        assert len(set(registry.values())) == len(registry), f'Codepoints duplicados: {variant}'
        assert set(cmap) == {registry[name] for name in entries}, f'Cmap incorrecto: {variant}'
        assert all(f'get {name} =>' in dart for name in entries), f'Getters faltantes: {variant}'
        assert all(font['glyf'][glyph].numberOfContours > 0 for glyph in cmap.values()), f'Glifos vacios: {variant}'
        if sources.exists():
            actual = {file.stem for file in sources.glob('*.svg')}
            assert actual == set(entries), f'SVG normalizados incorrectos: {variant}'
        for name in entries:
            cp = registry[name]
            assert re.search(rf'get {re.escape(name)} => const IconData\(0x{cp:x},', dart)
        total += len(entries)
        print(f'{variant}: {len(entries)} glifos validados')
    print(f'Correcto: {total} iconos, dos fuentes y API sincronizada')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', type=Path, default=ROOT)
    options = parser.parse_args()
    main(options.package.resolve())
