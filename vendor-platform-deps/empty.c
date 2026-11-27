/*
 * Пустой якорь: нужен только чтобы через `required` потянуть в раздел vendor платформенные
 * библиотеки, которые блобы раздела ждут в DT_NEEDED (см. ../vendor-platform-deps/Android.bp).
 */
void emerald_vendor_platform_deps_anchor(void) {
}
