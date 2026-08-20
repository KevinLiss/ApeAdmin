<template>
  <div class="apeui-page" v-html="htmlContent"></div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const htmlContent = ref('')
const loading = ref(false)

async function loadPage(page: string) {
  if (!page) return
  loading.value = true
  try {
    const resp = await fetch(`/koho/${page}.html`)
    if (!resp.ok) {
      htmlContent.value = `<div style="padding:40px;text-align:center;color:#999;">页面 ${page} 加载失败 (${resp.status})</div>`
      return
    }
    let html = await resp.text()
    // 提取 page-body 区域（Koho 主内容）
    const bodyStart = html.indexOf('class="page-body"')
    if (bodyStart > 0) {
      const bodyEnd = html.indexOf('<!-- footer', bodyStart)
      const bodyEnd2 = html.indexOf('<footer', bodyStart)
      const end = [bodyEnd, bodyEnd2].filter((v) => v > 0).sort((a, b) => a - b)[0]
      const tagStart = html.lastIndexOf('<div', bodyStart)
      htmlContent.value = html.substring(tagStart, end > 0 ? end : html.length)
    } else {
      const cfStart = html.indexOf('container-fluid')
      if (cfStart > 0) {
        const tagStart = html.lastIndexOf('<div', cfStart)
        htmlContent.value = html.substring(tagStart)
      } else {
        htmlContent.value = html
      }
    }
    await nextTick()
    initFeatherIcons()
    if ((window as any).Prism) (window as any).Prism.highlightAll()
  } catch (e: any) {
    htmlContent.value = `<div style="padding:40px;text-align:center;color:#f56c6c;">加载出错: ${e.message}</div>`
  } finally {
    loading.value = false
  }
}

function initFeatherIcons() {
  if ((window as any).feather) {
    ;(window as any).feather.replace({ 'stroke-width': 2 })
  }
}

onMounted(() => {
  const page = (route.params.page as string) || 'index'
  loadPage(page)
})

watch(
  () => route.params.page,
  (newPage) => {
    if (newPage) loadPage(newPage as string)
  },
)
</script>

<style scoped>
.apeui-page {
  padding: 20px;
}
.apeui-page :deep(.container-fluid) {
  width: 100%;
}
.apeui-page :deep(.page-title) {
  margin-bottom: 20px;
}
</style>