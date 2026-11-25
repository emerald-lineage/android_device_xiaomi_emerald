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
  * libraries that exist in the tree only as system_ext modules are plain copies too;
  * paths the platform installs into the vendor image itself are not listed at all (FROM_SOURCE, 408 of
    them): soong packs the vendor variant of every vendor_available module in PRODUCT_PACKAGES, and a
    second rule for the same path is a kati error.
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

# Paths the platform itself installs into the vendor image: soong packs the vendor variant of every
# vendor_available module listed in PRODUCT_PACKAGES (base_system.mk lists libbase, libcutils, libbinder,
# libui, ...), and a blob for the same path is a hard kati conflict ("overriding commands for target").
# PRODUCT_PACKAGES cannot keep a module out of one partition ("-module" arrives verbatim, and a
# filter-out in a product makefile runs before the inherited lists are merged); `overrides` drops a
# module from every partition at once, so it is no option for a library the system image needs too.
# So these paths come from the source tree, not from the image.
#
# 401 paths in two waves: 20 that clashed as modules of the same name, then 388 that kati reported
# twice on the first vendorimage build that got through soong (25.11, 19:47), minus the seven below.
# All of them are the stock vendor's copies of libraries the tree builds from AOSP or MediaTek open
# source (hardware/interfaces, hardware/mediatek, hardware/nxp, frameworks/av, system/core, ...).
#
# The four exceptions (seven paths) stay blobs, because the stock copies are built from MediaTek's or
# the chip vendor's own sources and flags: libaedv (the AEE library 73 stock AEE tools link against;
# strings show vendor/mediatek/proprietary/aee_sec), audio.bluetooth.default and
# vendor.mediatek.hardware.bluetooth.audio-V1-ndk (MTK's Bluetooth audio HAL and its interface, source
# paths under vendor/mediatek/proprietary/packages/modules/Bluetooth), and nfc_nci_nxp_snxxx_v2 (NXP
# NFC HAL: the tree builds it with its own cflags and source version, and a wrong firmware download
# breaks NFC). The tree builds its own versions of these modules, so they are listed in `overrides` of
# emerald_vendor_platform_override (../vendor-image/Android.bp) instead: none of them is in
# PRODUCT_PACKAGES, they only arrive as dependency installs, and fsgen drops a dependency of the
# vendor image when another installed module overrides it.
# ABI: for the first 20, readelf -Ws over all 3762 stock files of vendor/lib*, vendor/bin showed that no
# stock file imports a symbol the newer (Android 17 vs stock 16) build lacks - docs/plan-2.24.md. The
# rest get the same check over the built vendor image before it goes to a phone.
#
# Regenerate after a build reports more duplicates: README.md, "FROM_SOURCE".
FROM_SOURCE = {
    '/lib/android.frameworks.sensorservice-V1-ndk.so',
    '/lib/android.hardware.audio.common-V3-ndk.so',
    '/lib/android.hardware.audio.common-V4-ndk.so',
    '/lib/android.hardware.audio.common-util.so',
    '/lib/android.hardware.audio.core-V3-ndk.so',
    '/lib/android.hardware.audio.core.sounddose-V3-ndk.so',
    '/lib/android.hardware.audio.effect-V2-ndk.so',
    '/lib/android.hardware.audio.effect-V3-ndk.so',
    '/lib/android.hardware.bluetooth.audio-V4-ndk.so',
    '/lib/android.hardware.bluetooth.audio-V5-ndk.so',
    '/lib/android.hardware.common-V2-ndk.so',
    '/lib/android.hardware.common.fmq-V1-ndk.so',
    '/lib/android.hardware.graphics.allocator-V2-ndk.so',
    '/lib/android.hardware.graphics.common-V6-ndk.so',
    '/lib/android.hardware.media.bufferpool2-V2-ndk.so',
    '/lib/android.hardware.media.c2-V1-ndk.so',
    '/lib/android.hardware.sensors-V2-ndk.so',
    '/lib/android.hardware.sensors-V3-ndk.so',
    '/lib/android.hardware.soundtrigger3-V3-ndk.so',
    '/lib/android.media.audio.common.types-V3-ndk.so',
    '/lib/android.media.audio.common.types-V4-ndk.so',
    '/lib/android.media.audio.eraser.types-V1-ndk.so',
    '/lib/android.media.soundtrigger.types-V3-ndk.so',
    '/lib/android.system.suspend-V1-ndk.so',
    '/lib/hw/audio.primary.default.so',
    '/lib/hw/audio.r_submix.default.so',
    '/lib/hw/audio.usb.default.so',
    '/lib/hw/audio_policy.stub.so',
    '/lib/hw/gralloc.default.so',
    '/lib/hw/local_time.default.so',
    '/lib/hw/power.default.so',
    '/lib/hw/sensors.dynamic_sensor_hal.so',
    '/lib/hw/vibrator.default.so',
    '/lib/libRSCpuRef.so',
    '/lib/libRSDriver.so',
    '/lib/libRS_internal.so',
    '/lib/libaconfig_storage_read_api_cc.so',
    '/lib/libalsautils.so',
    '/lib/libalsautilsv2.so',
    '/lib/libaudio_aidl_conversion_common_ndk.so',
    '/lib/libaudioaidlcommon.so',
    '/lib/libaudioutils.so',
    '/lib/libavservices_minijail.so',
    '/lib/libbase.so',
    '/lib/libbcinfo.so',
    '/lib/libbinder.so',
    '/lib/libblas.so',
    '/lib/libbluetooth_audio_session.so',
    '/lib/libbluetooth_audio_session_aidl.so',
    '/lib/libcap.so',
    '/lib/libclang_rt.ubsan_standalone-arm-android.so',
    '/lib/libcodec2.so',
    '/lib/libcodec2_aidl.so',
    '/lib/libcodec2_hal_common.so',
    '/lib/libcodec2_hidl_plugin.so',
    '/lib/libcodec2_soft_common.so',
    '/lib/libcodec2_vndk.so',
    '/lib/libcompiler_rt.so',
    '/lib/libcrypto.so',
    '/lib/libcurl.so',
    '/lib/libcutils.so',
    '/lib/libdmabufheap.so',
    '/lib/libdrm.so',
    '/lib/libeffects.so',
    '/lib/libeffectsconfig.so',
    '/lib/libexpat.so',
    '/lib/libflatbuffers-cpp.so',
    '/lib/libfmq.so',
    '/lib/libgralloctypes.so',
    '/lib/libhardware.so',
    '/lib/libhardware_legacy.so',
    '/lib/libhidlbase.so',
    '/lib/libhidlmemory.so',
    '/lib/libhidltransport.so',
    '/lib/libhidparser.so',
    '/lib/libhwbinder.so',
    '/lib/libion.so',
    '/lib/libjsoncpp.so',
    '/lib/libkeystore-wifi-hidl.so',
    '/lib/libladder.so',
    '/lib/liblzma.so',
    '/lib/libmedia_helper.so',
    '/lib/libmediautils_vendor.so',
    '/lib/libmemunreachable.so',
    '/lib/libminijail.so',
    '/lib/libnbaio_mono.so',
    '/lib/libnetutils.so',
    '/lib/libpcap.so',
    '/lib/libpng.so',
    '/lib/libpower.so',
    '/lib/libprocessgroup.so',
    '/lib/libprotobuf-cpp-full-21.12.so',
    '/lib/libreference-ril.so',
    '/lib/libril.so',
    '/lib/librilutils.so',
    '/lib/libruy.so',
    '/lib/libsensorndkbridge.so',
    '/lib/libsfplugin_ccodec_utils.so',
    '/lib/libspeexresampler.so',
    '/lib/libsqlite.so',
    '/lib/libssl.so',
    '/lib/libstagefright_aidl_bufferpool2.so',
    '/lib/libstagefright_foundation.so',
    '/lib/libsysutils.so',
    '/lib/libtextclassifier_hash.so',
    '/lib/libtinyalsa.so',
    '/lib/libtinyalsav2.so',
    '/lib/libtinycompress.so',
    '/lib/libtinyxml2.so',
    '/lib/libui.so',
    '/lib/libunwindstack.so',
    '/lib/libutils.so',
    '/lib/libutilscallstack.so',
    '/lib/libvibratorutils.so',
    '/lib/libwpa_client.so',
    '/lib/libxml2.so',
    '/lib/libz.so',
    '/lib/mediacas/libclearkeycasplugin.so',
    '/lib/mediadrm/libdrmclearkeyplugin.so',
    '/lib/mediadrm/libmockdrmcryptoplugin.so',
    '/lib/server_configurable_flags.so',
    '/lib/soundfx/libaecsw.so',
    '/lib/soundfx/libagc1sw.so',
    '/lib/soundfx/libagc2sw.so',
    '/lib/soundfx/libaudiopreprocessing.so',
    '/lib/soundfx/libbassboostsw.so',
    '/lib/soundfx/libbundleaidl.so',
    '/lib/soundfx/libbundlewrapper.so',
    '/lib/soundfx/libdownmix.so',
    '/lib/soundfx/libdownmixaidl.so',
    '/lib/soundfx/libdynamicsprocessingaidl.so',
    '/lib/soundfx/libdynproc.so',
    '/lib/soundfx/libeffectproxy.so',
    '/lib/soundfx/libenvreverbsw.so',
    '/lib/soundfx/libequalizersw.so',
    '/lib/soundfx/libextensioneffect.so',
    '/lib/soundfx/libhapticgenerator.so',
    '/lib/soundfx/libhapticgeneratoraidl.so',
    '/lib/soundfx/libldnhncr.so',
    '/lib/soundfx/libloudnessenhanceraidl.so',
    '/lib/soundfx/libnssw.so',
    '/lib/soundfx/libpreprocessingaidl.so',
    '/lib/soundfx/libpresetreverbsw.so',
    '/lib/soundfx/libreverbaidl.so',
    '/lib/soundfx/libreverbwrapper.so',
    '/lib/soundfx/libvirtualizersw.so',
    '/lib/soundfx/libvisualizer.so',
    '/lib/soundfx/libvisualizeraidl.so',
    '/lib/soundfx/libvolumesw.so',
    '/lib/vendor.mediatek.hardware.audio-V1-ndk.so',
    '/lib/vendor.mediatek.hardware.mtkpower-V2-ndk.so',
    '/lib64/android.frameworks.sensorservice-V1-ndk.so',
    '/lib64/android.frameworks.stats-V1-ndk.so',
    '/lib64/android.frameworks.stats-V2-ndk.so',
    '/lib64/android.hardware.audio.common-V3-ndk.so',
    '/lib64/android.hardware.audio.common-V4-ndk.so',
    '/lib64/android.hardware.audio.common-util.so',
    '/lib64/android.hardware.audio.core-V3-ndk.so',
    '/lib64/android.hardware.audio.core.sounddose-V3-ndk.so',
    '/lib64/android.hardware.audio.effect-V2-ndk.so',
    '/lib64/android.hardware.audio.effect-V3-ndk.so',
    '/lib64/android.hardware.biometrics.common-V4-ndk.so',
    '/lib64/android.hardware.biometrics.common.thread.so',
    '/lib64/android.hardware.biometrics.common.util.so',
    '/lib64/android.hardware.biometrics.fingerprint-V4-ndk.so',
    '/lib64/android.hardware.bluetooth-V1-ndk.so',
    '/lib64/android.hardware.bluetooth.audio-V4-ndk.so',
    '/lib64/android.hardware.bluetooth.audio-V5-ndk.so',
    '/lib64/android.hardware.bluetooth.finder-V1-ndk.so',
    '/lib64/android.hardware.bluetooth.ranging-V1-ndk.so',
    '/lib64/android.hardware.boot-V1-ndk.so',
    '/lib64/android.hardware.camera.common-V1-ndk.so',
    '/lib64/android.hardware.camera.common-V2-ndk.so',
    '/lib64/android.hardware.camera.device-V3-ndk.so',
    '/lib64/android.hardware.camera.metadata-V3-ndk.so',
    '/lib64/android.hardware.camera.provider-V3-ndk.so',
    '/lib64/android.hardware.common-V2-ndk.so',
    '/lib64/android.hardware.common.fmq-V1-ndk.so',
    '/lib64/android.hardware.contexthub-V4-ndk.so',
    '/lib64/android.hardware.drm-V1-ndk.so',
    '/lib64/android.hardware.drm.common-V1-ndk.so',
    '/lib64/android.hardware.dumpstate-V1-ndk.so',
    '/lib64/android.hardware.gatekeeper-V1-ndk.so',
    '/lib64/android.hardware.gnss-V5-ndk.so',
    '/lib64/android.hardware.graphics.allocator-V2-ndk.so',
    '/lib64/android.hardware.graphics.common-V5-ndk.so',
    '/lib64/android.hardware.graphics.common-V6-ndk.so',
    '/lib64/android.hardware.graphics.composer3-V2-ndk.so',
    '/lib64/android.hardware.graphics.composer3-V3-ndk.so',
    '/lib64/android.hardware.graphics.composer3-V4-ndk.so',
    '/lib64/android.hardware.health-V1-ndk.so',
    '/lib64/android.hardware.health-V4-ndk.so',
    '/lib64/android.hardware.ir-V1-ndk.so',
    '/lib64/android.hardware.keymaster-V4-ndk.so',
    '/lib64/android.hardware.light-V1-ndk.so',
    '/lib64/android.hardware.light-V2-ndk.so',
    '/lib64/android.hardware.media.bufferpool2-V2-ndk.so',
    '/lib64/android.hardware.media.c2-V1-ndk.so',
    '/lib64/android.hardware.memtrack-V1-ndk.so',
    '/lib64/android.hardware.nfc-V1-ndk.so',
    '/lib64/android.hardware.nfc-V2-ndk.so',
    '/lib64/android.hardware.power-V4-ndk.so',
    '/lib64/android.hardware.power-V6-ndk.so',
    '/lib64/android.hardware.radio-V4-ndk.so',
    '/lib64/android.hardware.radio.config-V4-ndk.so',
    '/lib64/android.hardware.radio.data-V4-ndk.so',
    '/lib64/android.hardware.radio.ims-V3-ndk.so',
    '/lib64/android.hardware.radio.messaging-V4-ndk.so',
    '/lib64/android.hardware.radio.modem-V4-ndk.so',
    '/lib64/android.hardware.radio.network-V4-ndk.so',
    '/lib64/android.hardware.radio.sap-V1-ndk.so',
    '/lib64/android.hardware.radio.sim-V4-ndk.so',
    '/lib64/android.hardware.radio.voice-V4-ndk.so',
    '/lib64/android.hardware.secure_element-V1-ndk.so',
    '/lib64/android.hardware.security.keymint-V1-ndk.so',
    '/lib64/android.hardware.security.keymint-V3-ndk.so',
    '/lib64/android.hardware.security.keymint-V4-ndk.so',
    '/lib64/android.hardware.security.rkp-V3-ndk.so',
    '/lib64/android.hardware.security.secureclock-V1-ndk.so',
    '/lib64/android.hardware.security.sharedsecret-V1-ndk.so',
    '/lib64/android.hardware.sensors-V2-ndk.so',
    '/lib64/android.hardware.sensors-V3-ndk.so',
    '/lib64/android.hardware.soundtrigger3-V1-ndk.so',
    '/lib64/android.hardware.soundtrigger3-V3-ndk.so',
    '/lib64/android.hardware.tetheroffload-V1-ndk.so',
    '/lib64/android.hardware.usb-V3-ndk.so',
    '/lib64/android.hardware.usb.gadget-V1-ndk.so',
    '/lib64/android.hardware.vibrator-V1-ndk.so',
    '/lib64/android.hardware.wifi-V3-ndk.so',
    '/lib64/android.hardware.wifi.common-V2-ndk.so',
    '/lib64/android.hardware.wifi.hostapd-V3-ndk.so',
    '/lib64/android.hardware.wifi.supplicant-V4-ndk.so',
    '/lib64/android.media.audio.common.types-V2-ndk.so',
    '/lib64/android.media.audio.common.types-V3-ndk.so',
    '/lib64/android.media.audio.common.types-V4-ndk.so',
    '/lib64/android.media.audio.eraser.types-V1-ndk.so',
    '/lib64/android.media.soundtrigger.types-V1-ndk.so',
    '/lib64/android.media.soundtrigger.types-V3-ndk.so',
    '/lib64/android.system.keystore2-V1-ndk.so',
    '/lib64/android.system.suspend-V1-ndk.so',
    '/lib64/chre_atoms_log.so',
    '/lib64/chremetrics-cpp.so',
    '/lib64/hw/audio.primary.default.so',
    '/lib64/hw/audio.r_submix.default.so',
    '/lib64/hw/audio.usb.default.so',
    '/lib64/hw/audio_policy.stub.so',
    '/lib64/hw/gralloc.default.so',
    '/lib64/hw/local_time.default.so',
    '/lib64/hw/power.default.so',
    '/lib64/hw/sensors.dynamic_sensor_hal.so',
    '/lib64/hw/vibrator.default.so',
    '/lib64/libRSCpuRef.so',
    '/lib64/libRSDriver.so',
    '/lib64/libRS_internal.so',
    '/lib64/lib_android_keymaster_keymint_utils.so',
    '/lib64/libaconfig_storage_read_api_cc.so',
    '/lib64/libalsautils.so',
    '/lib64/libalsautilsv2.so',
    '/lib64/libaudio_aidl_conversion_common_ndk.so',
    '/lib64/libaudioaidlcommon.so',
    '/lib64/libaudioutils.so',
    '/lib64/libavservices_minijail.so',
    '/lib64/libbase.so',
    '/lib64/libbcinfo.so',
    '/lib64/libbinder.so',
    '/lib64/libbinderdebug.so',
    '/lib64/libblas.so',
    '/lib64/libbluetooth_audio_session.so',
    '/lib64/libbluetooth_audio_session_aidl.so',
    '/lib64/libcap.so',
    '/lib64/libclang_rt.ubsan_standalone-aarch64-android.so',
    '/lib64/libcodec2.so',
    '/lib64/libcodec2_aidl.so',
    '/lib64/libcodec2_hal_common.so',
    '/lib64/libcodec2_hidl_plugin.so',
    '/lib64/libcodec2_soft_common.so',
    '/lib64/libcodec2_vndk.so',
    '/lib64/libcompiler_rt.so',
    '/lib64/libcppbor.so',
    '/lib64/libcppbor_external.so',
    '/lib64/libcppcose_rkp.so',
    '/lib64/libcrypto.so',
    '/lib64/libcurl.so',
    '/lib64/libcutils.so',
    '/lib64/libdmabufheap.so',
    '/lib64/libdrm.so',
    '/lib64/libdumpstateutil.so',
    '/lib64/libeffects.so',
    '/lib64/libeffectsconfig.so',
    '/lib64/libexif.so',
    '/lib64/libexpat.so',
    '/lib64/libflatbuffers-cpp.so',
    '/lib64/libfmq.so',
    '/lib64/libgatekeeper.so',
    '/lib64/libgralloctypes.so',
    '/lib64/libgrallocusage.so',
    '/lib64/libhardware.so',
    '/lib64/libhardware_legacy.so',
    '/lib64/libhidlbase.so',
    '/lib64/libhidlmemory.so',
    '/lib64/libhidltransport.so',
    '/lib64/libhidparser.so',
    '/lib64/libhwbinder.so',
    '/lib64/libimage_io.so',
    '/lib64/libion.so',
    '/lib64/libjpeg.so',
    '/lib64/libjpegdecoder.so',
    '/lib64/libjpegencoder.so',
    '/lib64/libjsoncpp.so',
    '/lib64/libkeymaster4support.so',
    '/lib64/libkeymaster_messages.so',
    '/lib64/libkeymaster_portable.so',
    '/lib64/libkeymint.so',
    '/lib64/libkeymint_remote_prov_support.so',
    '/lib64/libkeymint_support.so',
    '/lib64/libkeystore-engine-wifi-hidl.so',
    '/lib64/libkeystore-wifi-hidl.so',
    '/lib64/libladder.so',
    '/lib64/liblzma.so',
    '/lib64/libmedia_helper.so',
    '/lib64/libmediautils_vendor.so',
    '/lib64/libmeminfo.so',
    '/lib64/libmemunreachable.so',
    '/lib64/libminijail.so',
    '/lib64/libnbaio_mono.so',
    '/lib64/libnetutils.so',
    '/lib64/libnl.so',
    '/lib64/libpcap.so',
    '/lib64/libpng.so',
    '/lib64/libpower.so',
    '/lib64/libprocessgroup.so',
    '/lib64/libprocinfo.so',
    '/lib64/libprotobuf-cpp-full-21.12.so',
    '/lib64/libpuresoftkeymasterdevice.so',
    '/lib64/libreference-ril.so',
    '/lib64/libril.so',
    '/lib64/librilutils.so',
    '/lib64/libruy.so',
    '/lib64/libsensorndkbridge.so',
    '/lib64/libsfplugin_ccodec_utils.so',
    '/lib64/libsoft_attestation_cert.so',
    '/lib64/libspeexresampler.so',
    '/lib64/libsqlite.so',
    '/lib64/libssl.so',
    '/lib64/libstagefright_aidl_bufferpool2.so',
    '/lib64/libstagefright_bufferqueue_helper.so',
    '/lib64/libstagefright_foundation.so',
    '/lib64/libsysutils.so',
    '/lib64/libtextclassifier_hash.so',
    '/lib64/libtinyalsa.so',
    '/lib64/libtinyalsav2.so',
    '/lib64/libtinycompress.so',
    '/lib64/libtinyxml2.so',
    '/lib64/libtrusty.so',
    '/lib64/libui.so',
    '/lib64/libultrahdr.so',
    '/lib64/libunwindstack.so',
    '/lib64/libutils.so',
    '/lib64/libutilscallstack.so',
    '/lib64/libvibratorutils.so',
    '/lib64/libwifi-hal.so',
    '/lib64/libwifi-system-iface.so',
    '/lib64/libwpa_client.so',
    '/lib64/libxml2.so',
    '/lib64/libz.so',
    '/lib64/mediacas/libclearkeycasplugin.so',
    '/lib64/mediadrm/libdrmclearkeyplugin.so',
    '/lib64/mediadrm/libmockdrmcryptoplugin.so',
    '/lib64/server_configurable_flags.so',
    '/lib64/soundfx/libaecsw.so',
    '/lib64/soundfx/libagc1sw.so',
    '/lib64/soundfx/libagc2sw.so',
    '/lib64/soundfx/libaudiopreprocessing.so',
    '/lib64/soundfx/libbassboostsw.so',
    '/lib64/soundfx/libbundleaidl.so',
    '/lib64/soundfx/libbundlewrapper.so',
    '/lib64/soundfx/libdownmix.so',
    '/lib64/soundfx/libdownmixaidl.so',
    '/lib64/soundfx/libdynamicsprocessingaidl.so',
    '/lib64/soundfx/libdynproc.so',
    '/lib64/soundfx/libeffectproxy.so',
    '/lib64/soundfx/libenvreverbsw.so',
    '/lib64/soundfx/libequalizersw.so',
    '/lib64/soundfx/libextensioneffect.so',
    '/lib64/soundfx/libhapticgenerator.so',
    '/lib64/soundfx/libhapticgeneratoraidl.so',
    '/lib64/soundfx/libldnhncr.so',
    '/lib64/soundfx/libloudnessenhanceraidl.so',
    '/lib64/soundfx/libnssw.so',
    '/lib64/soundfx/libpreprocessingaidl.so',
    '/lib64/soundfx/libpresetreverbsw.so',
    '/lib64/soundfx/libreverbaidl.so',
    '/lib64/soundfx/libreverbwrapper.so',
    '/lib64/soundfx/libvirtualizersw.so',
    '/lib64/soundfx/libvisualizer.so',
    '/lib64/soundfx/libvisualizeraidl.so',
    '/lib64/soundfx/libvolumesw.so',
    '/lib64/vendor.mediatek.hardware.audio-V1-ndk.so',
    '/lib64/vendor.mediatek.hardware.mtkpower-V1-ndk.so',
    '/lib64/vendor.mediatek.hardware.mtkpower-V2-ndk.so',
    '/lib64/vendor.nxp.nxpnfc_aidl-V1-ndk.so',
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
