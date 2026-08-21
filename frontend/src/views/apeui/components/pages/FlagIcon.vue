<template>
  <div>
    <PageHeader title="国旗图标" :breadcrumb="['APEUI库', '组件示例', '国旗图标']" />

    <el-card shadow="hover">
      <template #header>Unicode Emoji Flags</template>
      <div class="flag-grid">
        <div v-for="item in flags" :key="item.name" class="flag-item">
          <span class="flag-emoji">{{ item.emoji }}</span>
          <span class="flag-name">{{ item.name }}</span>
          <code class="flag-code">{{ item.code }}</code>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'

const flags = [
  { emoji: '🇨🇳', name: '中国', code: 'CN' },
  { emoji: '🇺🇸', name: '美国', code: 'US' },
  { emoji: '🇬🇧', name: '英国', code: 'GB' },
  { emoji: '🇯🇵', name: '日本', code: 'JP' },
  { emoji: '🇰🇷', name: '韩国', code: 'KR' },
  { emoji: '🇩🇪', name: '德国', code: 'DE' },
  { emoji: '🇫🇷', name: '法国', code: 'FR' },
  { emoji: '🇮🇹', name: '意大利', code: 'IT' },
  { emoji: '🇪🇸', name: '西班牙', code: 'ES' },
  { emoji: '🇨🇦', name: '加拿大', code: 'CA' },
  { emoji: '🇦🇺', name: '澳大利亚', code: 'AU' },
  { emoji: '🇧🇷', name: '巴西', code: 'BR' },
  { emoji: '🇮🇳', name: '印度', code: 'IN' },
  { emoji: '🇷🇺', name: '俄罗斯', code: 'RU' },
  { emoji: '🇲🇽', name: '墨西哥', code: 'MX' },
  { emoji: '🇸🇦', name: '沙特阿拉伯', code: 'SA' },
  { emoji: '🇿🇦', name: '南非', code: 'ZA' },
  { emoji: '🇸🇬', name: '新加坡', code: 'SG' },
  { emoji: '🇹🇭', name: '泰国', code: 'TH' },
  { emoji: '🇻🇳', name: '越南', code: 'VN' },
  { emoji: '🇮🇩', name: '印度尼西亚', code: 'ID' },
  { emoji: '🇲🇾', name: '马来西亚', code: 'MY' },
  { emoji: '🇵🇭', name: '菲律宾', code: 'PH' },
  { emoji: '🇪🇬', name: '埃及', code: 'EG' },
  { emoji: '🇹🇷', name: '土耳其', code: 'TR' },
  { emoji: '🇳🇱', name: '荷兰', code: 'NL' },
  { emoji: '🇸🇪', name: '瑞典', code: 'SE' },
  { emoji: '🇨🇭', name: '瑞士', code: 'CH' },
  { emoji: '🇧🇪', name: '比利时', code: 'BE' },
  { emoji: '🇦🇹', name: '奥地利', code: 'AT' },
]
</script>

<style scoped>
.flag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}
.flag-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 8px;
  border-radius: 8px;
  background: #f9f8fd;
  transition: background 0.2s;
}
.flag-item:hover {
  background: #ede8f7;
}
.flag-emoji {
  font-size: 40px;
  line-height: 1;
}
.flag-name {
  font-size: 13px;
  font-weight: 600;
  color: #303030;
}
.flag-code {
  font-size: 11px;
  color: #909399;
  background: none;
}
</style>
