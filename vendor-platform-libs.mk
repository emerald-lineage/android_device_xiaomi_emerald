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
# `shared_libs` модулей-держателей emerald_vendor_deps_* (vendor/xiaomi/emerald-platform-deps), а
# здесь — только сервисы и сами держатели. `required` для этого не годится (28.11): он ставит
# system-вариант, и 89 библиотек уехали в /system/lib64.
#
# Правило на будущее: сюда попадает модуль только при доказанной нужде — его soname есть в DT_NEEDED
# файлов раздела (аудит: scripts/vendor-needed.py в emerald-build), а не «на всякий случай».

# Сервисы и демоны раздела: сток их содержал, у нас не было ни бинарника, ни init-скрипта.
# Без vndservicemanager не поднимается ни один vendor-HAL (это менеджер сервисов раздела), без
# wpa_supplicant/hostapd нет wifi. Найдено 27.11 вторым аудитом — по init-скриптам образа: сервис
# есть, бинарника нет.
# thermal-HAL здесь больше нет (28.11): платформенный android.hardware.thermal-service.mediatek ставил
# свой VINTF-фрагмент рядом со стоковым thermal-mediatek.xml — оба IThermal/default @3, libvintf
# отверг манифест устройства целиком (NULL VINTF MANIFEST, все vendor-HAL — SIGABRT). Бинарник,
# rc и фрагмент теперь стоковые, из блобов (vendor-blobs/list.py, путь ушёл из FROM_SOURCE).
PRODUCT_PACKAGES += \
    android.hardware.drm-service.clearkey \
    android.hardware.ir-service.example \
    android.hardware.memtrack-service.mediatek \
    android.hardware.nfc2-service.nxp \
    android.hardware.sensors-service.multihal \
    android.hardware.wifi-service-lazy \
    vndservicemanager \
    wlan_assistant \
    wpa_supplicant

# Тянут в /vendor 179 библиотек из DT_NEEDED файлов раздела (по одной в shared_libs на модуль,
# разрядности — ровно нужные образу; транзитивные зависимости soong ставит сам). Модулей 179, а не один:
# soong запрещает графу зависеть от двух версий одного aidl_interface, проверка транзитивная —
# 17:14 упало на audio.effect V2+V3, 17:20 на graphics.common V6+V7, где V7 пришёл транзитивно.
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
    emerald_vendor_deps_5 \
    emerald_vendor_deps_6 \
    emerald_vendor_deps_7 \
    emerald_vendor_deps_8 \
    emerald_vendor_deps_9 \
    emerald_vendor_deps_10 \
    emerald_vendor_deps_11 \
    emerald_vendor_deps_12 \
    emerald_vendor_deps_13 \
    emerald_vendor_deps_14 \
    emerald_vendor_deps_15 \
    emerald_vendor_deps_16 \
    emerald_vendor_deps_17 \
    emerald_vendor_deps_18 \
    emerald_vendor_deps_19 \
    emerald_vendor_deps_20 \
    emerald_vendor_deps_21 \
    emerald_vendor_deps_22 \
    emerald_vendor_deps_23 \
    emerald_vendor_deps_24 \
    emerald_vendor_deps_25 \
    emerald_vendor_deps_26 \
    emerald_vendor_deps_27 \
    emerald_vendor_deps_28 \
    emerald_vendor_deps_29 \
    emerald_vendor_deps_30 \
    emerald_vendor_deps_31 \
    emerald_vendor_deps_32 \
    emerald_vendor_deps_33 \
    emerald_vendor_deps_34 \
    emerald_vendor_deps_35 \
    emerald_vendor_deps_36 \
    emerald_vendor_deps_37 \
    emerald_vendor_deps_38 \
    emerald_vendor_deps_39 \
    emerald_vendor_deps_40 \
    emerald_vendor_deps_41 \
    emerald_vendor_deps_42 \
    emerald_vendor_deps_43 \
    emerald_vendor_deps_44 \
    emerald_vendor_deps_45 \
    emerald_vendor_deps_46 \
    emerald_vendor_deps_47 \
    emerald_vendor_deps_48 \
    emerald_vendor_deps_49 \
    emerald_vendor_deps_50 \
    emerald_vendor_deps_51 \
    emerald_vendor_deps_52 \
    emerald_vendor_deps_53 \
    emerald_vendor_deps_54 \
    emerald_vendor_deps_55 \
    emerald_vendor_deps_56 \
    emerald_vendor_deps_57 \
    emerald_vendor_deps_58 \
    emerald_vendor_deps_59 \
    emerald_vendor_deps_60 \
    emerald_vendor_deps_61 \
    emerald_vendor_deps_62 \
    emerald_vendor_deps_63 \
    emerald_vendor_deps_64 \
    emerald_vendor_deps_65 \
    emerald_vendor_deps_66 \
    emerald_vendor_deps_67 \
    emerald_vendor_deps_68 \
    emerald_vendor_deps_69 \
    emerald_vendor_deps_70 \
    emerald_vendor_deps_71 \
    emerald_vendor_deps_72 \
    emerald_vendor_deps_73 \
    emerald_vendor_deps_74 \
    emerald_vendor_deps_75 \
    emerald_vendor_deps_76 \
    emerald_vendor_deps_77 \
    emerald_vendor_deps_78 \
    emerald_vendor_deps_79 \
    emerald_vendor_deps_80 \
    emerald_vendor_deps_81 \
    emerald_vendor_deps_82 \
    emerald_vendor_deps_83 \
    emerald_vendor_deps_84 \
    emerald_vendor_deps_85 \
    emerald_vendor_deps_86 \
    emerald_vendor_deps_87 \
    emerald_vendor_deps_88 \
    emerald_vendor_deps_89 \
    emerald_vendor_deps_90 \
    emerald_vendor_deps_91 \
    emerald_vendor_deps_92 \
    emerald_vendor_deps_93 \
    emerald_vendor_deps_94 \
    emerald_vendor_deps_95 \
    emerald_vendor_deps_96 \
    emerald_vendor_deps_97 \
    emerald_vendor_deps_98 \
    emerald_vendor_deps_99 \
    emerald_vendor_deps_100 \
    emerald_vendor_deps_101 \
    emerald_vendor_deps_102 \
    emerald_vendor_deps_103 \
    emerald_vendor_deps_104 \
    emerald_vendor_deps_105 \
    emerald_vendor_deps_106 \
    emerald_vendor_deps_107 \
    emerald_vendor_deps_108 \
    emerald_vendor_deps_109 \
    emerald_vendor_deps_110 \
    emerald_vendor_deps_111 \
    emerald_vendor_deps_112 \
    emerald_vendor_deps_113 \
    emerald_vendor_deps_114 \
    emerald_vendor_deps_115 \
    emerald_vendor_deps_116 \
    emerald_vendor_deps_117 \
    emerald_vendor_deps_118 \
    emerald_vendor_deps_119 \
    emerald_vendor_deps_120 \
    emerald_vendor_deps_121 \
    emerald_vendor_deps_122 \
    emerald_vendor_deps_123 \
    emerald_vendor_deps_124 \
    emerald_vendor_deps_125 \
    emerald_vendor_deps_126 \
    emerald_vendor_deps_127 \
    emerald_vendor_deps_128 \
    emerald_vendor_deps_129 \
    emerald_vendor_deps_130 \
    emerald_vendor_deps_131 \
    emerald_vendor_deps_132 \
    emerald_vendor_deps_133 \
    emerald_vendor_deps_134 \
    emerald_vendor_deps_135 \
    emerald_vendor_deps_136 \
    emerald_vendor_deps_137 \
    emerald_vendor_deps_138 \
    emerald_vendor_deps_139 \
    emerald_vendor_deps_140 \
    emerald_vendor_deps_141 \
    emerald_vendor_deps_142 \
    emerald_vendor_deps_143 \
    emerald_vendor_deps_144 \
    emerald_vendor_deps_145 \
    emerald_vendor_deps_146 \
    emerald_vendor_deps_147 \
    emerald_vendor_deps_148 \
    emerald_vendor_deps_149 \
    emerald_vendor_deps_150 \
    emerald_vendor_deps_151 \
    emerald_vendor_deps_152 \
    emerald_vendor_deps_153 \
    emerald_vendor_deps_154 \
    emerald_vendor_deps_155 \
    emerald_vendor_deps_156 \
    emerald_vendor_deps_157 \
    emerald_vendor_deps_158 \
    emerald_vendor_deps_159 \
    emerald_vendor_deps_160 \
    emerald_vendor_deps_161 \
    emerald_vendor_deps_162 \
    emerald_vendor_deps_163 \
    emerald_vendor_deps_164 \
    emerald_vendor_deps_165 \
    emerald_vendor_deps_166 \
    emerald_vendor_deps_167 \
    emerald_vendor_deps_168 \
    emerald_vendor_deps_169 \
    emerald_vendor_deps_170 \
    emerald_vendor_deps_171 \
    emerald_vendor_deps_172 \
    emerald_vendor_deps_173 \
    emerald_vendor_deps_174 \
    emerald_vendor_deps_175 \
    emerald_vendor_deps_176 \
    emerald_vendor_deps_177 \
    emerald_vendor_deps_178 \
    emerald_vendor_deps_179

# Камера (B20): android.hardware.camera.common заморожен на V2 в форке hardware/interfaces
# (emerald-lineage, ветка main) — только после заморозки платформа собирает vendor-вариант V2,
# которого требует блоб libmtkcam_hal_aidl_common.so (DT_NEEDED camera.common-V2-ndk.so).
# Заморозки мало: в /vendor библиотеку кладёт `shared_libs` vendor-модуля-держателя (emerald_vendor_deps_*).
# Стоковая V2-библиотека побайтово равна V1, поэтому V2 заморожен без изменений API. Блоб на этот
# путь класть нельзя — платформа держит правило на тот же файл.
