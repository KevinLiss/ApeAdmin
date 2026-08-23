import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import '@/styles/apeui-theme.css'

import App from './App.vue'
import router from './router'
import { permissionDirective } from './directives/permission'
import { initTheme } from './composables/useTheme'

const app = createApp(App)

// 应用已保存的主题（深色/浅色），需在挂载前执行以避免闪白
initTheme()

// Register all Element Plus icons globally
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// Register global directives
app.directive('permission', permissionDirective)

app.mount('#app')
