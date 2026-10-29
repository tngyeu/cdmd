"""Repair the legacy Vietnamese strings in a CadCraft DXF export.

TCVN3 character assignments follow UniKey's charset data:
https://github.com/KeiosStarqua/fcitx5-unikey/blob/master/unikey/data.cpp
Only text content and the corresponding text-style font fields are changed.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r'D:\Workspace\Anhome\DCPL 7.dwg')
OUTPUT = Path(r'D:\Workspace\Anhome\DCPL 7 - Unicode.dxf')
src_chars = 'µ¸¶·¹¨»¾¼½Æ©ÇÊÈÉË®ÌÐÎÏÑªÒÕÓÔÖ×ÝØÜÞßãáâä«åèæçé¬êíëìîïóñòô­õøö÷ùúýûüþ¡¢§£¤¥¦'
dst_chars = 'àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĂÂĐÊÔƠƯ'
assert len(src_chars) == len(dst_chars) == len(set(src_chars))
mapping = str.maketrans(src_chars, dst_chars)
fonts = {
    'Style-Vntime': 'times.ttf',
    'Style-Vnarial': 'arial.ttf',
    'Style-vncour': 'cour.ttf',
    'Style-Vnarial I 0.26180': 'arial.ttf',
    'Style-Vntime I 0.26180': 'times.ttf',
    'Style-VHarial': 'arial.ttf',
}

def decode_escape(value):
    return re.sub(r'\\U\+([0-9A-Fa-f]{4})', lambda m: chr(int(m[1], 16)), value)

def encode_escape(value):
    return ''.join(c if ord(c) < 128 else '\\U+%04X' % ord(c) for c in value)

def convert(value, uppercase=False):
    value = decode_escape(value)
    # The imported legacy glyph for TCVN3 0xD8 (ỉ) was normalized to
    # the diameter symbol in five Vietnamese words. Restore it only
    # inside a word, leaving actual diameter annotations untouched.
    value = re.sub(r'(?<=[A-Za-z\u00a0-\u00ff])∅(?=[A-Za-z])', 'Ø', value)
    value = value.translate(mapping)
    if uppercase:
        # These are TEXT title entities, rendered by an uppercase Vietnamese font.
        value = value.upper()
    return value

for old, expected in [('®­êng', 'đường'), ('Sè thªm', 'Số thêm'),
                      ('Ngâ ®i chung 64 m2', 'Ngõ đi chung 64 m2'),
                      ('Tr.MÇm Non\\PTh«n Nha X¸\\P', 'Tr.Mầm Non\\PThôn Nha Xá\\P')]:
    assert convert(old) == expected

rows = (ROOT / 'source.dxf').read_text(encoding='utf-8').splitlines()
assert len(rows) % 2 == 0
pairs = [[int(rows[i]), rows[i + 1]] for i in range(0, len(rows), 2)]
before = [p[:] for p in pairs]
records = []
for i, (code, value) in enumerate(pairs):
    if code == 0:
        records.append([])
    if records:
        records[-1].append(i)
changes = []
changed_entities = set()
style_changes = []
allowed = set()
for indexes in records:
    kind = pairs[indexes[0]][1]
    fields = {pairs[i][0]: pairs[i][1] for i in indexes}
    if kind == 'STYLE' and fields.get(2) in fonts:
        name = fields[2]
        for i in indexes:
            if pairs[i][0] == 3:
                pairs[i][1] = fonts[name]
                allowed.add(i)
                style_changes.append({'name': name, 'old': before[i][1], 'new': pairs[i][1]})
    elif kind in ('TEXT', 'MTEXT', 'ATTRIB', 'ATTDEF') and fields.get(7) in fonts:
        style = fields[7]
        for i in indexes:
            if pairs[i][0] not in ((1, 3) if kind == 'MTEXT' else (1,)):
                continue
            original = pairs[i][1]
            repaired = convert(original, uppercase=style == 'Style-VHarial')
            if repaired != decode_escape(original):
                pairs[i][1] = encode_escape(repaired)
                allowed.add(i)
                changed_entities.add(fields.get(5))
                changes.append({'handle': fields.get(5), 'type': kind, 'style': style,
                                'old': decode_escape(original), 'new': repaired})

diff = [i for i in range(len(pairs)) if pairs[i] != before[i]]
assert set(diff) == allowed
assert all(pairs[i][0] == before[i][0] for i in diff)
assert changes and len(style_changes) == len(fonts)
OUTPUT.write_text(''.join(f'{code}\n{value}\n' for code, value in pairs), encoding='utf-8')
report = {
    'source': str(SOURCE), 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'output_dxf': str(OUTPUT), 'changed_text_entities': len(changed_entities),
    'style_changes': style_changes, 'changes': changes,
    'verification': 'Every DXF group other than the listed text strings and six font names is unchanged.',
    'record_counts': dict(Counter(pairs[r[0]][1] for r in records)),
}
(ROOT / 'font-fix-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: report[k] for k in ('source_sha256', 'output_dxf', 'changed_text_entities', 'style_changes')}, ensure_ascii=False))
print(json.dumps(changes[:12], ensure_ascii=False))
