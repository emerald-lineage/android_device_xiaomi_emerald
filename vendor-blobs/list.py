#!/usr/bin/env python3
"""Write the vendor part of device/xiaomi/emerald/proprietary-files.txt from the stock image.

See README.md next to this file: it documents the preparation commands, the rules and why they exist.

Rules, all applied from scratch so the result does not depend on earlier fixes:
  * every regular file of the stock vendor.img is listed (build.prop is not: the build writes it);
  * four files are provided by the device tree instead (health HAL binary + its vintf fragment,
    media_profiles_V1_0.xml, fstab.mt6789) - they are not listed;
  * symlinks that point at listed files become SYMLINK arguments on the target line, except the four
    with names soong cannot use (`[`, `@`) - those are written by hand in vendor_symlinks/Android.bp -
    and the two that point at a directory or into vendor_dlkm;
  * files soong has no package rule for (odm/*, overlay/*.apk) and the two 32-bit libraries whose 64-bit
    twin takes the module name are installed as plain copies (MAKE_COPY_RULE_ONLY);
  * every library whose name also exists as a module in the source tree gets its own module name
    (MODULE=emerald_blob_...) with the file name kept by stem, so a blob never fights a source module
    for the vendor partition (AIDL/HIDL interface libraries, vendor_available libraries);
  * libraries that exist in the tree only as system_ext modules are plain copies too.
"""
import os
import re
import sys

TREE = '/home/ramdll/lineage'
ROOT = '/home/ramdll/lineage/out/scratch/vendor-305-tree'
META = '/tmp/opencode/vendor305-meta.tsv'
OUT = os.path.join(TREE, 'device/xiaomi/emerald/proprietary-files.txt')

TREE_PROVIDED = {
    '/bin/hw/android.hardware.health-service.example',
    '/etc/vintf/manifest/android.hardware.health-service.example.xml',
    '/etc/media_profiles_V1_0.xml',
    '/etc/fstab.mt6789',
}
COPY_RULE_ONLY = {
    '/lib/libnotifyaudiohal.so',
    '/lib/hw/sensors.elliptic.so',
}

# Libraries the platform puts into the vendor image on its own: soong packs the vendor variant of every
# vendor_available module listed in PRODUCT_PACKAGES (base_system.mk lists libbase, libcutils, libbinder,
# libui, ...), and a blob for the same path is a hard packaging conflict - and PRODUCT_PACKAGES has no
# way to keep a module out of one partition (no "-module", and a filter-out in a product makefile runs
# before the inherited lists are merged). So these come from the source tree, not from the image.
# The AOSP builds are Android 17 where the stock copies are Android 16; every symbol the stock vendor
# binaries import from these libraries exists in the AOSP builds (checked with readelf over all 3762
# stock files of vendor/lib*, vendor/bin), so the newer copy is ABI-safe for the stock blobs.
# Only the paths soong actually installs can be dropped; the other bitness (e.g. lib64/libbinder.so)
# is not installed by the source build and stays a blob, or the file would disappear from the partition.
FROM_SOURCE = {
    '/lib/android.hardware.common-V2-ndk.so',
    '/lib/android.hardware.graphics.allocator-V2-ndk.so',
    '/lib/libaconfig_storage_read_api_cc.so',
    '/lib/libavservices_minijail.so',
    '/lib/libbase.so',
    '/lib/libbinder.so',
    '/lib/libcap.so',
    '/lib/libcutils.so',
    '/lib/libexpat.so',
    '/lib/libgralloctypes.so',
    '/lib/libhidlbase.so',
    '/lib/libhidlmemory.so',
    '/lib/libminijail.so',
    '/lib/libstagefright_foundation.so',
    '/lib/libui.so',
    '/lib/libutils.so',
    '/lib64/libbase.so',
    '/lib64/libcutils.so',
    '/lib64/libhidlbase.so',
    '/lib64/libutils.so',
}
UNUSABLE_SYMLINKS = {
    '/bin/[',
    '/lib64/hw/android.hardware.camera.provider@2.6-impl-mediatek.so',
    '/lib64/hw/vendor.mediatek.hardware.camera.ccap@1.0-impl.so',
    '/lib64/hw/vendor.mediatek.hardware.camera.isphal_aidl@1.0-impl.so',
}

# names of modules the source tree defines (any partition), and of modules that only exist for
# system_ext - those two sets decide about MODULE=/MAKE_COPY_RULE_ONLY
BLOCK = re.compile(r'^([A-Za-z_][\w]*)\s*\{\s*$')
NAME = re.compile(r'^\s*name:\s*"([^"]+)"', re.M)
SKIP_DIRS = {'.repo', 'out', '.git'}
mods, system_ext_only = set(), set()
for root, dirs, files in os.walk(TREE):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    if root.startswith(os.path.join(TREE, 'vendor/xiaomi/emerald')):
        # our own blob repo: its module names are the file names, they would collide with themselves
        continue
    if 'Android.bp' not in files:
        continue
    try:
        lines = open(os.path.join(root, 'Android.bp'), encoding='utf-8', errors='replace').read().splitlines()
    except OSError:
        continue
    i = 0
    while i < len(lines):
        m = BLOCK.match(lines[i])
        if not m:
            i += 1
            continue
        depth, j = 0, i
        while j < len(lines):
            depth += lines[j].count('{') - lines[j].count('}')
            if depth <= 0 and j > i:
                break
            j += 1
        body = '\n'.join(lines[i:j + 1])
        nm = NAME.search(body)
        if nm:
            name = nm.group(1)
            mods.add(name)
            if re.search(r'^\s*system_ext_specific:\s*true', body, re.M):
                system_ext_only.add(name)
        i = j + 1

files = [l.split('\t')[0] for l in open(META)
         if l.split('\t')[1] == 'regular file' and l.split('\t')[0] != '/build.prop']
# the static RROs under /overlay/*.apk are not listed either: a prebuilt APK cannot be a copy rule and
# extract-utils cannot emit prebuilt_overlay, so the files are kept in the device tree
# (prebuilts/overlays/) and installed by the modules there.
files = [f for f in files if f not in TREE_PROVIDED and f not in FROM_SOURCE
         and not (f.startswith('/overlay/') and f.endswith('.apk'))]
files.sort()
fileset = set(files)

links = {}
left_out = []
for line in open(META):
    path, typ = line.split('\t')[:2]
    if typ != 'symlink file' or path in UNUSABLE_SYMLINKS:
        continue
    target = os.readlink(ROOT + path)
    if target.startswith('/'):
        resolved = target[len('/vendor'):] if target.startswith('/vendor/') else None
    else:
        resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
    if resolved in fileset:
        links.setdefault(resolved, []).append(path)
    else:
        left_out.append((path, target))

with open(OUT, 'a') as f:
    f.write('\n# Vendor partition: everything inside the stock OS3.0.305.0.WNFMIXM vendor.img (5222 files, 740 symlinks).\n')
    f.write('# Source: a dump whose vendor/ directory is the image unpacked with fsck.erofs; build.prop is not\n')
    f.write('# listed (the build writes it from vendor/xiaomi/emerald/vendor.prop). Four files come from the\n')
    f.write('# device tree instead, see device.mk: the health HAL binary and its vintf fragment, the media\n')
    f.write('# profiles and the fstab. Symlinks are install_symlink rules on the target lines (absolute /vendor\n')
    f.write('# paths), except six that device/xiaomi/emerald/vendor_symlinks/Android.bp writes by hand: four\n')
    f.write('# names soong cannot use, and two whose targets are not files of the partition.\n')
    f.write('# MODULE=emerald_blob_<name> keeps the file name (stem) while giving the prebuilt module a name no\n')
    f.write('# module of the source tree has; MAKE_COPY_RULE_ONLY installs a file without a module.\n')
    f.write('# %d libraries are not listed: the platform installs its own build of them into the vendor image\n' % len(FROM_SOURCE))
    f.write('# (FROM_SOURCE in vendor-blobs/list.py, see there for why and for the ABI check).\n')
    f.write('# The static RROs (/overlay/*.apk) are in the device tree: prebuilts/overlays/.\n')
    marked = copied = 0
    for path in files:
        name = os.path.basename(path)
        base = name[:-3] if name.endswith('.so') else name
        args = []
        symlinks = links.get(path, [])
        if symlinks:
            args.append('SYMLINK=' + ','.join('vendor' + s for s in sorted(symlinks)))
        invalid = not re.fullmatch(r'[A-Za-z0-9_.-]+', base)
        # a file whose module name (the generator names prebuilt_etc/apex modules after the file) is
        # already a module of the source tree cannot be a module: kati refuses two definitions of the
        # same name in one partition (android.hardware.audio.service-aidl.xml, manifest.xml,
        # com.android.hardware.cas, ...). Install those as plain copies, like the binaries below.
        collides = not name.endswith('.so') and (
            name in mods or base in mods or os.path.splitext(name)[0] in mods)
        # shell scripts: the generated sh_binary ignores MODULE/stem, so a name clash cannot be avoided
        # by renaming the module - install them as plain files (fs_config gives the stock mode)
        # binaries and scripts: the generated sh_binary/prebuilt writers ignore MODULE/stem, so a name
        # clash cannot be fixed by renaming the module - install them as plain files instead (fs_config
        # gives the stock owner and mode)
        if (path in COPY_RULE_ONLY or base in system_ext_only or invalid or collides
                or '/bin/' in path or path.startswith('/odm/')):
            args.append('MAKE_COPY_RULE_ONLY')
            copied += 1
        elif name.endswith('.so'):
            args.append('MODULE=emerald_blob_' + re.sub(r'[^A-Za-z0-9_.-]', '.', base))
            # the modules are renamed, so the shared_libs the generator derives from the ELF files would
            # point at names that no longer exist (and at MTK libraries named differently); the blobs do
            # not participate in the build, so drop the dependency lists
            args.append('DISABLE_DEPS')
            marked += 1
        f.write('vendor' + path + ('' if not args else ';' + ';'.join(args)) + '\n')

print(f'файлов: {len(files)}, MODULE=: {marked}, copy-rule: {copied}, '
      f'симлинков: {sum(len(v) for v in links.values())}, не воспроизводим: {len(left_out)}')
for item in left_out:
    print('   ', item)
print(f'модулей в дереве: {len(mods)}', file=sys.stderr)
