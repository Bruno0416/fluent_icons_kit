#!/usr/bin/env python3
"""Pruebas de subsetting sobre una fuente artificial sin depender de Internet."""
import json
import tempfile
import unittest
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from official_font_builder import build_from_official
from svg_reference import svg_reference_bounds


def glyph(dx: int):
    pen = TTGlyphPen(None)
    pen.moveTo((dx, 200))
    pen.lineTo((dx + 120, 200))
    pen.lineTo((dx + 120, 380))
    pen.closePath()
    return pen.glyph()


def make_source(base: Path, post3: bool = False):
    fb = FontBuilder(2048, isTTF=True)
    fb.setupGlyphOrder(['.notdef', 'g_heart', 'g_search', 'g_unused'])
    fb.setupCharacterMap({0xE101: 'g_heart', 0xE102: 'g_search', 0xE103: 'g_unused'})
    fb.setupGlyf({'.notdef': TTGlyphPen(None).glyph(), 'g_heart': glyph(270), 'g_search': glyph(510), 'g_unused': glyph(630)})
    fb.setupHorizontalMetrics({'.notdef': (2048, 0), 'g_heart': (2048, 270), 'g_search': (2048, 510), 'g_unused': (2048, 630)})
    fb.setupHorizontalHeader(ascent=1854, descent=-434)
    fb.setupNameTable({'familyName': 'OfficialFluent', 'styleName': 'Regular'})
    fb.setupOS2(sTypoAscender=1854, sTypoDescender=-434, usWinAscent=1854, usWinDescent=434)
    fb.setupPost()
    fb.setupMaxp()
    fb.setupHead(unitsPerEm=2048, created=3850000000, modified=3850000000)
    if post3:
        fb.font['post'].formatType = 3.0
    fb.save(base / 'FluentSystemIcons-Regular.ttf')
    (base / 'FluentSystemIcons-Regular.json').write_text(json.dumps({
        'ic_fluent_heart_24_regular': 0xE101,
        'ic_fluent_search_24_regular': 0xE102,
        'ic_fluent_unused_24_regular': 0xE103,
    }))


class FontUpstreamTests(unittest.TestCase):
    def test_selected_icons_preserve_official_geometry_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_source(root)
            dest = root / 'FluentKitLine.ttf'
            mapping = {'heart': 0xE000, 'search': 0xE001}
            entries = {'heart': (24, 'heart.svg', b''), 'search': (24, 'search.svg', b'')}
            self.assertEqual(build_from_official('line', entries, mapping, dest, root), 2)
            original = TTFont(root / 'FluentSystemIcons-Regular.ttf')
            result = TTFont(dest)
            self.assertEqual(result['head'].unitsPerEm, original['head'].unitsPerEm)
            self.assertEqual(result['hhea'].ascent, original['hhea'].ascent)
            self.assertEqual(result['hhea'].descent, original['hhea'].descent)
            self.assertEqual(result.getBestCmap(), {0xE000: 'g_heart', 0xE001: 'g_search'})
            self.assertEqual(result['hmtx']['g_heart'], original['hmtx']['g_heart'])
            self.assertEqual(result['hmtx']['g_search'], original['hmtx']['g_search'])
            self.assertEqual(result['glyf']['g_heart'].coordinates, original['glyf']['g_heart'].coordinates)
            self.assertEqual(result['glyf']['g_search'].coordinates, original['glyf']['g_search'].coordinates)
            self.assertNotIn('g_unused', result.getGlyphOrder())
            self.assertEqual(result['name'].getDebugName(1), 'FluentKitLine')

    def test_incorrect_official_left_bearings_are_fixed_without_moving_outlines(self):
        # Reproduce la fuente real: UPM 500 y LSB 0 frente a xMin > 0.
        # El motor de texto debe poder dibujar cada icono dentro de su avance.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_source(root)
            original_path = root / 'FluentSystemIcons-Regular.ttf'
            source = TTFont(original_path)
            for name in ('g_heart', 'g_search'):
                advance, _ = source['hmtx'][name]
                source['hmtx'][name] = (advance, 0)
            source['head'].flags &= ~0x0002
            source.save(original_path)
            source.close()
            output_path = root / 'FluentKitLine.ttf'
            build_from_official(
                'line',
                {'heart': (24, '', b''), 'search': (24, '', b'')},
                {'heart': 0xE000, 'search': 0xE001},
                output_path, root,
            )
            original = TTFont(original_path)
            result = TTFont(output_path)
            try:
                for glyph_name in ('g_heart', 'g_search'):
                    with self.subTest(glyph=glyph_name):
                        self.assertEqual(original['hmtx'][glyph_name][1], 0)
                        self.assertEqual(
                            result['hmtx'][glyph_name],
                            (original['hmtx'][glyph_name][0],
                             original['glyf'][glyph_name].xMin),
                        )
                        self.assertEqual(
                            result['glyf'][glyph_name].coordinates,
                            original['glyf'][glyph_name].coordinates,
                        )
                self.assertTrue(result['head'].flags & 0x0002)
            finally:
                original.close()
                result.close()

    def test_svg_viewbox_restores_translated_official_glyph(self):
        # Fuente artificial con contorno correcto, pero fuera de su posicion SVG.
        svg = (b'<svg xmlns="http://www.w3.org/2000/svg" '
               b'viewBox="0 0 2048 2048">'
               b'<path d="M300 1754L420 1754L420 1574Z"/></svg>')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_source(root)
            output = root / 'aligned.ttf'
            build_from_official('line', {'heart': (24, 'heart.svg', svg)},
                                {'heart': 0xE000}, output, root)
            generated = TTFont(output)
            glyph_name = generated.getBestCmap()[0xE000]
            glyph = generated['glyf'][glyph_name]
            self.assertEqual((glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax),
                             (300, 100, 420, 280))
            self.assertEqual(generated['hmtx'][glyph_name], (2048, 300))
            original = TTFont(root / 'FluentSystemIcons-Regular.ttf')
            unmodified = original['glyf']['g_heart']
            self.assertEqual((unmodified.xMin, unmodified.yMin), (270, 200))

    def test_svg_is_used_even_when_official_outline_differs(self):
        # La geometria original del SVG prevalece sobre la TTF oficial.
        svg = (b'<svg xmlns="http://www.w3.org/2000/svg" '
               b'viewBox="0 0 24 24"><path d="M6 6h12v12H6Z"/></svg>')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_source(root)
            diagnostics = []
            output = root / 'output.ttf'
            build_from_official('line', {'heart': (24, 'heart.svg', svg)},
                                {'heart': 0xE000}, output, root,
                                diagnostics=diagnostics)
            self.assertFalse(diagnostics)
            result = TTFont(output)
            source = TTFont(root / 'FluentSystemIcons-Regular.ttf')
            try:
                glyph = result['glyf'][result.getBestCmap()[0xE000]]
                self.assertEqual(
                    (glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax),
                    svg_reference_bounds(svg, 2048, 1854),
                )
                self.assertNotEqual(glyph.coordinates, source['glyf']['g_heart'].coordinates)
                self.assertEqual(result['head'].unitsPerEm, 2048)
            finally:
                result.close()
                source.close()

    def test_two_icons_with_different_geometry_are_independent(self):
        svg_heart = (b'<svg xmlns="http://www.w3.org/2000/svg" '
                     b'viewBox="0 0 24 24"><path d="M2 2h20v20H2Z"/></svg>')
        svg_search = (b'<svg xmlns="http://www.w3.org/2000/svg" '
                      b'viewBox="0 0 24 24"><path d="M6 6h12v12H6Z"/></svg>')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_source(root)
            output = root / 'output.ttf'
            count = build_from_official('line', {
                'heart': (24, 'heart.svg', svg_heart),
                'search': (24, 'search.svg', svg_search),
            }, {'heart': 0xE000, 'search': 0xE001}, output, root)
            self.assertEqual(count, 2)
            font = TTFont(output)
            try:
                self.assertEqual(set(font.getBestCmap()), {0xE000, 0xE001})
                for cp, svg in ((0xE000, svg_heart), (0xE001, svg_search)):
                    glyph = font['glyf'][font.getBestCmap()[cp]]
                    self.assertEqual(
                        (glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax),
                        svg_reference_bounds(svg, 2048, 1854),
                    )
            finally:
                font.close()

    def test_svg_outline_is_preserved_not_replaced_by_official_triangle(self):
        svg = (b'<svg xmlns="http://www.w3.org/2000/svg" '
               b'viewBox="0 0 2048 2048">'
               b'<path d="M300 1574h120v180H300Z"/></svg>')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_source(root)
            output = root / 'result.ttf'
            build_from_official('line', {'heart': (24, '', svg)},
                                {'heart': 0xE000}, output, root)
            font = TTFont(output)
            source = TTFont(root / 'FluentSystemIcons-Regular.ttf')
            try:
                glyph = font['glyf'][font.getBestCmap()[0xE000]]
                self.assertEqual(glyph.numberOfContours, 1)
                self.assertEqual(
                    (glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax),
                    (300, 100, 420, 280),
                )
                self.assertNotEqual(glyph.coordinates, source['glyf']['g_heart'].coordinates)
            finally:
                font.close()
                source.close()

    def test_same_upstream_glyph_can_represent_two_independent_svgs(self):
        svg_a = (b'<svg xmlns="http://www.w3.org/2000/svg" '
                 b'viewBox="0 0 24 24"><path d="M2 2h20v20H2Z"/></svg>')
        svg_b = (b'<svg xmlns="http://www.w3.org/2000/svg" '
                 b'viewBox="0 0 24 24"><path d="M6 6h12v12H6Z"/></svg>')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_source(root)
            upstream_json = root / 'FluentSystemIcons-Regular.json'
            data = json.loads(upstream_json.read_text())
            data['ic_fluent_alias_24_regular'] = data['ic_fluent_heart_24_regular']
            upstream_json.write_text(json.dumps(data))
            output = root / 'alias.ttf'
            self.assertEqual(build_from_official('line', {
                'heart': (24, '', svg_a),
                'alias': (24, '', svg_b),
            }, {'heart': 0xE000, 'alias': 0xE001}, output, root), 2)
            font = TTFont(output)
            try:
                a = font['glyf'][font.getBestCmap()[0xE000]]
                b = font['glyf'][font.getBestCmap()[0xE001]]
                self.assertEqual((a.xMin, a.xMax), (171, 1877))
                self.assertEqual((b.xMin, b.xMax), (512, 1536))
            finally:
                font.close()

    def test_partially_supplied_svg_is_rejected(self):
        svg = (b'<svg xmlns="http://www.w3.org/2000/svg" '
               b'viewBox="0 0 24 24"><path d="M2 2h20v20H2Z"/></svg>')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_source(root)
            with self.assertRaisesRegex(ValueError, 'faltan SVGs'):
                build_from_official('line', {
                    'heart': (24, '', svg),
                    'search': (24, '', b''),
                }, {'heart': 0xE000, 'search': 0xE001}, root / 'out.ttf', root)
            self.assertFalse((root / 'out.ttf').exists())

    def test_svg_reference_bounds_preserves_viewbox_position(self):
        svg = (b'<svg xmlns="http://www.w3.org/2000/svg" '
               b'viewBox="0 0 24 24"><path d="M3 5h18v14H3Z"/></svg>')
        self.assertEqual(svg_reference_bounds(svg, 1024, 850),
                         (128, 39, 896, 637))

    def test_post_v3_fonts_without_glyph_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_source(root, post3=True)
            out = root / 'result.ttf'
            build_from_official('line', {'heart': (24, '', b'')}, {'heart': 0xE000}, out, root)
            result = TTFont(out)
            self.assertEqual(set(result.getBestCmap()), {0xE000})
            self.assertEqual(result['hmtx'][result.getBestCmap()[0xE000]], (2048, 270))

    def test_missing_official_glpyhs_do_not_generate_incomplete_font(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_source(root)
            with self.assertRaisesRegex(ValueError, 'no coinciden'):
                build_from_official('line', {'missing': (24, '', b'')}, {'missing': 0xE000}, root / 'output.ttf', root)
            self.assertFalse((root / 'output.ttf').exists())

    def test_input_files_are_required(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                build_from_official('filled', {}, {}, Path(temp) / 'out.ttf', Path(temp))


if __name__ == '__main__':
    unittest.main()
