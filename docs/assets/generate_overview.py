"""From repo root: uv run --no-project --with fonttools --with cairosvg docs/assets/generate_overview.py.

Requires DejaVu Sans Bold and DejaVu Sans Mono TTFs. Set ALLOKATR_FONT_DIR
if they are not installed in /usr/share/fonts/truetype/dejavu.
"""
import os
from pathlib import Path

import cairosvg
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

OUT = Path(__file__).resolve().parent
FONTS = Path(os.environ.get('ALLOKATR_FONT_DIR', '/usr/share/fonts/truetype/dejavu'))
BOLD = TTFont(FONTS / 'DejaVuSans-Bold.ttf')
MONO = TTFont(FONTS / 'DejaVuSansMono.ttf')
# Dark terminal palette from frontend/src/app/globals.css.
BG, PANEL, TILE, LINE = '#0B0D0E', '#111416', '#171B1E', '#30373E'
INK, MUTED, CYAN, AMBER = '#E6EAED', '#A0ABB4', '#00D4E6', '#FFB020'
MARK = 'M10 51 28 12H37L55 51H44L40 42H24L20 51ZM28 33H36L32 24Z'


def text(value, x, y, size, color=INK, font=MONO):
    glyphs, cmap, metrics = font.getGlyphSet(), font.getBestCmap(), font['hmtx'].metrics
    scale, offset, paths = size / font['head'].unitsPerEm, 0, []
    for char in value:
        name = cmap[ord(char)]
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        if pen.getCommands():
            paths.append(f'<path transform="translate({offset})" d="{pen.getCommands()}"/>')
        offset += metrics[name][0]
    return f'<g fill="{color}" transform="translate({x} {y}) scale({scale} {-scale})">' + ''.join(paths) + '</g>'


def rect(x, y, w, h, color, stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="{stroke}"/>'


def mark(x, y, size):
    return (f'<g transform="translate({x} {y}) scale({size / 64})">'
            f'{rect(0, 0, 64, 64, BG, CYAN)}'
            f'<path fill="{CYAN}" fill-rule="evenodd" d="{MARK}"/></g>')


def save(name, width, height, content):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}">' + ''.join(content) + '</svg>\n')
    (OUT / f'{name}.svg').write_text(svg, encoding='utf-8')
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(OUT / f'{name}.png'))


def main():
    save('allokatr-logo', 128, 128, [rect(0, 0, 128, 128, BG), mark(1, 1, 126)])
    parts = [rect(0, 0, 1440, 596, BG), rect(1, 1, 1438, 594, 'none', LINE),
             mark(66, 77, 68), text('PORTFOLIO TERMINAL', 154, 118, 20, CYAN),
             text('Allokatr', 62, 255, 100, INK, BOLD),
             text('See where your', 67, 326, 37, INK, BOLD),
             text('next euro goes.', 67, 373, 37, INK, BOLD),
             rect(68, 437, 476, 1, LINE),
             text('IMPORT / PLAN / SIMULATE', 68, 482, 23, CYAN),
             text('SELF-HOSTED  ·  SINGLE-USER', 68, 524, 19, MUTED)]

    # Illustration of the allocation plan. All values below are synthetic.
    parts += [rect(592, 72, 782, 452, PANEL, LINE), rect(593, 73, 780, 50, TILE),
              text('PLAN', 620, 106, 23, CYAN),
              text('DEMO PORTFOLIO', 1120, 105, 22, MUTED),
              text('Target allocation', 620, 171, 33, INK, BOLD),
              text('CURRENT', 620, 216, 21, MUTED), text('TARGET', 620, 273, 21, MUTED)]
    for y, widths in ((194, (278, 184, 78)), (251, (318, 159, 63))):
        x = 806
        for width, color in zip(widths, (CYAN, '#0093A0', AMBER), strict=True):
            parts.append(rect(x, y, width - 4, 29, color))
            x += width
    parts.extend((rect(620, 315, 725, 1, LINE), text('ASSET CLASS', 620, 350, 20, MUTED),
                  text('CURRENT', 997, 350, 20, MUTED), text('TARGET', 1208, 350, 20, MUTED)))
    for y, label, actual, target, color in ((390, 'ETF', '52%', '59%', CYAN),
                                            (434, 'STOCK', '34%', '29%', '#0093A0'),
                                            (478, 'CRYPTO', '14%', '12%', AMBER)):
        parts.extend((rect(620, y - 14, 12, 12, color), text(label, 650, y, 23),
                      text(actual, 1000, y, 23), text(target, 1210, y, 23),
                      rect(620, y + 13, 725, 1, LINE)))
    save('allokatr-overview', 1440, 596, parts)


if __name__ == '__main__':
    main()
