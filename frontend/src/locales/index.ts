import { createI18n } from 'vue-i18n'
import type { I18n } from 'vue-i18n'

// Import translation files
import zhCNCommon from './zh-CN/common.json'
import zhCNMenu from './zh-CN/menu.json'
import zhCNAuth from './zh-CN/auth.json'
import zhCNDashboard from './zh-CN/dashboard.json'
import zhCNSystem from './zh-CN/system.json'

import enUSCommon from './en-US/common.json'
import enUSMenu from './en-US/menu.json'
import enUSAuth from './en-US/auth.json'
import enUSDashboard from './en-US/dashboard.json'
import enUSSystem from './en-US/system.json'

export type Locale = 'zh-CN' | 'en-US'

export const SUPPORTED_LOCALES: { label: string; value: Locale }[] = [
  { label: '简体中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' },
]

/** Detect initial locale: localStorage → browser language → default zh-CN */
function detectLocale(): Locale {
  // 1. User manually selected (stored in localStorage)
  const stored = localStorage.getItem('locale')
  if (stored && (stored === 'zh-CN' || stored === 'en-US')) return stored

  // 2. Browser language detection (first visit)
  const browserLang = navigator.language || (navigator as any).userLanguage || 'zh-CN'
  if (browserLang.startsWith('zh')) return 'zh-CN'
  if (browserLang.startsWith('en')) return 'en-US'

  // 3. Default to Chinese
  return 'zh-CN'
}

const i18n: I18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': {
      common: zhCNCommon,
      menu: zhCNMenu,
      auth: zhCNAuth,
      dashboard: zhCNDashboard,
      system: zhCNSystem,
    },
    'en-US': {
      common: enUSCommon,
      menu: enUSMenu,
      auth: enUSAuth,
      dashboard: enUSDashboard,
      system: enUSSystem,
    },
  },
})

/** Switch locale and persist to localStorage + update Accept-Language header */
export function setLocale(locale: Locale) {
  ;(i18n.global.locale as any).value = locale
  localStorage.setItem('locale', locale)
  // Update axios default header for all subsequent requests
  document.documentElement.setAttribute('lang', locale)
}

/** Get current locale */
export function getLocale(): Locale {
  return (i18n.global.locale as any).value as Locale
}

export default i18n
