#!/usr/bin/env python3
"""Calcula los limites de un SVG Fluent dentro del em-square de Microsoft.

La referencia es el viewBox original, no el centro de masa de los pixeles.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path


def svg_reference_glyph(content: bytes, units_per_em: int, ascent: int):
    """Convierte los contornos SVG en un glifo temporal para comparar su geometria."""
    root = ET.fromstring(content)
    box = root.attrib.get('viewBox')
    if not box:
        raise ValueError('SVG sin viewBox')
    x0, y0, w, h = map(float, re.split(r'[\s,]+', box.strip()))
    if w <= 0 or h <= 0:
        raise ValueError(f'viewBox invalido: {box}')
    scale = units_per_em / max(w, h)
    dx = (units_per_em - w * scale) / 2 - x0 * scale
    dy = ascent + y0 * scale
    base = TTGlyphPen(None)
    pen = TransformPen(Cu2QuPen(base, max_err=1.0, reverse_direction=False),
                       (scale, 0, 0, -scale, dx, dy))
    ns = '{http://www.w3.org/2000/svg}'
    for element in root.iter():
        tag = element.tag.removeprefix(ns)
        if tag == 'path' and element.attrib.get('d'):
            parse_path(element.attrib['d'], pen)
        elif tag == 'rect':
            x = float(element.attrib.get('x', 0))
            y = float(element.attrib.get('y', 0))
            rw, rh = float(element.attrib['width']), float(element.attrib['height'])
            parse_path(f'M{x} {y}h{rw}v{rh}h{-rw}Z', pen)
        elif tag not in ('svg', 'g', 'title', 'desc'):
            raise ValueError(f'Elemento SVG no soportado: {tag}')
    glyph = base.glyph()
    if glyph.numberOfContours <= 0:
        raise ValueError('SVG sin contornos')
    glyph.recalcBounds(None)
    return glyph


def svg_reference_bounds(content: bytes, units_per_em: int, ascent: int):
    """Obtiene el bbox cuantizado a unidades TTF sin normalizaciones opticas."""
    glyph = svg_reference_glyph(content, units_per_em, ascent)
    return glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax


def is_pure_translation(reference, official, glyph_table, dx: int, dy: int) -> bool:
    """Confirma que los dos contornos difieran solo en su posicion, no en su forma."""
    if official.isComposite():
        return False
    points_a, ends_a, flags_a = reference.getCoordinates(None)
    points_b, ends_b, flags_b = official.getCoordinates(glyph_table)
    if len(points_a) != len(points_b) or ends_a != ends_b or list(flags_a) != list(flags_b):
        return False
    # diferencia maxima de una unidad por redondeo de curvas a coordenadas TTF
    return all(abs(a[0] - b[0] - dx) <= 1 and abs(a[1] - b[1] - dy) <= 1
               for a, b in zip(points_a, points_b))
