"""Valida que el laboratorio use las tres fuentes reales sin offsets."""
import hashlib
import json
import os
import unittest
from pathlib import Path

from fontTools.ttLib import TTFont

from build_icon_diagnostics import ROOT, SAMPLES, prepare


class IconDiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        upstream = Path(os.environ.get(
            'FLUENT_UPSTREAM_FONTS', ROOT.parent / 'fluentui-system-icons' / 'fonts'
        ))
        if not (upstream / 'FluentSystemIcons-Regular.ttf').is_file():
            raise unittest.SkipTest('Microsoft upstream TTFs not available; set FLUENT_UPSTREAM_FONTS')
        cls.upstream = upstream
        cls.samples = prepare(upstream)

    def test_both_variants_and_expected_sample_icons(self):
        self.assertEqual(len(self.samples), 2 * len(SAMPLES))
        self.assertEqual({r['variant'] for r in self.samples}, {'line', 'filled'})
        self.assertEqual({r['name'] for r in self.samples}, set(SAMPLES))

    def test_official_fonts_are_copied_byte_for_byte(self):
        for family in ('Regular', 'Filled'):
            filename = f'FluentSystemIcons-{family}.ttf'
            source = (self.upstream / filename).read_bytes()
            actual = (ROOT / 'preview/assets/diagnostics/fonts' / filename).read_bytes()
            self.assertEqual(hashlib.sha256(actual).digest(), hashlib.sha256(source).digest())

    def test_all_samples_have_cmap_and_advance_width(self):
        for sample in self.samples:
            for source in ('official', 'kit'):
                info = sample[source]
                self.assertGreater(info['advance_width'], 0)
                self.assertEqual(len(info['bounds']), 4)
                self.assertLess(info['bounds'][0], info['bounds'][2])
                self.assertLess(info['bounds'][1], info['bounds'][3])

    def test_generated_dart_references_published_kit_names(self):
        dart = (ROOT / 'preview/lib/icon_diagnostics.g.dart').read_text()
        for sample in self.samples:
            self.assertIn(f"FluentIcons.{sample['variant']}.{sample['name']}", dart)
            self.assertIn(f"0x{sample['official']['codepoint']:X}", dart)

    def test_diagnostic_process_does_not_modify_kit_font(self):
        before = {
            family: hashlib.sha256((ROOT / 'assets/fonts' / f'FluentKit{family}.ttf').read_bytes()).digest()
            for family in ('Line', 'Filled')
        }
        prepare(self.upstream)
        for family, digest in before.items():
            self.assertEqual(
                hashlib.sha256((ROOT / 'assets/fonts' / f'FluentKit{family}.ttf').read_bytes()).digest(),
                digest,
            )


if __name__ == '__main__':
    unittest.main()
