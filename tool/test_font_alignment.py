#!/usr/bin/env python3
"""Regresion de fuentes: integridad, tipografia y glifos no vacios.

No exige centrar visualmente todos los glifos: Microsoft puede dibujar elementos
asimetricos intencionalmente. La fidelidad se comprueba contra sus SVG originales.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from svg_reference import svg_reference_glyph

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ('search', 'checkmark', 'heart', 'add', 'chevron_down', 'dismiss')


def font_path(variant: str) -> Path:
    return ROOT / 'assets' / 'fonts' / f'FluentKit{variant.title()}.ttf'


def optical_center(font: ImageFont.FreeTypeFont, codepoint: int, size: int = 96):
    """Metrica diagnostica: NO se aplica como traslacion automatica."""
    side = size * 3
    middle = side // 2
    image = Image.new('L', (side, side), 0)
    ImageDraw.Draw(image).text((middle, middle), chr(codepoint), font=font, anchor='mm', fill=255)
    bounds = image.getbbox()
    if bounds is None:
        raise AssertionError(f'Glifo vacio U+{codepoint:04X}')
    pixels = image.load()
    ink = x_sum = y_sum = 0
    for y in range(bounds[1], bounds[3]):
        for x in range(bounds[0], bounds[2]):
            amount = pixels[x, y]
            ink += amount
            x_sum += x * amount
            y_sum += y * amount
    return x_sum / ink - middle, y_sum / ink - middle


class FontAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / 'tool' / 'codepoints.json').read_text('utf-8'))

    def test_catalog_matches_both_font_cmaps(self):
        for variant in ('line', 'filled'):
            with self.subTest(variant=variant):
                font = TTFont(font_path(variant))
                cmap = font.getBestCmap()
                self.assertEqual(set(cmap), set(self.registry[variant].values()))
                self.assertGreater(font['head'].unitsPerEm, 0)
                self.assertGreater(font['hhea'].ascent, font['hhea'].descent)
                self.assertGreater(font['hhea'].advanceWidthMax, 0)

    def test_all_glyphs_have_valid_geometry_and_advance_width(self):
        """Comprueba la integridad TTF sin exigir igualdad con SVG de otra revision.

        Una fuente oficial puede contener curvas, detalles o redondeos distintos
        a una conversion SVG independiente. Esa diferencia no implica un error.
        """
        total = 0
        for variant in ('line', 'filled'):
            font = TTFont(font_path(variant))
            try:
                cmap = font.getBestCmap()
                glyphs = font['glyf']
                metrics = font['hmtx'].metrics
                advance_max = font['hhea'].advanceWidthMax
                for name, codepoint in self.registry[variant].items():
                    with self.subTest(variant=variant, icon=name):
                        glyph_name = cmap[codepoint]
                        glyph = glyphs[glyph_name]
                        # 1. asegurar que el codigo apunta a un dibujo real
                        self.assertTrue(glyph.isComposite() or glyph.numberOfContours > 0)
                        self.assertLess(glyph.xMin, glyph.xMax)
                        self.assertLess(glyph.yMin, glyph.yMax)
                        # 2. comprobar que el glifo dispone de avance horizontal
                        advance, bearing = metrics[glyph_name]
                        self.assertGreater(advance, 0)
                        self.assertLessEqual(advance, advance_max)
                        self.assertIsInstance(bearing, int)
                        total += 1
            finally:
                font.close()
        self.assertEqual(total, sum(map(len, self.registry.values())))

    def test_all_rendered_glyph_left_bearings_match_outlines(self):
        # Una discrepancia LSB/xMin mueve visualmente el icono dentro
        # del avance de Flutter Icon, aunque el contorno TTF sea correcto.
        for variant in ('line', 'filled'):
            font = TTFont(font_path(variant))
            try:
                self.assertTrue(font['head'].flags & 0x0002)
                cmap = font.getBestCmap()
                for name, codepoint in self.registry[variant].items():
                    with self.subTest(variant=variant, icon=name):
                        glyph_name = cmap[codepoint]
                        glyph = font['glyf'][glyph_name]
                        self.assertEqual(font['hmtx'][glyph_name][1], glyph.xMin)
            finally:
                font.close()

    def test_symmetrical_glyphs_are_horizontally_centered_at_48_px(self):
        # No exigimos esto a iconos asimetricos; solo a disenos simetricos.
        for variant in ('line', 'filled'):
            font = ImageFont.truetype(str(font_path(variant)), 48)
            for name in ('add', 'dismiss', 'access_time'):
                with self.subTest(variant=variant, icon=name):
                    image = Image.new('L', (128, 128), 0)
                    origin_x = 32
                    ImageDraw.Draw(image).text(
                        (origin_x, 32), chr(self.registry[variant][name]),
                        font=font, anchor='la', fill=255,
                    )
                    bbox = image.getbbox()
                    self.assertIsNotNone(bbox)
                    center_x = (bbox[0] + bbox[2]) / 2
                    self.assertLessEqual(abs(center_x - (origin_x + 24)), 1.25)

    def test_svg_ttf_differences_are_diagnostics_not_failures(self):
        """Verifica que el nuevo pipeline no dependa de reconciliaciones opticas."""
        path = ROOT / 'tool' / 'font_geometry_report.json'
        if not path.exists():
            self.skipTest('No hay reporte de diferencias SVG/TTF')
        report = json.loads(path.read_text(encoding='utf-8'))
        allowed = {'repositioned', 'incompatible_geometry', 'incompatible_outline'}
        for item in report.get('details', []):
            with self.subTest(variant=item.get('variant'), icon=item.get('icon')):
                self.assertIn(item['status'], allowed)
                self.assertIn(item['variant'], ('line', 'filled'))
                self.assertIn(item['icon'], self.registry[item['variant']])
                self.assertEqual(len(item['svg_bounds']), 4)
                self.assertEqual(len(item['ttf_bounds']), 4)
        self.assertEqual(
            report.get('compatible_translations', 0),
            sum(item['status'] == 'repositioned' for item in report.get('details', [])),
        )
        if 'incompatible' in report:
            self.assertEqual(
                report['incompatible'],
                sum(item['status'] != 'repositioned' for item in report.get('details', [])),
            )

    def test_all_glyph_outlines_match_original_svgs(self):
        # Compara todas las coordenadas, no solo el bbox: evita falsos positivos
        # cuando dos formas distintas ocupan la misma caja rectangular.
        count = 0
        for variant in ('line', 'filled'):
            font = TTFont(font_path(variant))
            try:
                cmap = font.getBestCmap()
                em = font['head'].unitsPerEm
                ascent = font['hhea'].ascent
                for name, cp in self.registry[variant].items():
                    with self.subTest(variant=variant, icon=name):
                        source = ROOT / 'tool' / 'source' / 'svg' / variant / f'{name}.svg'
                        expected = svg_reference_glyph(source.read_bytes(), em, ascent)
                        actual = font['glyf'][cmap[cp]]
                        exp_points, exp_ends, exp_flags = expected.getCoordinates(None)
                        act_points, act_ends, act_flags = actual.getCoordinates(font['glyf'])
                        self.assertEqual(list(exp_points), list(act_points))
                        self.assertEqual(exp_ends, act_ends)
                        self.assertEqual(list(exp_flags), list(act_flags))
                        self.assertEqual(font['hmtx'][cmap[cp]], (em, expected.xMin))
                        count += 1
            finally:
                font.close()
        self.assertEqual(count, sum(map(len, self.registry.values())))

    def test_sample_glyphs_are_nonempty_at_48_px(self):
        for variant in ('line', 'filled'):
            font = ImageFont.truetype(str(font_path(variant)), 48)
            for name in SAMPLES:
                with self.subTest(variant=variant, icon=name):
                    image = Image.new('L', (128, 128), 0)
                    ImageDraw.Draw(image).text((64, 64), chr(self.registry[variant][name]), font=font, anchor='mm', fill=255)
                    self.assertIsNotNone(image.getbbox(), f'{variant}.{name} no se renderizo')


if __name__ == '__main__':
    unittest.main()
