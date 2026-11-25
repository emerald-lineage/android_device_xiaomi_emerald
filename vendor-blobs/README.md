# Списки блобов вендора 2.24 — как они сделаны

`list.py` заново генерирует vendor-часть `../proprietary-files.txt` из стокового `vendor.img` 305.
Список — не ручная работа: правила ниже, иначе 5222 файла и 740 симлинков не проверить.

## Подготовка (один раз)

```bash
# 1. распаковать образ (без root достаточно: capability и hardlink'ов в 305 нет)
fsck.erofs --extract=$HOME/lineage/out/scratch/vendor-305-tree \
    $HOME/lineage/vendor/xiaomi/emerald-images/vendor.img

# 2. метаданные каждого inode из образа (путь, тип, размер, uid/gid, режим, размер xattr)
cd $HOME/lineage/out/scratch/vendor-305-tree
find . -mindepth 1 | sed 's|^\.||' | sort > /tmp/vendor305-paths.txt
xargs -a /tmp/vendor305-paths.txt -d '\n' -P 8 -n 1 \
    $HOME/lineage/device/xiaomi/emerald/vendor-blobs/meta-one.sh \
    $HOME/lineage/vendor/xiaomi/emerald-images/vendor.img > /tmp/vendor305-meta.tsv
```

## Генерация

```bash
cd $HOME/lineage/device/xiaomi/emerald
# в файле обе части: system_ext (1-36) и vendor; list.py дописывает vendor-часть,
# поэтому её сначала отрезаем, иначе в списке окажется два экземпляра
git show HEAD:proprietary-files.txt | sed '/^# Vendor partition:/,$d' > proprietary-files.txt
python3 vendor-blobs/list.py                 # дописывает vendor-часть
./extract-files.py -m --skip-firmware $HOME/lineage/out/scratch/vendor305-dump
```

`list.py` берёт пути из `/tmp/opencode/vendor305-meta.tsv`. Если тот недописан (оборванный прогон
`xargs`), список молча получится короче — сверять: `wc -l /tmp/opencode/vendor305-meta.tsv` должен быть
равен числу строк `/tmp/opencode/vendor305-paths.txt` (6305), а после генерации — 4808 строк `vendor/`
и 4808 файлов в `../../vendor/xiaomi/emerald/proprietary/vendor`.

Дамп для `extract-files.py` — каталог с `system/`, `system_ext/` и `vendor/` (последний — распакованный
образ). После генерации три строки `system_ext/...videotelephony@1.0...` дописывались вручную с
`;MAKE_COPY_RULE_ONLY`: имена с `@` нельзя делать именем soong-модуля, а `libmtk_vt_wrapper.so` ссылается
на них, поэтому у восьми `system_ext/lib*/**.so` стоит `;DISABLE_DEPS`.

## Правила `list.py`

| Что | Как |
| --- | --- |
| все обычные файлы образа кроме `build.prop` | строка `vendor/<путь>` |
| 4 файла, которые даёт дерево (health HAL, его vintf-фрагмент, media_profiles, fstab) | не перечисляются, их ставит `device.mk` |
| симлинки на файлы раздела | `;SYMLINK=vendor/<путь>` на строке цели |
| 4 симлинка с `[` и `@` в имени, каталог `/firmware/sensor`, `/lib/modules` → `vendor_dlkm` | не воспроизводятся: первые четыре — руками в `../vendor_symlinks/Android.bp` |
| `.so` | `;MODULE=emerald_blob_<имя>;DISABLE_DEPS` — имя модуля своё, имя файла сохраняет `stem`; список зависимостей из ELF не нужен (блоб не участвует в сборке) |
| `bin/**`, `odm/**`, `overlay/**`, имена с `@`, две 32-битные библиотеки с общим именем, библиотеки, которые в дереве есть только как system_ext | `;MAKE_COPY_RULE_ONLY` — ставится файлом, без модуля |

Почему так: сборка раздела из блобов конфликтует с деревом в трёх местах — модуль с тем же именем, что
исходный модуль для vendor (`vendor_available`, интерфейсы AIDL/HIDL), модуль с тем же именем в другой
партиции (`system_ext`) и имена, недопустимые в soong (`@`, `[`). Отсюда переименование модулей и
копирование файлов вместо модулей.

## FROM_SOURCE — пути, которые ставит платформа

В vendor пишут двумя способами: soong ставит vendor-вариант каждого `vendor_available` модуля из
`PRODUCT_PACKAGES` (и его зависимости), а `PRODUCT_COPY_FILES` сгенерированного `emerald-vendor.mk`
копирует файл напрямую. Наш блоб на тот же путь — ошибка kati «overriding commands for target».
Выключить это для одного раздела нельзя: у `PRODUCT_PACKAGES` нет синтаксиса «−модуль», `filter-out`
в product-makefile выполняется до слияния унаследованных списков, а `overrides` (фониковый модуль)
влияет только на упаковку fsgen — install-правило от самого модуля остаётся (проверено 25.11:
`passwd_vendor` и `toolbox_vendor` так и остались установленными). Поэтому такие пути в списке блобов не
перечисляются (`FROM_SOURCE` в `list.py`), а файл в образ приходит из дерева.

Сейчас их 647: 401 из первой волны (20 — конфликт имён модулей, 388 — названные kati на первом прогоне,
прошедшем soong, 25.11 19:47, минус 7, которые тогда оставили блобами), 245 из статической сверки
итогового списка с `installs-*.mk`, ещё 2 (`lib/mt6789/libmnl.so` обеих битностей — их ставит платформа,
а наши симлинки на них давали второй `install_symlink`-дубль), минус `com.google.android.widevine.
nonupdatable.apex` — его ставим только мы, он снова блоб. AOSP и открытые MediaTek/NXP:
`hardware/interfaces`, `hardware/mediatek`, `hardware/nxp`, `frameworks/*`, `system/*`.

Среди этих путей — стоковые `libaedv`, `audio.bluetooth.default`,
`vendor.mediatek.hardware.bluetooth.audio-V1-ndk` (обе битности) и `nfc_nci_nxp_snxxx_v2`: в образе теперь
сборка дерева (Android 17), а не стоковая из проприетарных исходников MTK/NXP. Это осознанный обмен
(решение пользователя 25.11, вариант «платформа владеет тем, что ставит»): фониковый `overrides` kati не
проходит, а вычитать отдельные модули из `PRODUCT_PACKAGES` нельзя.

Обновить список после сборки, которая сообщила новые дубли, или для статической сверки:

```bash
cd $HOME/lineage
python3 - <<'EOF'
import re, collections, os
D = 'device/xiaomi/emerald'
d = collections.defaultdict(set)
for line in open('out/soong/installs-lineage_emerald.mk', errors='replace'):
    m = re.match(r'^(out/target/product/emerald/(?:vendor|odm)/\S+): (\S+)', line)
    if m: d[m.group(1)].add(m.group(2))
paths = set()                                    # файлы + симлинки, наши правила
for line in open(os.path.join(D, 'proprietary-files.txt')):
    line = line.strip()
    if not line or line.startswith('#'): continue
    parts = line.split(';'); paths.add(parts[0])
    for a in parts[1:]:
        if a.startswith('SYMLINK='): paths.update(x for x in a[8:].split(',') if x)
for loc in re.findall(r'installed_location: "([^"]+)"', open(os.path.join(D, 'vendor_symlinks/Android.bp')).read()):
    paths.add('vendor/' + loc)
for k, v in sorted(d.items()):
    rel = k[len('out/target/product/emerald/'):]
    # свои правила (блоб-модуль, копия из блоб-репо) конфликтом не считаются
    if rel in paths and any('emerald_blob_' not in s and 'vendor/xiaomi/emerald/' not in s for s in v):
        print('/' + rel[len('vendor'):], '<-', sorted(v)[0])
EOF
```

Пути из вывода дописать в `FROM_SOURCE` (`list.py`) и перегенерировать список и блоб-репо: `list.py` сам
`proprietary-files.txt` перезапишет, `extract-files.py` файлы **не удаляет** — лишние снять вручную
(`find proprietary/vendor -type f`, которых нет в списке), и только потом повторить генерацию.
