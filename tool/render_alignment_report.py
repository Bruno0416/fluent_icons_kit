#!/usr/bin/env python3
"""Genera una muestra PNG con cruces de centrado para revisar los glifos."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from test_font_alignment import ROOT, SAMPLES, font_path, optical_center


def render(output: Path):
    mapping = json.loads((ROOT / 'tool' / 'codepoints.json').read_text('utf-8'))
    cell_w, cell_h = 104, 112
    image = Image.new('RGB', (cell_w * len(SAMPLES), cell_h * 2), '#f7f8fa')
    draw = ImageDraw.Draw(image)
    for row, variant in enumerate(('line', 'filled')):
        font = ImageFont.truetype(str(font_path(variant)), 48)
        for col, name in enumerate(SAMPLES):
            x = col * cell_w + cell_w // 2
            y = row * cell_h + 48
            draw.rectangle((x - 24, y - 24, x + 24, y + 24), outline='#718096')
            draw.line((x - 24, y, x + 24, y), fill='#ce5362')
            draw.line((x, y - 24, x, y + 24), fill='#ce5362')
            draw.text((x, y), chr(mapping[variant][name]), font=font, anchor='mm', fill='#171c27')
            # 1. el punto verde indica el centro de masa visual del glifo
            cx, cy = optical_center(font, mapping[variant][name], size=48)
            ox, oy = x + cx, y + cy
            draw.ellipse((ox - 2, oy - 2, ox + 2, oy + 2), fill='#159f73')
            draw.text((col * cell_w + 6, row * cell_h + 80), f'{variant}.{name}', fill='#273142')
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(f'Reporte visual: {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'alignment_report.png')
    render(parser.parse_args().output.resolve())
