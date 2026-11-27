# Модули платформы, которые стоковый vendor.img 305 содержал, а наш PRODUCT_PACKAGES не просил.
#
# Как список появился (27.11, после первого собранного образа раздела): образ собрался и даже влез,
# но аудит зависимостей — DT_NEEDED по всем 3010 ELF образа против того, что есть в образе и в
# system/ — показал 98 библиотек, которые не разрешаются нигде, и 28 бинарников, которые не
# загрузились бы вообще: composer@3.2/3.3/3.4 и allocator-V2 (без них SurfaceFlinger не получает
# графический HAL, то есть экрана нет), audio.service-aidl.mediatek, camerahalserver, sensors,
# bluetooth-service-mediatek, hostapd, nfc-service-tms, usb, mtkpower, vibrator.
#
# Причина: `vendor-blobs/list.py` исключает эти пути из блобов (`FROM_SOURCE`) на том основании, что
# «их ставит платформа». Платформа ставит их только когда модуль попросили в PRODUCT_PACKAGES, а
# просили только HAL-бинарники — сами бинарники у нас блобы, зависимостей они не объявляют.
# Итог: ни блоба, ни сборки. Отсюда этот файл.
#
# Правило на будущее: сюда попадает библиотека только при доказанной нужде — её soname есть в
# DT_NEEDED файлов раздела (аудит в emerald-build: scripts/vendor-needed.py), а не «на всякий случай».
# Список сверен с soong (out/soong/Android-lineage_emerald.mk) 27.11: все 98 имён — существующие
# модули, 22 МиБ в сыром виде на обе битности.

# --- звук
PRODUCT_PACKAGES += \
    android.hardware.audio.common@5.0 \
    android.hardware.audio.core-V3-ndk \
    android.hardware.audio.core.sounddose-V3-ndk \
    android.hardware.audio.effect-V2-ndk \
    android.hardware.audio.effect-V3-ndk \
    android.hardware.bluetooth.audio-V4-ndk \
    android.hardware.bluetooth.audio-V5-ndk \
    android.hardware.bluetooth.audio@2.0 \
    android.hardware.bluetooth.audio@2.1 \
    android.hardware.soundtrigger3-V3-ndk \
    android.media.audio.common.types-V4-ndk \
    libalsautils \
    libalsautilsv2 \
    libmediautils_vendor \
    libnbaio_mono \
    libtinyalsav2 \
    libtinycompress \
    vendor.mediatek.hardware.audio-V1-ndk \
    vendor.mediatek.hardware.bluetooth.audio-V1-ndk \
    vendor.mediatek.hardware.bluetooth.audio@2.1 \
    vendor.mediatek.hardware.bluetooth.audio@2.2

# --- графика (composer/allocator: без них системы нет)
PRODUCT_PACKAGES += \
    android.hardware.graphics.common-V5-ndk \
    android.hardware.graphics.common-V6-ndk \
    android.hardware.graphics.composer3-V2-ndk \
    android.hardware.graphics.composer3-V3-ndk \
    android.hardware.graphics.composer3-V4-ndk \
    libdrm \
    libgrallocusage

# --- камера и медиа
PRODUCT_PACKAGES += \
    android.hardware.camera.common-V2-ndk \
    android.hardware.camera.device-V3-ndk \
    android.hardware.camera.provider-V3-ndk \
    android.hardware.camera.provider@2.4 \
    android.hardware.camera.provider@2.5 \
    android.hardware.camera.provider@2.6 \
    android.hardware.media.c2-V1-ndk \
    libcodec2_aidl \
    libcodec2_hidl@1.0 \
    libcodec2_hidl@1.1 \
    libcodec2_hidl@1.2 \
    libcodec2_soft_common

# --- связь: радио, wifi, bt, nfc
PRODUCT_PACKAGES += \
    android.hardware.bluetooth-V1-ndk \
    android.hardware.bluetooth.finder-V1-ndk \
    android.hardware.bluetooth.ranging-V1-ndk \
    android.hardware.nfc-V1-ndk \
    android.hardware.nfc@1.0 \
    android.hardware.radio-V4-ndk \
    android.hardware.radio.config-V4-ndk \
    android.hardware.radio.data-V4-ndk \
    android.hardware.radio.ims-V3-ndk \
    android.hardware.radio.messaging-V4-ndk \
    android.hardware.radio.modem-V4-ndk \
    android.hardware.radio.network-V4-ndk \
    android.hardware.radio.sap-V1-ndk \
    android.hardware.radio.sim-V4-ndk \
    android.hardware.radio.voice-V4-ndk \
    android.hardware.secure_element-V1-ndk \
    android.hardware.tetheroffload-V1-ndk \
    android.hardware.wifi.common-V2-ndk \
    android.hardware.wifi.hostapd-V3-ndk \
    libkeystore-wifi-hidl \
    vendor.mediatek.hardware.lbs@1.0 \
    vendor.mediatek.hardware.netdagent@1.0

# --- датчики, питание, USB, прочая мелочь
PRODUCT_PACKAGES += \
    android.hardware.gnss-V5-ndk \
    android.hardware.health-V1-ndk \
    android.hardware.ir-V1-ndk \
    android.hardware.light-V1-ndk \
    android.hardware.light-V2-ndk \
    android.hardware.power-V4-ndk \
    android.hardware.power-V6-ndk \
    android.hardware.sensors-V2-ndk \
    android.hardware.sensors@2.0-ScopedWakelock \
    android.hardware.usb-V3-ndk \
    android.hardware.usb.gadget-V1-ndk \
    android.hardware.vibrator-V1-ndk \
    android.hardware.biometrics.common-V4-ndk \
    android.hardware.biometrics.common.thread \
    android.hardware.biometrics.common.util \
    android.hardware.biometrics.fingerprint-V4-ndk \
    android.frameworks.stats-V1-ndk \
    libsensorndkbridge

# --- сервисы и демоны раздела: сток их содержал, у нас не было ни бинарника, ни init-скрипта.
# Без vndservicemanager не поднимается ни один vendor-HAL (это менеджер сервисов раздела), без
# wpa_supplicant/hostapd нет wifi, без thermal-mediatek нет термоконтроля. Найдено 27.11 вторым
# аудитом — по init-скриптам образа: сервис есть, бинарника нет.
PRODUCT_PACKAGES += \
    android.hardware.drm-service.clearkey \
    android.hardware.ir-service.example \
    android.hardware.memtrack-service.mediatek \
    android.hardware.nfc2-service.nxp \
    android.hardware.sensors-service.multihal \
    android.hardware.thermal-service.mediatek \
    android.hardware.wifi-service-lazy \
    vndservicemanager \
    wlan_assistant \
    wpa_supplicant

# --- power/perf MTK: их ждут libmtkperf_client_vendor, lib_power_applist и power HAL
PRODUCT_PACKAGES += \
    vendor.mediatek.hardware.mtkpower-V1-ndk \
    vendor.mediatek.hardware.mtkpower-V2-ndk \
    vendor.mediatek.hardware.mtkpower@1.0 \
    vendor.mediatek.hardware.mtkpower@1.1 \
    vendor.mediatek.hardware.mtkpower@1.2

# --- keymint / trusty / базовые для MTK-раздела
PRODUCT_PACKAGES += \
    android.hardware.security.keymint-V3-ndk \
    android.hardware.security.keymint-V4-ndk \
    lib_android_keymaster_keymint_utils \
    libkeymint \
    libkeymint_remote_prov_support \
    libtrusty \
    libcppbor_external

# --- базовое: без libhidltransport/libhwbinder/libmnl не грузятся 70/25/18 файлов
PRODUCT_PACKAGES += \
    libaedv \
    libflatbuffers-cpp \
    libhidltransport \
    libhwbinder \
    libladder \
    libmnl
