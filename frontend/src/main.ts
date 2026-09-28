import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import '@/styles/apeui-theme.css'
import 'vue3-verify/dist/vue3-verify.css'

import App from './App.vue'
import router from './router'
import { permissionDirective } from './directives/permission'
import { initTheme } from './composables/useTheme'
import { useSettingsStore } from './stores/settings'
import i18n, { getLocale, setLocale } from './locales'

// Element Plus locale maps
import elZhCn from 'element-plus/es/locale/lang/zh-cn'
import elEn from 'element-plus/es/locale/lang/en'

const app = createApp(App)

// 应用已保存的主题（深色/浅色），需在挂载前执行以避免闪白
initTheme()

// Register all Element Plus icons globally
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(i18n)

// Sync Element Plus locale with i18n locale
const elLocaleMap: Record<string, any> = { 'zh-CN': elZhCn, 'en-US': elEn }
app.use(ElementPlus, { locale: elLocaleMap[getLocale()] || elZhCn })

// Apply initial locale attributes
setLocale(getLocale())

// Watch for locale changes to update Element Plus locale at runtime
// (Element Plus locale is reactive via app.provide)
import { watch } from 'vue'
watch(() => (i18n.global.locale as any).value, (newLocale) => {
  app.provide('elLocale', elLocaleMap[newLocale] || elZhCn)
})

// Register global directives
app.directive('permission', permissionDirective)

// Fetch public settings and apply theme color before mount
const settingsStore = useSettingsStore()
settingsStore.fetchPublicSettings().finally(() => {
  app.mount('#app')
})
