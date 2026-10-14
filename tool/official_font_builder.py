#!/usr/bin/env python3
"""Construye fuentes Flutter directamente desde los SVG originales de Microsoft.

Las TTF/JSON oficiales se usan como registro de identificadores y como fuente
para las metricas verticales; no reutilizamos sus contornos reescalados.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from svg_reference import svg_reference_glyph

FONT_FILES = {
    'line': ('FluentSystemIcons-Regular.ttf', 'FluentSystemIcons-Regular.json', 'regular'),
    'filled': ('FluentSystemIcons-Filled.ttf', 'FluentSystemIcons-Filled.json', 'filled'),
}
OUTPUT_FAMILIES = {'line': 'FluentKitLine', 'filled': 'FluentKitFilled'}
FIXED_TIMESTAMP = 3850000000


def upstream_identifier(name: str, size: int, style: str) -> str:
    # Los identificadores Dart pueden tener el prefijo icon_ para palabras reservadas.
    from normalize_icons import DART_RESERVED
    source_name = name[5:] if name.startswith('icon_') and name[5:] in DART_RESERVED else name
    return f'ic_fluent_{source_name}_{size}_{style}'


def read_official(directory: Path, variant: str):
    ttf_name, json_name, _ = FONT_FILES[variant]
    font_path = directory / ttf_name
    mapping_path = directory / json_name
    if not font_path.is_file() or not mapping_path.is_file():
        raise FileNotFoundError(
            f'Faltan archivos oficiales en {directory}: {ttf_name} y {json_name}. '
            'Clona microsoft/fluentui-system-icons y usa --upstream-fonts <repo>/fonts.'
        )
    font = TTFont(str(font_path), recalcTimestamp=False)
    return font, json.loads(mapping_path.read_text(encoding='utf-8'))


def build_from_official(
    variant: str,
    entries: dict,
    mapping: dict,
    output: Path,
    upstream_fonts: Path,
    *,
    diagnostics: list | None = None,
):
    """Crea una TTF con avance uniforme y contornos del viewBox SVG original."""
    original, upstream_codes = read_official(upstream_fonts, variant)
    try:
        _, _, style = FONT_FILES[variant]
        original_cmap = original.getBestCmap()
        em = original['head'].unitsPerEm
        ascent = original['hhea'].ascent
        descent = original['hhea'].descent
        family = OUTPUT_FAMILIES[variant]
        if not 0 < em <= 16384 or ascent <= descent:
            raise ValueError(f'{variant}: metricas de fuente original invalidas')

        glyph_order = ['.notdef']
        empty = TTGlyphPen(None).glyph()
        glyphs = {'.notdef': empty}
        hmtx = {'.notdef': (em, 0)}
        unicode_map = {}
        used_names = set()
        missing = []
        svg_count = 0
        for icon_name, (size, _, svg_data) in sorted(entries.items()):
            key = upstream_identifier(icon_name, size, style)
            source_cp = upstream_codes.get(key)
            source_name = original_cmap.get(source_cp) if source_cp is not None else None
            if source_name is None:
                missing.append(key)
                continue
            if icon_name not in mapping:
                raise ValueError(f'{variant}: codigo Unicode faltante para {icon_name}')
            cp = mapping[icon_name]
            glyph_name = source_name
            if glyph_name in used_names:
                glyph_name = f'kit_{cp:06X}'
            if glyph_name in used_names or glyph_name == '.notdef':
                raise ValueError(f'{variant}: nombre de glifo duplicado: {glyph_name}')
            used_names.add(glyph_name)
            if svg_data:
                glyph = svg_reference_glyph(svg_data, em, ascent)
                advance = em
                svg_count += 1
            else:
                # Compatibilidad con fixtures sin SVG de las pruebas unitarias.
                glyph = copy.deepcopy(original['glyf'][source_name])
                advance, _ = original['hmtx'][source_name]
            if glyph.isComposite():
                glyph.recalcBounds(original['glyf'])
            elif not hasattr(glyph, 'xMin'):
                glyph.recalcBounds(None)
            glyphs[glyph_name] = glyph
            hmtx[glyph_name] = (advance, glyph.xMin)
            glyph_order.append(glyph_name)
            unicode_map[cp] = glyph_name

        if missing:
            raise ValueError(
                f'{variant}: {len(missing)} iconos no coinciden con el catalogo original. '
                'Usa el mismo commit de Microsoft para SVG y TTF/JSON. '
                'Ejemplos: ' + ', '.join(missing[:10])
            )
        if svg_count and svg_count != len(entries):
            raise ValueError(f'{variant}: faltan SVGs: {svg_count}/{len(entries)} reconstruidos')
        if diagnostics is not None:
            diagnostics.clear()

        # FontBuilder evita los glyphOrder y las instrucciones de hinting
        # heredadas que dejan incongruentes algunas TTF oficiales.
        fb = FontBuilder(em, isTTF=True)
        fb.setupGlyphOrder(glyph_order)
        fb.setupCharacterMap(unicode_map)
        fb.setupGlyf(glyphs)
        fb.setupHorizontalMetrics(hmtx)
        fb.setupHorizontalHeader(ascent=ascent, descent=descent)
        fb.setupNameTable({'familyName': family, 'styleName': 'Regular', 'fullName': family,
                           'psName': family})
        fb.setupOS2(sTypoAscender=ascent, sTypoDescender=descent,
                    usWinAscent=max(ascent, em), usWinDescent=max(0, -descent))
        fb.setupPost()
        fb.setupMaxp()
        fb.setupHead(unitsPerEm=em, created=FIXED_TIMESTAMP, modified=FIXED_TIMESTAMP)
        fb.font['head'].flags |= 0x0002
        fb.font.recalcTimestamp = False
        output.parent.mkdir(parents=True, exist_ok=True)
        fb.save(str(output))

        # Validar el archivo fisico, no solo el objeto antes de guardarlo.
        verified = TTFont(str(output))
        try:
            cmap = verified.getBestCmap()
            if set(cmap) != set(unicode_map):
                raise AssertionError(f'{variant}: cmap resultante incorrecto')
            for cp, name in unicode_map.items():
                result_name = cmap[cp]
                glyph = verified['glyf'][result_name]
                width, left_bearing = verified['hmtx'][result_name]
                if left_bearing != glyph.xMin:
                    raise AssertionError(f'{variant}: LSB/xMin incorrecto: {name}')
                if svg_count and width != em:
                    raise AssertionError(f'{variant}: avance inconsistente: {name}')
            if not verified['head'].flags & 0x0002:
                raise AssertionError(f'{variant}: bandera LSB/xMin ausente')
        finally:
            verified.close()
        print(f'{variant}: {svg_count} contornos reconstruidos desde SVG originales')
        return len(unicode_map)
    finally:
        original.close()
