<template>
  <div>
    <PageHeader title="Draggable Card" :breadcrumb="['APEUI库', 'Components', 'Draggable Card']" />

    <el-card shadow="hover" style="margin-bottom: 16px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600; color: #5A67F5">可拖拽排序卡片</span>
          <el-button type="primary" size="small" @click="resetList">
            <el-icon><Refresh /></el-icon>
            <span>重置</span>
          </el-button>
        </div>
      </template>
      <p style="margin: 0 0 16px; color: #909399; font-size: 13px">
        <el-icon><InfoFilled /></el-icon>
        拖拽卡片可重新排序，支持跨列拖拽。
      </p>
      <draggable
        v-model="cardList"
        :group="{ name: 'cards' }"
        item-key="id"
        ghost-class="drag-ghost"
        chosen-class="drag-chosen"
        animation="200"
        class="drag-grid"
      >
        <template #item="{ element }">
          <div class="drag-card-wrapper">
            <el-card shadow="hover" class="drag-card">
              <div class="drag-card-header" :style="{ background: element.gradient }">
                <el-icon :size="28" color="#fff"><component :is="element.icon" /></el-icon>
                <span class="drag-handle">⋮⋮</span>
              </div>
              <div class="drag-card-body">
                <h4 style="margin: 0 0 4px; font-weight: 600; color: #5A67F5">{{ element.title }}</h4>
                <p style="margin: 0; color: #909399; font-size: 13px">{{ element.desc }}</p>
                <div class="drag-card-meta">
                  <el-tag size="small" :type="element.tagType">{{ element.tag }}</el-tag>
                  <span class="drag-order">#{{ element.id }}</span>
                </div>
              </div>
            </el-card>
          </div>
        </template>
      </draggable>
    </el-card>

    <el-card shadow="hover">
      <template #header>
        <span style="font-weight: 600; color: #5A67F5">当前排序</span>
      </template>
      <div class="order-display">
        <el-tag
          v-for="(item, idx) in cardList"
          :key="item.id"
          :type="idx === 0 ? 'success' : 'info'"
          effect="plain"
          style="margin: 0 8px 8px 0"
        >
          {{ idx + 1 }}. {{ item.title }}
        </el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Refresh, InfoFilled, Cpu, Monitor, DataLine, Bell, Setting, Box } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'
import draggable from 'vuedraggable'

interface DragCard {
  id: number
  title: string
  desc: string
  icon: typeof Cpu
  gradient: string
  tag: string
  tagType: '' | 'success' | 'warning' | 'info' | 'danger'
}

const defaultCards: DragCard[] = [
  { id: 1, title: '计算资源', desc: 'CPU & GPU 集群', icon: Cpu, gradient: 'linear-gradient(135deg, #5A67F5, #7F8AF8)', tag: '运行中', tagType: 'success' },
  { id: 2, title: '监控面板', desc: '实时系统监控', icon: Monitor, gradient: 'linear-gradient(135deg, #3B46C8, #5A67F5)', tag: '正常', tagType: 'success' },
  { id: 3, title: '数据分析', desc: '数据趋势分析', icon: DataLine, gradient: 'linear-gradient(135deg, #5A67F5, #A5ACFA)', tag: '处理中', tagType: 'warning' },
  { id: 4, title: '消息中心', desc: '通知与告警', icon: Bell, gradient: 'linear-gradient(135deg, #7F8AF8, #5A67F5)', tag: '3条新', tagType: 'danger' },
  { id: 5, title: '系统设置', desc: '全局配置管理', icon: Setting, gradient: 'linear-gradient(135deg, #4a3f7a, #6b5fa0)', tag: '已配置', tagType: 'info' },
  { id: 6, title: '存储管理', desc: '云端文件存储', icon: Box, gradient: 'linear-gradient(135deg, #5A67F5, #8FA0FF)', tag: '运行中', tagType: 'success' },
]

const cardList = ref<DragCard[]>([...defaultCards])

const resetList = () => {
  cardList.value = [...defaultCards]
}
</script>

<style scoped>
.drag-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.drag-card-wrapper {
  cursor: grab;
}
.drag-card {
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.drag-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(90, 103, 245, 0.15);
}
.drag-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
}
.drag-handle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 18px;
  letter-spacing: -2px;
  cursor: grab;
}
.drag-card-body {
  padding: 14px 20px;
}
.drag-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}
.drag-order {
  color: #c0c4cc;
  font-size: 13px;
  font-weight: 600;
}
.drag-ghost {
  opacity: 0.4;
  background: #f0eef7 !important;
}
.drag-chosen {
  cursor: grabbing;
}
.order-display {
  display: flex;
  flex-wrap: wrap;
}
</style>
