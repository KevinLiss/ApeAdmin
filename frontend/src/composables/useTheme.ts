/**
 * 全局主题 composable —— 暗色/浅色模式切换与持久化
 * 用法：
 *   const { isDark, applyDark, toggleDark } = useTheme()
 */
import { ref } from 'vue'

const THEME_KEY = 'apeadmin_theme'

// 模块级单例状态，多个组件共享同一份 isDark
const isDark = ref<boolean>(localStorage.getItem(THEME_KEY) === 'dark')

/** 将 dark class 应用到 documentElement，并持久化 */
export function applyDark(dark: boolean) {
  isDark.value = dark
  const root = document.documentElement
  if (dark) {
    root.classList.add('dark')
    localStorage.setItem(THEME_KEY, 'dark')
  } else {
    root.classList.remove('dark')
    localStorage.setItem(THEME_KEY, 'light')
  }
}

/** 初始化：应用已保存的主题（App 启动时调用一次） */
export function initTheme() {
  applyDark(isDark.value)
}

/** 切换主题并返回新状态 */
export function toggleDark(): boolean {
  applyDark(!isDark.value)
  return isDark.value
}

export function useTheme() {
  return { isDark, applyDark, toggleDark, initTheme }
}