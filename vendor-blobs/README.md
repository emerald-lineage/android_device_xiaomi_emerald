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
git checkout -- proprietary-files.txt        # в файле живёт ещё system_ext-часть, её не трогаем
python3 vendor-blobs/list.py                 # дописывает vendor-часть
./extract-files.py -m --skip-firmware $HOME/lineage/out/scratch/vendor305-dump
```

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
