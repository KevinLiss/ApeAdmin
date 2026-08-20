<template>
  <div>
    <PageHeader title="Flag Icons" :breadcrumb="['APEUI库', 'Components', 'Flag Icons']" />

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
  { emoji: '🇨🇳', name: 'China', code: 'CN' },
  { emoji: '🇺🇸', name: 'United States', code: 'US' },
  { emoji: '🇬🇧', name: 'United Kingdom', code: 'GB' },
  { emoji: '🇯🇵', name: 'Japan', code: 'JP' },
  { emoji: '🇰🇷', name: 'South Korea', code: 'KR' },
  { emoji: '🇩🇪', name: 'Germany', code: 'DE' },
  { emoji: '🇫🇷', name: 'France', code: 'FR' },
  { emoji: '🇮🇹', name: 'Italy', code: 'IT' },
  { emoji: '🇪🇸', name: 'Spain', code: 'ES' },
  { emoji: '🇨🇦', name: 'Canada', code: 'CA' },
  { emoji: '🇦🇺', name: 'Australia', code: 'AU' },
  { emoji: '🇧🇷', name: 'Brazil', code: 'BR' },
  { emoji: '🇮🇳', name: 'India', code: 'IN' },
  { emoji: '🇷🇺', name: 'Russia', code: 'RU' },
  { emoji: '🇲🇽', name: 'Mexico', code: 'MX' },
  { emoji: '🇸🇦', name: 'Saudi Arabia', code: 'SA' },
  { emoji: '🇿🇦', name: 'South Africa', code: 'ZA' },
  { emoji: '🇸🇬', name: 'Singapore', code: 'SG' },
  { emoji: '🇹🇭', name: 'Thailand', code: 'TH' },
  { emoji: '🇻🇳', name: 'Vietnam', code: 'VN' },
  { emoji: '🇮🇩', name: 'Indonesia', code: 'ID' },
  { emoji: '🇲🇾', name: 'Malaysia', code: 'MY' },
  { emoji: '🇵🇭', name: 'Philippines', code: 'PH' },
  { emoji: '🇪🇬', name: 'Egypt', code: 'EG' },
  { emoji: '🇹🇷', name: 'Turkey', code: 'TR' },
  { emoji: '🇳🇱', name: 'Netherlands', code: 'NL' },
  { emoji: '🇸🇪', name: 'Sweden', code: 'SE' },
  { emoji: '🇨🇭', name: 'Switzerland', code: 'CH' },
  { emoji: '🇧🇪', name: 'Belgium', code: 'BE' },
  { emoji: '🇦🇹', name: 'Austria', code: 'AT' },
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
