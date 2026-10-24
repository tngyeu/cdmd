"""Render the number/date and operative grant of every 2026 My Loc decision."""
import concurrent.futures
import json
from pathlib import Path
import re
import subprocess
import sys

import pdfplumber
from PIL import Image, ImageDraw, ImageFont

from parse_sources import ROOT

sys.stdout.reconfigure(encoding='utf-8')
OUT = ROOT / 'tmp/pdfs/myloc_area_2026'
ROWS = json.loads((OUT / 'texts.json').read_text(encoding='utf-8'))
DPI = 120
SCALE = DPI / 72


def render(row):
    number = row['source_number'].split('/')[0]
    folder = OUT / number
    folder.mkdir(parents=True, exist_ok=True)
    prefix = folder / 'page'
    first = folder / 'page-1.png'
    second = folder / 'page-2.png'
    if not (first.exists() and second.exists()):
        subprocess.run(['pdftoppm', '-f', '1', '-l', '2', '-r', str(DPI), '-png', str(ROOT / row['local_pdf']), str(prefix)], check=True, capture_output=True)
    with pdfplumber.open(ROOT / row['local_pdf']) as pdf:
        page = pdf.pages[1]
        matches = page.search(r'Điều\s*1[.:]')
        if not matches:
            raise ValueError('Article 1 not found: ' + number)
        top = matches[0]['top'] - 5
        endings = page.search(r'Vị trí,?\s*ranh giới')
        bottom = min((m['top'] + 6 for m in endings if m['top'] > top), default=min(top + 280, page.height))
        body_bounds = [top, bottom]
    header_image = Image.open(first).convert('RGB')
    article_image = Image.open(second).convert('RGB')
    header = header_image.crop((45 * SCALE, 20 * SCALE, header_image.width - 35 * SCALE, 210 * SCALE))
    article = article_image.crop((45 * SCALE, top * SCALE, article_image.width - 35 * SCALE, bottom * SCALE))
    width = 1000
    header = header.resize((width - 24, round(header.height * (width - 24) / header.width)))
    article = article.resize((width - 24, round(article.height * (width - 24) / article.width)))
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 23)
    tile = Image.new('RGB', (width, header.height + article.height + 105), 'white')
    draw = ImageDraw.Draw(tile)
    draw.text((12, 10), f"{row['source_number']} | {row['issue_date']} | PDF pages 1 + 2", fill='#164d3b', font=font)
    tile.paste(header, (12, 48))
    draw.line((0, header.height + 55, width, header.height + 55), fill='#90a992', width=2)
    tile.paste(article, (12, header.height + 70))
    draw.rectangle((0, 0, tile.width - 1, tile.height - 1), outline='#90a992', width=2)
    tile.save(folder / 'review.png')
    return {'number': number, 'body_bounds_points': body_bounds, 'image': str(folder / 'review.png')}


if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rendered = list(pool.map(render, ROWS))
    manifests = []
    for i in range(0, len(rendered), 4):
        part = rendered[i:i + 4]
        tiles = [Image.open(r['image']).convert('RGB') for r in part]
        heights = [max(t.height for t in tiles[:2]), max(t.height for t in tiles[2:])]
        sheet = Image.new('RGB', (2000, sum(heights) + 12), '#e7ece3')
        for j, tile in enumerate(tiles):
            sheet.paste(tile, ((j % 2) * 1000, 0 if j < 2 else heights[0] + 12))
        target = OUT / f'review_batch_{i // 4 + 1:02}.png'
        sheet.save(target)
        manifests.append({'image': str(target), 'numbers': [r['number'] for r in part]})
    (OUT / 'render_manifest.json').write_text(json.dumps(manifests, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(manifests, ensure_ascii=False, indent=2))
