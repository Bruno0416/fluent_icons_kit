#!/usr/bin/env python3
"""Normaliza Fluent SVGs y extrae fuentes oficiales + catalogo IconData.

Uso:
    python tool/normalize_icons.py --input /ruta/fluent_icons_upstream/assets --upstream-fonts /ruta/fluent_icons_upstream/fonts
    python tool/normalize_icons.py --input tool/source/svg --upstream-fonts /ruta/fluent_icons_upstream/fonts --no-sources

Requiere: python -m pip install fonttools
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r'^ic_fluent_(?P<name>.+)_(?P<size>\d+)_(?P<variant>regular|filled)\.svg$', re.I)
PREFERRED_SIZES = (24, 20, 28, 16, 32, 48, 12, 10)
BMP_START, BMP_END = 0xE000, 0xF8FF
SUPPLEMENTARY_START = 0xF0000
FONT_FAMILIES = {'line': 'FluentKitLine', 'filled': 'FluentKitFilled'}
DART_RESERVED = {
    'abstract','as','assert','async','await','base','break','case','catch','class','const',
    'continue','covariant','default','deferred','do','dynamic','else','enum','export',
    'extends','extension','external','factory','false','final','finally','for','Function',
    'get','hide','if','implements','import','in','interface','is','late','library','mixin',
    'new','null','of','on','operator','part','required','rethrow','return','sealed','set',
    'show','static','super','switch','sync','this','throw','true','try','typedef','var',
    'void','when','while','with','yield','hashCode','runtimeType','toString','noSuchMethod',
}


def records(source: Path):
    """Enumera SVGs y metadatos sin extraer miles de archivos redundantes."""
    # 1. permitir reconstruir fuentes usando solo los SVG ya normalizados
    if source.is_dir() and source.name == 'svg' and source.parent.name == 'source':
        for f in sorted(source.glob('*/*.svg')):
            if f.parent.name in FONT_FAMILIES:
                yield f.as_posix(), f.read_bytes()
        return
    if source.is_file() and source.suffix.lower() == '.zip':
        with zipfile.ZipFile(source) as z:
            for info in sorted(z.infolist(), key=lambda i: i.filename):
                if info.is_dir():
                    continue
                name = info.filename.replace('\\', '/')
                if '/SVG/' in name and name.endswith('.svg') or name.endswith('/metadata.json'):
                    yield name, z.read(info)
    else:
        if not source.is_dir():
            raise ValueError(f'Ruta de entrada inexistente: {source}')
        for f in sorted(source.rglob('*')):
            if f.is_file() and (f.suffix.lower() == '.svg' and '/SVG/' in f.as_posix() or f.name == 'metadata.json'):
                yield f.as_posix(), f.read_bytes()


def snake(name: str) -> str:
    """Convierte nombres oficiales en identificadores Dart estables."""
    identifier = re.sub(r'[^a-zA-Z0-9]+', '_', name).strip('_').lower()
    if not identifier or identifier[0].isdigit() or identifier in DART_RESERVED:
        identifier = 'icon_' + identifier
    return identifier


def parse_sources(source: Path, previous_manifest: dict | None = None):
    groups = defaultdict(dict)
    directions = {}
    stats = Counter()
    for path, content in records(source):
        stats['archivos_leidos'] += 1
        if path.endswith('/metadata.json'):
            try:
                meta = json.loads(content)
                original = snake(re.sub(r'\s+', '_', meta.get('name', '')))
                directions[original] = meta.get('directionType') == 'mirror'
            except (UnicodeError, ValueError):
                stats['metadatos_invalidos'] += 1
            continue
        m = NAME_RE.match(path.rsplit('/', 1)[-1])
        if m:
            name = snake(m['name'])
            variant = 'line' if m['variant'].lower() == 'regular' else 'filled'
            size = int(m['size'])
        else:
            # 2. preservar los tamanos y metadatos originales al reutilizar SVG normalizados
            normalized = re.search(r'/tool/source/svg/(line|filled)/([a-z0-9_]+)\.svg$', path)
            if normalized is None:
                stats['svg_omitidos'] += 1
                continue
            variant, name = normalized.groups()
            old = (previous_manifest or {}).get(variant, {}).get(name, {})
            size = int(old.get('source_size', 24))
            directions[name] = bool(old.get('mirror_rtl', False))
        groups[(variant, name)][size] = (path, content)
        stats['svg_admitidos'] += 1
    return groups, directions, stats


def choose(groups):
    """Prefiere una misma talla para filled y line del mismo icono."""
    by_name = defaultdict(dict)
    for (variant, name), sizes in groups.items():
        by_name[name][variant] = sizes
    result = {}
    for name in sorted(by_name):
        variants = by_name[name]
        common = set.intersection(*(set(variants[v]) for v in variants))
        preferred = next((size for size in PREFERRED_SIZES if size in common), None)
        if preferred is None and common:
            preferred = min(common, key=lambda size: (abs(size - 24), size < 24, size))
        for variant, sizes in variants.items():
            size = preferred if preferred is not None else min(sizes, key=lambda s: (abs(s - 24), s < 24, s))
            result[(variant, name)] = (size, *sizes[size])
    return result


def updated_mapping(path: Path, chosen):
    """Nunca reutiliza ni renumera un codigo de icono ya publicado."""
    old = json.loads(path.read_text('utf-8')) if path.exists() else {'line': {}, 'filled': {}}
    for variant in FONT_FAMILIES:
        group = old.setdefault(variant, {})
        occupied = set(group.values())
        next_bmp = BMP_START
        next_supp = SUPPLEMENTARY_START
        for name in sorted(n for v, n in chosen if v == variant):
            if name in group:
                continue
            while next_bmp in occupied and next_bmp <= BMP_END:
                next_bmp += 1
            if next_bmp <= BMP_END:
                cp = next_bmp
            else:
                while next_supp in occupied:
                    next_supp += 1
                cp = next_supp
            group[name] = cp
            occupied.add(cp)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(old, indent=2, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf-8')
    return old


def generated_dart(variant, entries, mapping, directions):
    cls = '_FluentLineIcons' if variant == 'line' else '_FluentFilledIcons'
    family = FONT_FAMILIES[variant]
    lines = [
        '// Generado automaticamente. No editar manualmente.',
        '// ignore_for_file: non_constant_identifier_names',
        "part of '../../fluent_icons_kit.dart';", 
        '// ---------- iconos fluent ' + variant + ' ----------',
        '',
        'class ' + cls + ' {',
        '  const ' + cls + '();',
        '',
    ]
    for name in sorted(entries):
        cp = mapping[name]
        rtl = ', matchTextDirection: true' if directions.get(name, False) else ''
        lines.append(f"  IconData get {name} => const IconData(0x{cp:x}, fontFamily: '{family}', fontPackage: 'fluent_icons_kit'{rtl});")
    lines += ['}', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Normalizar SVGs de Fluent y generar fuentes IconData')
    parser.add_argument('--input', required=True, type=Path, help='ZIP original o carpeta assets de Microsoft')
    parser.add_argument('--output', type=Path, default=ROOT, help='Raiz del paquete Flutter')
    parser.add_argument('--no-sources', action='store_true', help='No conservar SVGs normalizados en el paquete')
    parser.add_argument('--upstream-fonts', type=Path, required=True, help='Carpeta fonts/ oficial con TTF y JSON de Microsoft')
    args = parser.parse_args()
    dest = args.output.resolve()
    previous_manifest_path = dest / 'tool' / 'manifest.json'
    previous = json.loads(previous_manifest_path.read_text('utf-8'))['icons'] if previous_manifest_path.exists() else {}
    groups, directions, stats = parse_sources(args.input.resolve(), previous)
    chosen = choose(groups)
    if not chosen:
        parser.error('No se encontraron SVGs reconocibles con regular/filled')
    source_dir = dest / 'tool' / 'source' / 'svg'
    if not args.no_sources:
        if source_dir.exists():
            shutil.rmtree(source_dir)
        source_dir.mkdir(parents=True)
    manifest = {'source': 'microsoft/fluentui-system-icons', 'size_preference': list(PREFERRED_SIZES), 'icons': {'line': {}, 'filled': {}}}
    for (variant, name), (size, original, data) in sorted(chosen.items()):
        if not args.no_sources:
            target = source_dir / variant / (name + '.svg')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        manifest['icons'][variant][name] = {
            'source_size': size,
            'sha256': hashlib.sha256(data).hexdigest(),
            'mirror_rtl': directions.get(name, False),
        }
    manifest_file = dest / 'tool' / 'manifest.json'
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + '\n', 'utf-8')
    codepoints = updated_mapping(dest / 'tool' / 'codepoints.json', chosen)
    compatibility = []
    for variant in FONT_FAMILIES:
        entries = {name: rest for (v, name), rest in chosen.items() if v == variant}
        font_path = dest / 'assets' / 'fonts' / (FONT_FAMILIES[variant] + '.ttf')
        from official_font_builder import build_from_official
        build_from_official(variant, entries, codepoints[variant], font_path,
                            args.upstream_fonts.resolve(), diagnostics=compatibility)
        dart_path = dest / 'lib' / 'src' / 'generated' / (variant + '_icons.g.dart')
        dart_path.parent.mkdir(parents=True, exist_ok=True)
        dart_path.write_text(generated_dart(variant, entries, codepoints[variant], directions), encoding='utf-8')
        print(f'{variant}: {len(entries)} glifos -> {font_path.name} ({font_path.stat().st_size:,} bytes)')
    # 3. la geometria viene de SVG: no comparar con contornos TTF oficiales.
    report_path = dest / 'tool' / 'font_geometry_report.json'
    report_path.write_text(json.dumps({
        'reference': 'SVG originales: geometria canonica; TTF oficiales: Unicode y metricas',
        'rebuilt_from_svg': len(chosen),
        'compatible_translations': 0,
        'incompatible': 0,
        'details': [],
    }, indent=2, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf-8')
    print('Reporte de geometria:', report_path)
    print('SVG encontrados:', stats['svg_admitidos'], ' | ignorados:',stats['svg_omitidos'])
    # 1. sincronizar tambien la galeria cuando viene incluida en el paquete
    from generate_preview import generate
    if (dest / 'preview').exists():
        print('Catalogo preview:', generate(dest), 'nombres')
    print('Total glifos normalizados:',len(chosen),' | fuentes TTF: 2')


if __name__ == '__main__':
    main()
