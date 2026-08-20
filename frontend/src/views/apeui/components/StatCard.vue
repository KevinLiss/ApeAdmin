<template>
  <el-row :gutter="16" class="stat-card-grid">
    <el-col :span="6" v-for="card in cards" :key="card.label">
      <div class="stat-card">
        <div class="stat-icon" :style="{ background: card.bg, color: card.color }">
          <el-icon :size="26"><component :is="card.icon" /></el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-label">{{ card.label }}</div>
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-trend" v-if="card.trend">
            <span :class="card.trendUp ? 'up' : 'down'">
              <el-icon><ArrowUp v-if="card.trendUp" /><ArrowDown v-else /></el-icon>
              {{ card.trend }}
            </span>
            <span style="color: #909399; margin-left: 4px">{{ card.trendLabel }}</span>
          </div>
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
defineProps<{
  cards: Array<{
    label: string
    value: string | number
    icon: string
    bg: string
    color: string
    trend?: string
    trendUp?: boolean
    trendLabel?: string
  }>
}>()
</script>
