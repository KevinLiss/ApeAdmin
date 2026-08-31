/**
 * System settings store — manages runtime-configurable site settings.
 *
 * Public settings (site_name, logo_url, primary_color, etc.) are fetched
 * on app startup and applied to the layout (sidebar brand, theme color, etc.).
 */
import { defineStore } from 'pinia'
import { getPublicSettings } from '@/api'

interface SettingsState {
  site_name: string
  logo_url: string
  primary_color: string
  admin_path: string
  footer_text: string
  login_bg: string
  sidebar_theme: string
  loaded: boolean
}

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => ({
    site_name: 'ApeAdmin',
    logo_url: '',
    primary_color: '#5A67F5',
    admin_path: '/admin',
    footer_text: 'ApeAdmin © 2026',
    login_bg: '',
    sidebar_theme: 'light',
    loaded: false,
  }),

  actions: {
    /** Fetch public settings from backend and apply them */
    async fetchPublicSettings() {
      try {
        const data: any = await getPublicSettings()
        if (data) {
          if (data.site_name) this.site_name = data.site_name
          if (data.logo_url !== undefined) this.logo_url = data.logo_url
          if (data.primary_color) this.primary_color = data.primary_color
          if (data.admin_path) this.admin_path = data.admin_path
          if (data.footer_text !== undefined) this.footer_text = data.footer_text
          if (data.login_bg !== undefined) this.login_bg = data.login_bg
          if (data.sidebar_theme) this.sidebar_theme = data.sidebar_theme
        }
        this.loaded = true
        this.applyThemeColor()
      } catch {
        // Backend might be unreachable on first load; use defaults
        this.loaded = true
      }
    },

    /** Apply primary_color to CSS variables */
    applyThemeColor() {
      const color = this.primary_color
      if (!color || !color.startsWith('#')) return
      const root = document.documentElement
      root.style.setProperty('--el-color-primary', color)
      root.style.setProperty('--theme-default', color)

      // Derive light variants (simple mix with white)
      const rgb = hexToRgb(color)
      if (rgb) {
        root.style.setProperty('--el-color-primary-rgb', `${rgb.r}, ${rgb.g}, ${rgb.b}`)
        for (const pct of [3, 5, 7, 8, 9]) {
          const mixed = mixWithWhite(rgb, pct * 10)
          root.style.setProperty(`--el-color-primary-light-${pct}`, mixed)
        }
        const dark2 = darken(rgb, 0.12)
        root.style.setProperty('--el-color-primary-dark-2', dark2)
      }
    },
  },
})

/** Convert hex color to {r, g, b} */
function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  if (!m) return null
  return { r: parseInt(m[1], 16), g: parseInt(m[2], 16), b: parseInt(m[3], 16) }
}

/** Mix a color with white: ratio=0 → white, ratio=1 → original */
function mixWithWhite(rgb: { r: number; g: number; b: number }, whitePct: number): string {
  const ratio = 1 - whitePct / 100
  const r = Math.round(rgb.r * ratio + 255 * (1 - ratio))
  const g = Math.round(rgb.g * ratio + 255 * (1 - ratio))
  const b = Math.round(rgb.b * ratio + 255 * (1 - ratio))
  return `#${[r, g, b].map(x => x.toString(16).padStart(2, '0')).join('')}`
}

/** Darken a color by a ratio (0-1) */
function darken(rgb: { r: number; g: number; b: number }, ratio: number): string {
  const r = Math.round(rgb.r * (1 - ratio))
  const g = Math.round(rgb.g * (1 - ratio))
  const b = Math.round(rgb.b * (1 - ratio))
  return `#${[r, g, b].map(x => x.toString(16).padStart(2, '0')).join('')}`
}
