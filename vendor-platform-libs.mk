# Модули платформы, которые стоковый vendor.img 305 содержал в разделе, а наше дерево не ставило.
#
# Как список появился (27.11, после первого собранного образа): образ собрался и влез, но аудит
# зависимостей — DT_NEEDED по всем ELF образа против того, что есть в образе и в system/ — показал
# 98 библиотек, которые не разрешаются нигде, и 28 бинарников, которые не загрузились бы: composer@3.2/
# 3.3/3.4 и allocator-V2 (без них SurfaceFlinger не получает графический HAL, то есть экрана нет),
# audio.service-aidl.mediatek, camerahalserver, sensors, bluetooth-service-mediatek, hostapd,
# nfc-service-tms, usb, mtkpower, vibrator.
#
# Причина: `vendor-blobs/list.py` исключает эти пути из блобов (`FROM_SOURCE`) на том основании, что
# «их ставит платформа». Платформа ставит их только как зависимость (required) vendor-модуля —
# PRODUCT_PACKAGES для `vendor_available: true` даёт лишь system-вариант (проверено 27.11: после
# прогона с 98 модулями в PRODUCT_PACKAGES в ninja не было ни одного vendor-пути, интермедиатов
# vendor-варианта тоже; из 98 поставились 9 — те, что `vendor: true`). Поэтому библиотеки идут через
# `required` модуля emerald_vendor_platform_deps (vendor-platform-deps/Android.bp), а здесь — только
# сервисы и сам этот модуль.
#
# Правило на будущее: сюда попадает модуль только при доказанной нужде — его soname есть в DT_NEEDED
# файлов раздела (аудит: scripts/vendor-needed.py в emerald-build), а не «на всякий случай».

# Сервисы и демоны раздела: сток их содержал, у нас не было ни бинарника, ни init-скрипта.
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

# Тянет в /vendor 98 библиотек из DT_NEEDED блобов (списки — в required пяти модулей; 9 из них
# платформа ставит и сама как vendor: true, остальные 91 — только так). Модулей пять, а не один:
# soong запрещает одному графу зависеть от двух версий одного aidl_interface (27.11 17:14).
# Сами модули живут в vendor/xiaomi/emerald-platform-deps/ — не в этом дереве: зависимости
# (libhidltransport, libhwbinder, libmnl) объявляют visibility //vendor:__subpackages__, а у нас
# здесь soong_namespace, и soong падал на анализе. Каталог вне git-проектов: переживает repo sync,
# копии файлов — scripts/templates/vendor-platform-deps в emerald-build; если его удалить, сборка
# упадёт на «module emerald_vendor_deps_1 not found».
PRODUCT_PACKAGES += \
    emerald_vendor_deps_1 \
    emerald_vendor_deps_2 \
    emerald_vendor_deps_3 \
    emerald_vendor_deps_4 \
    emerald_vendor_deps_5
