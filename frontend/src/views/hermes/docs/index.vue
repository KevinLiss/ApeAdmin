<template>
  <div class="hermes-docs-page">
    <div class="docs-toolbar">
      <span class="docs-title">Hermes 官方文档</span>
      <el-button tag="a" :href="HERMES_DOCS_URL" target="_blank" rel="noopener noreferrer">
        新窗口打开
      </el-button>
    </div>
    <!-- 文档站为浅色主题，强制 color-scheme:light 保证深色模式下可读 -->
    <iframe
      :src="HERMES_DOCS_URL"
      class="docs-frame"
      style="color-scheme: light; background: #fff"
      sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
      referrerpolicy="no-referrer-when-downgrade"
      title="Hermes 文档"
    />
  </div>
</template>

<script setup lang="ts">
const HERMES_DOCS_URL = 'https://hermes-agent.nousresearch.com/docs/'
</script>

<style scoped>
.hermes-docs-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  gap: 12px;
}

.docs-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.docs-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.docs-frame {
  flex: 1;
  min-height: 0;
  width: 100%;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
}
</style>
