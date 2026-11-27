#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#
# clean-2: LineageOS 24.0 system on the unmodified stock HyperOS 3 Global OS3.0.305.0.WNFMIXM
# vendor, vendor_dlkm, odm_dlkm and system_dlkm images. Values marked "stock" were read from
# the 305 images (boot/vendor_boot headers, super metadata, vendor props).
#

DEVICE_PATH := device/xiaomi/emerald
KERNEL_PATH := device/xiaomi/emerald-kernel
IMAGES_PATH := vendor/xiaomi/emerald-images

# Architecture (mt6789: 2x Cortex-A76 + 6x Cortex-A55; as LineageOS daylight/jagar, xelex/Q25)
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-2a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_ABI2 :=
TARGET_CPU_VARIANT := generic
TARGET_CPU_VARIANT_RUNTIME := cortex-a76

TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv8-2a
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_ABI2 := armeabi
TARGET_2ND_CPU_VARIANT := generic
TARGET_2ND_CPU_VARIANT_RUNTIME := cortex-a55

# A/B
AB_OTA_UPDATER := true

AB_OTA_PARTITIONS += \
    boot \
    dtbo \
    odm_dlkm \
    product \
    system \
    system_dlkm \
    system_ext \
    vbmeta \
    vbmeta_system \
    vbmeta_vendor \
    vendor \
    vendor_boot \
    vendor_dlkm

# Bootloader
TARGET_BOOTLOADER_BOARD_NAME := emerald
TARGET_NO_BOOTLOADER := true

# Boot image (stock: boot header v4, kernel at 0x40000000, ramdisk at 0x66f00000,
# tags/dtb at 0x47c80000, page size 4096)
BOARD_BOOT_HEADER_VERSION := 4
BOARD_KERNEL_BASE := 0x3fff8000
BOARD_KERNEL_OFFSET := 0x00008000
BOARD_KERNEL_PAGESIZE := 4096
BOARD_RAMDISK_OFFSET := 0x26f08000
BOARD_KERNEL_TAGS_OFFSET := 0x07c88000
BOARD_DTB_OFFSET := 0x07c88000

BOARD_MKBOOTIMG_ARGS := --ramdisk_offset $(BOARD_RAMDISK_OFFSET)
BOARD_MKBOOTIMG_ARGS += --tags_offset $(BOARD_KERNEL_TAGS_OFFSET)
BOARD_MKBOOTIMG_ARGS += --dtb_offset $(BOARD_DTB_OFFSET)
BOARD_MKBOOTIMG_ARGS += --header_version $(BOARD_BOOT_HEADER_VERSION)

# Stock vendor_boot command line and bootconfig
BOARD_KERNEL_CMDLINE := bootopt=64S3,32N2,64N2
BOARD_BOOTCONFIG := \
    kernel.rcu_nocbs=all \
    kernel.rcutree.enable_rcu_lazy=1 \
    kernel.rcupdate.rcu_cpu_stall_cputime=1

BOARD_MOVE_GSI_AVB_KEYS_TO_VENDOR_BOOT := true
BOARD_RAMDISK_USE_LZ4 := true

# Display (stock ro.sf.lcd_density)
TARGET_SCREEN_DENSITY := 480

# HWUI on Vulkan, as on the stock 305 vendor (ro.hwui.use_vulkan=true). The build writes this prop
# into the vendor build.prop only (ADDITIONAL_VENDOR_PROPERTIES, sysprop_config.mk); without the flag
# it is empty, and a vendor image we build ourselves would turn HWUI back to SkiaGL — the stock
# partition we ship today keeps Vulkan through its own build.prop (device.mk, RenderEngine note).
TARGET_USES_VULKAN := true

# Health: LineageOS charging control switches the charger input off and on (no bypass). The
# service ships prebuilt in vendor.img (prebuilts/lineage-health); these are its build flags.
$(call soong_config_set,lineage_health,charging_control_charging_path,/sys/class/power_supply/battery/input_suspend)
$(call soong_config_set,lineage_health,charging_control_charging_enabled,0)
$(call soong_config_set,lineage_health,charging_control_charging_disabled,1)
$(call soong_config_set_bool,lineage_health,charging_control_supports_bypass,false)

# Init: product identity (brand / model / marketname / fingerprint) by hardware SKU, as the stock
# vendor picks build_${ro.boot.product.hardware.sku}.prop for its own partition (libinit/)
$(call soong_config_set,libinit,vendor_init_lib,//$(DEVICE_PATH):init_emerald)

# Kernel: stock GKI, see device/xiaomi/emerald-kernel/README.md
BOARD_USES_GENERIC_KERNEL_IMAGE := true
BOARD_KERNEL_IMAGE_NAME := Image.lz4
TARGET_PREBUILT_KERNEL := $(KERNEL_PATH)/Image.lz4
TARGET_PREBUILT_KERNEL_HEADERS := $(KERNEL_PATH)/kernel-uapi-headers.tar.gz

BOARD_INCLUDE_DTB_IN_BOOTIMG := true
BOARD_PREBUILT_DTBIMAGE_DIR := $(KERNEL_PATH)/dtb
BOARD_KERNEL_SEPARATED_DTBO := true
BOARD_PREBUILT_DTBOIMAGE := $(KERNEL_PATH)/dtbo.img

# Kernel modules: only the vendor ramdisk set is packed by the build; vendor_dlkm and
# system_dlkm ship as stock images (below).
EMERALD_RAMDISK_MODULES_DIR := $(KERNEL_PATH)/vendor_ramdisk
BOARD_VENDOR_RAMDISK_KERNEL_MODULES_LOAD := $(strip $(shell cat $(EMERALD_RAMDISK_MODULES_DIR)/modules.load))
BOARD_VENDOR_RAMDISK_RECOVERY_KERNEL_MODULES_LOAD := $(strip $(shell cat $(EMERALD_RAMDISK_MODULES_DIR)/modules.load.recovery))
BOARD_VENDOR_RAMDISK_KERNEL_MODULES := $(wildcard $(EMERALD_RAMDISK_MODULES_DIR)/*.ko)

# Partitions (stock sizes)
BOARD_FLASH_BLOCK_SIZE := 262144 # (BOARD_KERNEL_PAGESIZE * 64)
BOARD_BOOTIMAGE_PARTITION_SIZE := 67108864
BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 67108864
BOARD_DTBOIMG_PARTITION_SIZE := 8388608

# Stock super: 7516192768 bytes, groups main_a/main_b of 7505707008 bytes each
BOARD_SUPER_PARTITION_SIZE := 7516192768
BOARD_SUPER_PARTITION_GROUPS := main
BOARD_MAIN_SIZE := 7505707008
BOARD_MAIN_PARTITION_LIST := \
    odm_dlkm \
    product \
    system \
    system_dlkm \
    system_ext \
    vendor \
    vendor_dlkm

BOARD_PRODUCTIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_SYSTEM_EXTIMAGE_FILE_SYSTEM_TYPE := erofs
# Uncompressed (the default is lz4hc): reading them costs no decompression on this CPU. The
# images in super grow from ~4.2 to ~5.0 GB; the main dynamic partition group has 7.5 GB.
BOARD_PRODUCTIMAGE_EROFS_COMPRESSOR := none
BOARD_SYSTEMIMAGE_EROFS_COMPRESSOR := none
BOARD_SYSTEM_EXTIMAGE_EROFS_COMPRESSOR := none

TARGET_COPY_OUT_ODM_DLKM := odm_dlkm
TARGET_COPY_OUT_PRODUCT := product
TARGET_COPY_OUT_SYSTEM_DLKM := system_dlkm
TARGET_COPY_OUT_SYSTEM_EXT := system_ext
TARGET_COPY_OUT_VENDOR := vendor
TARGET_COPY_OUT_VENDOR_DLKM := vendor_dlkm

BOARD_USES_METADATA_PARTITION := true

-include vendor/lineage/config/BoardConfigReservedSize.mk

# Stock vendor-side images (copied by extract-images.sh), used as they are except
# vendor_dlkm.img, which gets the fixes in patch-images.py. The vendor partition itself is built from
# vendor/xiaomi/emerald (stock 305 blobs + our files), see "vendor image" below.
BOARD_PREBUILT_VENDOR_DLKMIMAGE := $(IMAGES_PATH)/vendor_dlkm.patched.img
BOARD_PREBUILT_ODM_DLKMIMAGE := $(IMAGES_PATH)/odm_dlkm.img
BOARD_PREBUILT_SYSTEM_DLKMIMAGE := $(IMAGES_PATH)/system_dlkm.img

# Vendor image: built from the blobs (vendor/xiaomi/emerald) as erofs, the same size and format as the
# stock one (777347072 bytes, EROFS+LZ4), so it fits the super partition the phone already has.
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_VENDORIMAGE_PARTITION_SIZE := 777347072

# Owner/group/mode of the vendor partition as the stock image has them (gid shell, 0751 directories),
# read from the image itself - see the file.
TARGET_FS_CONFIG_GEN := $(DEVICE_PATH)/configs/fs_config/emerald_fs_config

# Recovery (in vendor_boot; stock fstab and pixel format)
BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT := true
BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true
TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/rootdir/etc/fstab.mt6789
TARGET_RECOVERY_PIXEL_FORMAT := BGRA_8888
TARGET_USERIMAGES_USE_F2FS := true

# SELinux: LineageOS' MediaTek policy, included whole as daylight/jagar and xelex/Q25 do.
# Since 25.11 the vendor policy of the image is built by the platform, not taken from the stock image
# (option "the platform owns what it installs", the same rule as FROM_SOURCE in vendor-blobs/list.py:
# the selinux files are install rules of system/sepolicy, two rules for one path do not pass kati).
# So the MediaTek vendor .te is compiled in after all - the empty list that kept the stock policy was
# the reason it was not. This is the part that needs a boot test: type names come from the MediaTek
# source policy while the binaries are stock 305 (Android 16), a mismatch shows up as init denials.
include device/mediatek/sepolicy_vndr/SEPolicy.mk

# Our own vendor policy dir: file_contexts for stock blobs whose type exists in the MediaTek policy
# but whose path pattern is missing there (59 paths, found by vendor-diff 28.11). Needs the vendor
# policy (hal_*_default_exec), hence BOARD_VENDOR_SEPOLICY_DIRS and not the system_ext private dir.
BOARD_VENDOR_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/vendor

# Compat map of the system_ext public types for the stock vendor's 202504 policy (see the file)
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/private

# Security patch level (stock vendor)
VENDOR_SECURITY_PATCH := 2026-06-05

# Verified Boot (as LineageOS daylight/jagar; verification off, the bootloader is unlocked)
BOARD_AVB_ENABLE := true
BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 3

BOARD_AVB_BOOT_KEY_PATH := external/avb/test/data/testkey_rsa2048.pem
BOARD_AVB_BOOT_ALGORITHM := SHA256_RSA2048
BOARD_AVB_BOOT_ROLLBACK_INDEX := 1
BOARD_AVB_BOOT_ROLLBACK_INDEX_LOCATION := 1

BOARD_AVB_VBMETA_SYSTEM := product system system_ext
BOARD_AVB_VBMETA_SYSTEM_KEY_PATH := external/avb/test/data/testkey_rsa2048.pem
BOARD_AVB_VBMETA_SYSTEM_ALGORITHM := SHA256_RSA2048
BOARD_AVB_VBMETA_SYSTEM_ROLLBACK_INDEX := 1
BOARD_AVB_VBMETA_SYSTEM_ROLLBACK_INDEX_LOCATION := 2

BOARD_AVB_VBMETA_VENDOR := vendor
BOARD_AVB_VBMETA_VENDOR_KEY_PATH := external/avb/test/data/testkey_rsa2048.pem
BOARD_AVB_VBMETA_VENDOR_ALGORITHM := SHA256_RSA2048
BOARD_AVB_VBMETA_VENDOR_ROLLBACK_INDEX := 1
BOARD_AVB_VBMETA_VENDOR_ROLLBACK_INDEX_LOCATION := 3

# VINTF: the device manifest, its fragments and the compatibility matrix are the stock 305 ones inside the
# vendor partition (blobs in vendor/xiaomi/emerald). They are installed as plain files, not as VINTF
# declarations of this build: they describe a vendor we do not compile, so the build must not validate or
# merge them, and their file names (manifest.xml, android.hardware.audio.service-aidl.xml, ...) already
# belong to modules of the source tree. This is the switch the build offers for exactly that case.
# Same for the ELF files: the vendor binaries and libraries are prebuilts from the stock image, installed
# as files, they do not participate in the build (no shared_libs of their own, no stripping).
BUILD_BROKEN_VINTF_PRODUCT_COPY_FILES := true
BUILD_BROKEN_ELF_PREBUILT_PRODUCT_COPY_FILES := true

# Framework matrices: stock system and product fragments (Xiaomi/MediaTek vendor HALs).
DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE := \
    $(DEVICE_PATH)/vintf/framework_compatibility_matrix_system.xml \
    $(DEVICE_PATH)/vintf/framework_compatibility_matrix_product.xml

# Inherit the proprietary files
include vendor/xiaomi/emerald/BoardConfigVendor.mk
