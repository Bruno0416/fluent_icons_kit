#!/usr/bin/env python3
"""Regenera el catalogo Dart para la galeria desde manifest.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def generate(package: Path) -> int:
    manifest = json.loads((package / 'tool' / 'manifest.json').read_text('utf-8'))
    icons = manifest['icons']
    names = sorted(set(icons['line']) | set(icons['filled']))
    lines = [
        '// Generado automaticamente. No editar manualmente.',
        '// ---------- catalogo de la galeria ----------',
        '',
        "import 'package:flutter/widgets.dart';",
        "import 'package:fluent_icons_kit/fluent_icons_kit.dart';",
        '',
        'class PreviewIcon {',
        '  const PreviewIcon(this.name, {this.line, this.filled});',
        '  final String name;',
        '  final IconData? line;',
        '  final IconData? filled;',
        '}',
        '',
        'final List<PreviewIcon> previewIcons = [',
    ]
    for name in names:
        args = [f'{v}: FluentIcons.{v}.{name}' for v in ('line', 'filled') if name in icons[v]]
        lines.append(f"  PreviewIcon('{name}', {', '.join(args)}),")
    lines += ['];', '']
    dest = package / 'preview' / 'lib' / 'generated_catalog.dart'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text('\n'.join(lines), encoding='utf-8')
    return len(names)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Genera catalogo de galeria Flutter')
    parser.add_argument('--package', type=Path, default=ROOT)
    args = parser.parse_args()
    print(f'Catalogo preview: {generate(args.package.resolve())} nombres')
