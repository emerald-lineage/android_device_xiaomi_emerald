#!/usr/bin/env python3
"""Write the vendor part of device/xiaomi/emerald/proprietary-files.txt from the stock image.

See README.md next to this file: it documents the preparation commands, the rules and why they exist.

Rules, all applied from scratch so the result does not depend on earlier fixes:
  * every regular file of the stock vendor.img is listed (build.prop is not: the build writes it);
  * four files are provided by the device tree instead (health HAL binary + its vintf fragment,
    media_profiles_V1_0.xml, fstab.mt6789) - they are not listed;
  * symlinks that point at listed files become SYMLINK arguments on the target line, except the three
    with names soong cannot use (`@`) - those are written by hand in vendor_symlinks/Android.bp -
    and the two that point at a directory or into vendor_dlkm;
  * files soong has no package rule for (odm/*, overlay/*.apk) and the two 32-bit libraries whose 64-bit
    twin takes the module name are installed as plain copies (MAKE_COPY_RULE_ONLY);
  * every library whose name also exists as a module in the source tree gets its own module name
    (MODULE=emerald_blob_...) with the file name kept by stem, so a blob never fights a source module
    for the vendor partition (AIDL/HIDL interface libraries, vendor_available libraries);
  * libraries that exist in the tree only as system_ext modules are plain copies too;
  * paths the platform installs into the vendor image itself are not listed at all (FROM_SOURCE, 647 of
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

# Paths the platform installs into the vendor image itself. Two mechanisms write the same output path:
# soong packs the vendor variant of every vendor_available module of PRODUCT_PACKAGES (and installs its
# dependencies), and PRODUCT_COPY_FILES of the generated vendor makefile copies the file directly. A
# blob for such a path is a hard kati error ("overriding commands for target"), and it cannot be
# suppressed for one partition: PRODUCT_PACKAGES has no "-module" syntax, a filter-out in a product
# makefile runs before the inherited lists are merged, and `overrides` only affects fsgen packing - the
# install rule still comes from the module itself (checked 25.11: passwd_vendor and toybox_vendor stayed
# installed while listed in `overrides` of the phony module we had). So these paths come from the source
# tree, not from the image: 647 of them - 401 from the first wave (20 name clashes, 388 reported by kati
# on the first vendorimage build that got through soong, 25.11 19:47, minus 7 kept as blobs back then),
# 245 found by comparing the final list against installs-lineage_emerald.mk (vendor paths this list
# still wrote while the platform installed them, both module and copy-rule ones), 2 more libmnl
# (mt6789 copies: the platform's libmnl.so clashed with our symlinks), and minus the Widevine apex,
# which only we install, so it stays a blob.
#
# The stock copies of libaedv, audio.bluetooth.default, vendor.mediatek.hardware.bluetooth.audio-V1-ndk
# (both bitnesses) and nfc_nci_nxp_snxxx_v2 are built from MediaTek's and NXP's own sources, so the
# image keeps the tree's Android 17 build of them instead of the stock one - a conscious trade (option
# "the platform owns what it installs", user 25.11): the alternative, a phony `overrides` module, does
# not remove the install rule and cannot pass kati.
# ABI: for the first 20, readelf -Ws over all 3762 stock files of vendor/lib*, vendor/bin showed that no
# stock file imports a symbol the newer (Android 17 vs stock 16) build lacks - docs/plan-2.24.md. The
# whole image gets the same check before it goes to a phone.
#
# Regenerate after a build reports more duplicates: README.md, "FROM_SOURCE".
FROM_SOURCE = {
    '/apex/com.android.hardware.cas.apex',
    '/bin/awk',
    '/bin/boringssl_self_test32',
    '/bin/boringssl_self_test64',
    '/bin/chipinfo',
    '/bin/conninfra_loader',
    '/bin/dmabuf_dump',
    '/bin/dumpsys',
    '/bin/hs20-osu-client',
    '/bin/hw/android.hardware.contexthub-service.tinysys',
    '/bin/hw/android.hardware.drm-service.clearkey',
    '/bin/hw/android.hardware.ir-service.example',
    '/bin/hw/android.hardware.memtrack-service.mediatek',
    '/bin/hw/android.hardware.nfc2-service.nxp',
    '/bin/hw/android.hardware.sensors-service.multihal',
    '/bin/hw/android.hardware.thermal-service.mediatek',
    '/bin/hw/android.hardware.wifi-service-lazy',
    '/bin/hw/wpa_supplicant',
    '/bin/logwrapper',
    '/bin/sh',
    '/bin/toolbox',
    '/bin/toybox_vendor',
    '/bin/trusty-ut-ctrl',
    '/bin/vndservice',
    '/bin/vndservicemanager',
    '/bin/wlan_assistant',
    '/bin/wpa_cli',
    '/etc/NOTICE.xml.gz',
    '/etc/aidl/hfp/hfp_codec_capabilities.xml',
    '/etc/aidl/le_audio/aidl_audio_set_configurations.bfbs',
    '/etc/aidl/le_audio/aidl_audio_set_scenarios.bfbs',
    '/etc/aidl/le_audio/aidl_default_audio_set_configurations.json',
    '/etc/aidl/le_audio/aidl_default_audio_set_scenarios.json',
    '/etc/boringssl_self_test.zygote64.rc',
    '/etc/boringssl_self_test.zygote64_32.rc',
    '/etc/build_flags.json',
    '/etc/fs_config_dirs',
    '/etc/fs_config_files',
    '/etc/group',
    '/etc/init/android.hardware.drm-service.clearkey.rc',
    '/etc/init/android.hardware.health-service.example.rc',
    '/etc/init/android.hardware.ir-service.example.rc',
    '/etc/init/android.hardware.sensors-service-multihal.rc',
    '/etc/init/android.hardware.wifi-service-lazy.rc',
    '/etc/init/boringssl_self_test.rc',
    '/etc/init/hw/init.mt6789.usb.rc',
    '/etc/init/memtrack-mediatek.rc',
    '/etc/init/nfc2-service-nxp.rc',
    '/etc/init/vndservicemanager.rc',
    '/etc/init/wlan_assistant.rc',
    '/etc/mkshrc',
    '/etc/passwd',
    '/etc/permissions/android.hardware.audio.low_latency.prebuilt.xml',
    '/etc/permissions/android.hardware.bluetooth_le.prebuilt.xml',
    '/etc/permissions/android.hardware.consumerir.prebuilt.xml',
    '/etc/permissions/android.hardware.faketouch.prebuilt.xml',
    '/etc/permissions/android.hardware.hardware_keystore.xml',
    '/etc/permissions/android.hardware.location.gps.prebuilt.xml',
    '/etc/permissions/android.hardware.sensor.accelerometer.prebuilt.xml',
    '/etc/permissions/android.hardware.sensor.compass.prebuilt.xml',
    '/etc/permissions/android.hardware.sensor.gyroscope.prebuilt.xml',
    '/etc/permissions/android.hardware.sensor.light.prebuilt.xml',
    '/etc/permissions/android.hardware.sensor.proximity.prebuilt.xml',
    '/etc/permissions/android.hardware.sensor.stepcounter.prebuilt.xml',
    '/etc/permissions/android.hardware.sensor.stepdetector.prebuilt.xml',
    '/etc/permissions/android.hardware.telephony.ims.prebuilt.xml',
    '/etc/permissions/android.hardware.touchscreen.multitouch.distinct.prebuilt.xml',
    '/etc/permissions/android.hardware.usb.accessory.prebuilt.xml',
    '/etc/permissions/android.hardware.usb.host.prebuilt.xml',
    '/etc/permissions/android.hardware.vulkan.compute-0.prebuilt.xml',
    '/etc/permissions/android.hardware.vulkan.level-1.prebuilt.xml',
    '/etc/permissions/android.hardware.vulkan.version-1_3.prebuilt.xml',
    '/etc/permissions/android.hardware.wifi.passpoint.prebuilt.xml',
    '/etc/permissions/android.software.device_id_attestation.prebuilt.xml',
    '/etc/permissions/android.software.ipsec_tunnels.prebuilt.xml',
    '/etc/permissions/android.software.verified_boot.prebuilt.xml',
    '/etc/permissions/features_com.android.virt.xml',
    '/etc/permissions/handheld_core_hardware.prebuilt.xml',
    '/etc/selinux/genfs_labels_version.txt',
    '/etc/selinux/plat_pub_versioned.cil',
    '/etc/selinux/plat_sepolicy_vers.txt',
    '/etc/selinux/precompiled_sepolicy',
    '/etc/selinux/precompiled_sepolicy.plat_sepolicy_and_mapping.sha256',
    '/etc/selinux/precompiled_sepolicy.system_ext_sepolicy_and_mapping.sha256',
    '/etc/selinux/selinux_denial_metadata',
    '/etc/selinux/vendor_file_contexts',
    '/etc/selinux/vendor_hwservice_contexts',
    '/etc/selinux/vendor_keystore2_key_contexts',
    '/etc/selinux/vendor_mac_permissions.xml',
    '/etc/selinux/vendor_property_contexts',
    '/etc/selinux/vendor_seapp_contexts',
    '/etc/selinux/vendor_sepolicy.cil',
    '/etc/selinux/vendor_service_contexts',
    '/etc/selinux/vendor_tee_service_contexts',
    '/etc/selinux/vndservice_contexts',
    '/etc/vintf/compatibility_matrix.xml',
    '/etc/vintf/manifest/android.hardware.drm-service.clearkey.xml',
    '/etc/vintf/manifest/android.hardware.sensors-multihal.xml',
    '/etc/vintf/manifest/android.hardware.wifi-service.xml',
    '/etc/vintf/manifest/android.hardware.wifi.hostapd.xml',
    '/etc/vintf/manifest/android.hardware.wifi.supplicant.xml',
    '/lib/mt6789/libmnl.so',
    '/lib64/mt6789/libmnl.so',
    '/lib/android.frameworks.sensorservice-V1-ndk.so',
    '/lib/android.hardware.audio.common-V3-ndk.so',
    '/lib/android.hardware.audio.common-V4-ndk.so',
    '/lib/android.hardware.audio.common-util.so',
    '/lib/android.hardware.audio.common@5.0.so',
    '/lib/android.hardware.audio.common@6.0-util.so',
    '/lib/android.hardware.audio.common@6.0.so',
    '/lib/android.hardware.audio.common@7.0.so',
    '/lib/android.hardware.audio.core-V3-ndk.so',
    '/lib/android.hardware.audio.core.sounddose-V3-ndk.so',
    '/lib/android.hardware.audio.effect-V2-ndk.so',
    '/lib/android.hardware.audio.effect-V3-ndk.so',
    '/lib/android.hardware.audio.effect@6.0.so',
    '/lib/android.hardware.audio.effect@7.0.so',
    '/lib/android.hardware.audio@6.0.so',
    '/lib/android.hardware.audio@7.0.so',
    '/lib/android.hardware.bluetooth.audio-V4-ndk.so',
    '/lib/android.hardware.bluetooth.audio-V5-ndk.so',
    '/lib/android.hardware.bluetooth.audio@2.0.so',
    '/lib/android.hardware.bluetooth.audio@2.1.so',
    '/lib/android.hardware.common-V2-ndk.so',
    '/lib/android.hardware.common.fmq-V1-ndk.so',
    '/lib/android.hardware.graphics.allocator-V2-ndk.so',
    '/lib/android.hardware.graphics.allocator@2.0.so',
    '/lib/android.hardware.graphics.allocator@3.0.so',
    '/lib/android.hardware.graphics.allocator@4.0.so',
    '/lib/android.hardware.graphics.bufferqueue@2.0.so',
    '/lib/android.hardware.graphics.common-V6-ndk.so',
    '/lib/android.hardware.graphics.common@1.0.so',
    '/lib/android.hardware.graphics.common@1.1.so',
    '/lib/android.hardware.graphics.common@1.2.so',
    '/lib/android.hardware.graphics.mapper@2.0.so',
    '/lib/android.hardware.graphics.mapper@2.1.so',
    '/lib/android.hardware.graphics.mapper@3.0.so',
    '/lib/android.hardware.graphics.mapper@4.0.so',
    '/lib/android.hardware.media.bufferpool2-V2-ndk.so',
    '/lib/android.hardware.media.bufferpool@2.0.so',
    '/lib/android.hardware.media.c2-V1-ndk.so',
    '/lib/android.hardware.nfc@1.0.so',
    '/lib/android.hardware.power@1.0.so',
    '/lib/android.hardware.radio@1.0.so',
    '/lib/android.hardware.radio@1.1.so',
    '/lib/android.hardware.renderscript@1.0.so',
    '/lib/android.hardware.sensors-V2-ndk.so',
    '/lib/android.hardware.sensors-V3-ndk.so',
    '/lib/android.hardware.sensors@1.0.so',
    '/lib/android.hardware.sensors@2.0-ScopedWakelock.so',
    '/lib/android.hardware.sensors@2.0.so',
    '/lib/android.hardware.sensors@2.1.so',
    '/lib/android.hardware.soundtrigger3-V3-ndk.so',
    '/lib/android.hidl.allocator@1.0.so',
    '/lib/android.hidl.memory.token@1.0.so',
    '/lib/android.hidl.memory@1.0.so',
    '/lib/android.hidl.safe_union@1.0.so',
    '/lib/android.media.audio.common.types-V3-ndk.so',
    '/lib/android.media.audio.common.types-V4-ndk.so',
    '/lib/android.media.audio.eraser.types-V1-ndk.so',
    '/lib/android.media.soundtrigger.types-V3-ndk.so',
    '/lib/android.system.suspend-V1-ndk.so',
    '/lib/android.system.wifi.keystore@1.0.so',
    '/lib/hw/android.hardware.bluetooth.audio@2.0-impl.so',
    '/lib/hw/android.hardware.bluetooth.audio@2.1-impl.so',
    '/lib/hw/android.hardware.renderscript@1.0-impl.so',
    '/lib/hw/audio.bluetooth.default.so',
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
    '/lib/libaedv.so',
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
    '/lib/libc++.so',
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
    '/lib/libprotobuf-cpp-lite-21.12.so',
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
    '/lib/libstagefright_bufferpool@2.0.1.so',
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
    '/lib/vendor.mediatek.hardware.bluetooth.audio-V1-ndk.so',
    '/lib/vendor.mediatek.hardware.bluetooth.audio@2.1.so',
    '/lib/vendor.mediatek.hardware.bluetooth.audio@2.2.so',
    '/lib/vendor.mediatek.hardware.mtkpower-V2-ndk.so',
    '/lib/vendor.mediatek.hardware.mtkpower@1.0.so',
    '/lib/vendor.mediatek.hardware.mtkpower@1.1.so',
    '/lib/vendor.mediatek.hardware.mtkpower@1.2.so',
    '/lib/vendor.mediatek.hardware.netdagent@1.0.so',
    '/lib64/android.frameworks.sensorservice-V1-ndk.so',
    '/lib64/android.frameworks.sensorservice@1.0.so',
    '/lib64/android.frameworks.stats-V1-ndk.so',
    '/lib64/android.frameworks.stats-V2-ndk.so',
    '/lib64/android.hardware.audio.common-V3-ndk.so',
    '/lib64/android.hardware.audio.common-V4-ndk.so',
    '/lib64/android.hardware.audio.common-util.so',
    '/lib64/android.hardware.audio.common@5.0.so',
    '/lib64/android.hardware.audio.common@6.0-util.so',
    '/lib64/android.hardware.audio.common@6.0.so',
    '/lib64/android.hardware.audio.common@7.0.so',
    '/lib64/android.hardware.audio.core-V3-ndk.so',
    '/lib64/android.hardware.audio.core.sounddose-V3-ndk.so',
    '/lib64/android.hardware.audio.effect-V2-ndk.so',
    '/lib64/android.hardware.audio.effect-V3-ndk.so',
    '/lib64/android.hardware.audio.effect@6.0.so',
    '/lib64/android.hardware.audio.effect@7.0.so',
    '/lib64/android.hardware.audio@6.0.so',
    '/lib64/android.hardware.audio@7.0.so',
    '/lib64/android.hardware.biometrics.common-V4-ndk.so',
    '/lib64/android.hardware.biometrics.common.thread.so',
    '/lib64/android.hardware.biometrics.common.util.so',
    '/lib64/android.hardware.biometrics.fingerprint-V4-ndk.so',
    '/lib64/android.hardware.bluetooth-V1-ndk.so',
    '/lib64/android.hardware.bluetooth.audio-V4-ndk.so',
    '/lib64/android.hardware.bluetooth.audio-V5-ndk.so',
    '/lib64/android.hardware.bluetooth.audio@2.0.so',
    '/lib64/android.hardware.bluetooth.audio@2.1.so',
    '/lib64/android.hardware.bluetooth.finder-V1-ndk.so',
    '/lib64/android.hardware.bluetooth.ranging-V1-ndk.so',
    '/lib64/android.hardware.boot-V1-ndk.so',
    '/lib64/android.hardware.boot@1.0.so',
    '/lib64/android.hardware.boot@1.1.so',
    '/lib64/android.hardware.camera.common-V1-ndk.so',
    '/lib64/android.hardware.camera.common-V2-ndk.so',
    '/lib64/android.hardware.camera.common@1.0.so',
    '/lib64/android.hardware.camera.device-V3-ndk.so',
    '/lib64/android.hardware.camera.device@1.0.so',
    '/lib64/android.hardware.camera.device@3.2.so',
    '/lib64/android.hardware.camera.device@3.3.so',
    '/lib64/android.hardware.camera.device@3.4.so',
    '/lib64/android.hardware.camera.device@3.5.so',
    '/lib64/android.hardware.camera.device@3.6.so',
    '/lib64/android.hardware.camera.metadata-V3-ndk.so',
    '/lib64/android.hardware.camera.provider-V3-ndk.so',
    '/lib64/android.hardware.camera.provider@2.4.so',
    '/lib64/android.hardware.camera.provider@2.5.so',
    '/lib64/android.hardware.camera.provider@2.6.so',
    '/lib64/android.hardware.common-V2-ndk.so',
    '/lib64/android.hardware.common.fmq-V1-ndk.so',
    '/lib64/android.hardware.contexthub-V4-ndk.so',
    '/lib64/android.hardware.drm-V1-ndk.so',
    '/lib64/android.hardware.drm.common-V1-ndk.so',
    '/lib64/android.hardware.dumpstate-V1-ndk.so',
    '/lib64/android.hardware.gatekeeper-V1-ndk.so',
    '/lib64/android.hardware.gnss-V5-ndk.so',
    '/lib64/android.hardware.graphics.allocator-V2-ndk.so',
    '/lib64/android.hardware.graphics.allocator@2.0.so',
    '/lib64/android.hardware.graphics.allocator@3.0.so',
    '/lib64/android.hardware.graphics.allocator@4.0.so',
    '/lib64/android.hardware.graphics.bufferqueue@1.0.so',
    '/lib64/android.hardware.graphics.bufferqueue@2.0.so',
    '/lib64/android.hardware.graphics.common-V5-ndk.so',
    '/lib64/android.hardware.graphics.common-V6-ndk.so',
    '/lib64/android.hardware.graphics.common@1.0.so',
    '/lib64/android.hardware.graphics.common@1.1.so',
    '/lib64/android.hardware.graphics.common@1.2.so',
    '/lib64/android.hardware.graphics.composer3-V2-ndk.so',
    '/lib64/android.hardware.graphics.composer3-V3-ndk.so',
    '/lib64/android.hardware.graphics.composer3-V4-ndk.so',
    '/lib64/android.hardware.graphics.mapper@2.0.so',
    '/lib64/android.hardware.graphics.mapper@2.1.so',
    '/lib64/android.hardware.graphics.mapper@3.0.so',
    '/lib64/android.hardware.graphics.mapper@4.0.so',
    '/lib64/android.hardware.health-V1-ndk.so',
    '/lib64/android.hardware.health-V4-ndk.so',
    '/lib64/android.hardware.ir-V1-ndk.so',
    '/lib64/android.hardware.keymaster-V4-ndk.so',
    '/lib64/android.hardware.keymaster@3.0.so',
    '/lib64/android.hardware.keymaster@4.0.so',
    '/lib64/android.hardware.light-V1-ndk.so',
    '/lib64/android.hardware.light-V2-ndk.so',
    '/lib64/android.hardware.media.bufferpool2-V2-ndk.so',
    '/lib64/android.hardware.media.bufferpool@2.0.so',
    '/lib64/android.hardware.media.c2-V1-ndk.so',
    '/lib64/android.hardware.media.c2@1.0.so',
    '/lib64/android.hardware.media.c2@1.1.so',
    '/lib64/android.hardware.media.c2@1.2.so',
    '/lib64/android.hardware.media.omx@1.0.so',
    '/lib64/android.hardware.media@1.0.so',
    '/lib64/android.hardware.memtrack-V1-ndk.so',
    '/lib64/android.hardware.nfc-V1-ndk.so',
    '/lib64/android.hardware.nfc-V2-ndk.so',
    '/lib64/android.hardware.nfc@1.0.so',
    '/lib64/android.hardware.power-V4-ndk.so',
    '/lib64/android.hardware.power-V6-ndk.so',
    '/lib64/android.hardware.power@1.0.so',
    '/lib64/android.hardware.power@1.1.so',
    '/lib64/android.hardware.power@1.2.so',
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
    '/lib64/android.hardware.radio@1.0.so',
    '/lib64/android.hardware.radio@1.1.so',
    '/lib64/android.hardware.renderscript@1.0.so',
    '/lib64/android.hardware.secure_element-V1-ndk.so',
    '/lib64/android.hardware.security.keymint-V1-ndk.so',
    '/lib64/android.hardware.security.keymint-V3-ndk.so',
    '/lib64/android.hardware.security.keymint-V4-ndk.so',
    '/lib64/android.hardware.security.rkp-V3-ndk.so',
    '/lib64/android.hardware.security.secureclock-V1-ndk.so',
    '/lib64/android.hardware.security.sharedsecret-V1-ndk.so',
    '/lib64/android.hardware.sensors-V2-ndk.so',
    '/lib64/android.hardware.sensors-V3-ndk.so',
    '/lib64/android.hardware.sensors@1.0.so',
    '/lib64/android.hardware.sensors@2.0-ScopedWakelock.so',
    '/lib64/android.hardware.sensors@2.0.so',
    '/lib64/android.hardware.sensors@2.1.so',
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
    '/lib64/android.hidl.allocator@1.0.so',
    '/lib64/android.hidl.memory.token@1.0.so',
    '/lib64/android.hidl.memory@1.0.so',
    '/lib64/android.hidl.safe_union@1.0.so',
    '/lib64/android.hidl.token@1.0-utils.so',
    '/lib64/android.hidl.token@1.0.so',
    '/lib64/android.media.audio.common.types-V2-ndk.so',
    '/lib64/android.media.audio.common.types-V3-ndk.so',
    '/lib64/android.media.audio.common.types-V4-ndk.so',
    '/lib64/android.media.audio.eraser.types-V1-ndk.so',
    '/lib64/android.media.soundtrigger.types-V1-ndk.so',
    '/lib64/android.media.soundtrigger.types-V3-ndk.so',
    '/lib64/android.system.keystore2-V1-ndk.so',
    '/lib64/android.system.suspend-V1-ndk.so',
    '/lib64/android.system.wifi.keystore@1.0.so',
    '/lib64/chre_atoms_log.so',
    '/lib64/chremetrics-cpp.so',
    '/lib64/hw/android.hardware.bluetooth.audio@2.0-impl.so',
    '/lib64/hw/android.hardware.bluetooth.audio@2.1-impl.so',
    '/lib64/hw/android.hardware.renderscript@1.0-impl.so',
    '/lib64/hw/audio.bluetooth.default.so',
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
    '/lib64/libaedv.so',
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
    '/lib64/libc++.so',
    '/lib64/libcap.so',
    '/lib64/libclang_rt.ubsan_standalone-aarch64-android.so',
    '/lib64/libcodec2.so',
    '/lib64/libcodec2_aidl.so',
    '/lib64/libcodec2_hal_common.so',
    '/lib64/libcodec2_hidl@1.0.so',
    '/lib64/libcodec2_hidl@1.1.so',
    '/lib64/libcodec2_hidl@1.2.so',
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
    '/lib64/libprotobuf-cpp-lite-21.12.so',
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
    '/lib64/libstagefright_bufferpool@2.0.1.so',
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
    '/lib64/nfc_nci_nxp_snxxx_v2.so',
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
    '/lib64/vendor.mediatek.hardware.bluetooth.audio-V1-ndk.so',
    '/lib64/vendor.mediatek.hardware.bluetooth.audio@2.1.so',
    '/lib64/vendor.mediatek.hardware.bluetooth.audio@2.2.so',
    '/lib64/vendor.mediatek.hardware.lbs@1.0.so',
    '/lib64/vendor.mediatek.hardware.mtkpower-V1-ndk.so',
    '/lib64/vendor.mediatek.hardware.mtkpower-V2-ndk.so',
    '/lib64/vendor.mediatek.hardware.mtkpower@1.0.so',
    '/lib64/vendor.mediatek.hardware.mtkpower@1.1.so',
    '/lib64/vendor.mediatek.hardware.mtkpower@1.2.so',
    '/lib64/vendor.mediatek.hardware.netdagent@1.0.so',
    '/lib64/vendor.nxp.nxpese@1.0.so',
    '/lib64/vendor.nxp.nxpnfc_aidl-V1-ndk.so',
    '/odm/etc/build.prop',
    '/odm/etc/group',
    '/odm/etc/passwd',
    '/odm/etc/selinux/odm_file_contexts',
    '/odm/etc/selinux/odm_hwservice_contexts',
    '/odm/etc/selinux/odm_mac_permissions.xml',
    '/odm/etc/selinux/odm_property_contexts',
    '/odm/etc/selinux/odm_seapp_contexts',
    '/odm/etc/selinux/odm_sepolicy.cil',
    '/odm/etc/selinux/odm_service_contexts',
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
    f.write('# paths), except five that device/xiaomi/emerald/vendor_symlinks/Android.bp writes by hand: three\n')
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
