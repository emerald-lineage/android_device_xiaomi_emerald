#!/usr/bin/env python3
"""Сверка: какие наши пути в vendor/odm ставит ещё и платформа.

Читает `out/soong/installs-lineage_emerald.mk` (его пишет kati; нужен любой прогон, дошедший до
kati) и сравнивает со списком `proprietary-files.txt` этого дерева — файлы, симлинки `SYMLINK=` из
строк списка и симлинки `vendor_symlinks/Android.bp`. Ловит оба вида правил: `target: source`
(модули soong) и `$(eval $(call fn, src, target))` — make-копии, среди них vintf-фрагменты
платформенных HAL: kati считает их такими же правилами и падает на дубле.

Вывод — пути, которые надо дописать в `FROM_SOURCE` (`list.py`). Пустой вывод = дублей нет.
"""
import os
import re
import sys
import collections

TREE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
DEV = os.path.join(TREE, 'device/xiaomi/emerald')
MK = os.path.join(TREE, 'out/soong/installs-lineage_emerald.mk')
PREFIX = 'out/target/product/emerald/'
PATH_RE = r'out/target/product/emerald/(?:vendor|odm)/[^ \t,|:)]+'

if not os.path.exists(MK):
    sys.exit(f'нет {MK}: нужен прогон, дошедший до kati')

rules = collections.defaultdict(list)
for line in open(MK, encoding='utf-8', errors='replace'):
    m = re.match(r'^(' + PATH_RE + r'): (\S+)', line)
    if m:
        rules[m.group(1)].append(m.group(2))
        continue
    if '$(eval $(call ' in line:
        args = re.findall(r'\$\(eval \$\(call [^,]+, (.*)\)\)\s*$', line)
        if args:
            parts = [p.strip() for p in args[0].split(',')]
            if len(parts) >= 2 and re.fullmatch(PATH_RE, parts[-1]):
                rules[parts[-1]].append(parts[0])

def ours(src):
    return 'emerald_blob_' in src or 'vendor/xiaomi/emerald/' in src

have = set()
for line in open(os.path.join(DEV, 'proprietary-files.txt')):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    parts = line.split(';')
    have.add(parts[0])
    for arg in parts[1:]:
        if arg.startswith('SYMLINK='):
            have.update(p for p in arg[len('SYMLINK='):].split(',') if p)
for loc in re.findall(r'installed_location: "([^"]+)"',
                      open(os.path.join(DEV, 'vendor_symlinks/Android.bp')).read()):
    have.add('vendor/' + loc)

conflicts = 0
for target, srcs in sorted(rules.items()):
    rel = target[len(PREFIX):]
    if rel in have:
        platform = [s for s in srcs if not ours(s)]
        if platform:
            conflicts += 1
            print(rel[len('vendor'):], '<-', platform[0])
print(f'# наших путей: {len(have)}, конфликтов: {conflicts}', file=sys.stderr)
sys.exit(1 if conflicts else 0)
