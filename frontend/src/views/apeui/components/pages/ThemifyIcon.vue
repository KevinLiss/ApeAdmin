<template>
  <div>
    <PageHeader title="Themify 图标" :breadcrumb="['APEUI库', '组件示例', 'Themify 图标']" />

    <el-card shadow="hover">
      <template #header>Element Plus Icons — Arrows &amp; Navigation</template>
      <div class="icon-grid">
        <div v-for="item in icons" :key="item.name" class="icon-item">
          <el-icon :size="28"><component :is="item.component" /></el-icon>
          <span class="icon-name">{{ item.name }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import {
  ArrowUp, ArrowDown, ArrowLeft, ArrowRight, ArrowUpBold, ArrowDownBold,
  ArrowLeftBold, ArrowRightBold, CaretTop, CaretBottom, CaretLeft, CaretRight,
  DArrowLeft, DArrowRight, Back, Right, Top, Bottom, TopLeft, TopRight,
  BottomLeft, BottomRight, FullScreen, Rank, Sort, SortUp, SortDown, Expand,
  Fold, ScaleToOriginal, Crop, Refresh, RefreshLeft, RefreshRight, Select,
  School, Ship, Bicycle, Van, Stamp, Switch, Pointer, Share, Printer,
} from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const icons: { name: string; component: Component }[] = [
  { name: 'ArrowUp', component: ArrowUp },
  { name: 'ArrowDown', component: ArrowDown },
  { name: 'ArrowLeft', component: ArrowLeft },
  { name: 'ArrowRight', component: ArrowRight },
  { name: 'ArrowUpBold', component: ArrowUpBold },
  { name: 'ArrowDownBold', component: ArrowDownBold },
  { name: 'ArrowLeftBold', component: ArrowLeftBold },
  { name: 'ArrowRightBold', component: ArrowRightBold },
  { name: 'CaretTop', component: CaretTop },
  { name: 'CaretBottom', component: CaretBottom },
  { name: 'CaretLeft', component: CaretLeft },
  { name: 'CaretRight', component: CaretRight },
  { name: 'DArrowLeft', component: DArrowLeft },
  { name: 'DArrowRight', component: DArrowRight },
  { name: 'Back', component: Back },
  { name: 'Right', component: Right },
  { name: 'Top', component: Top },
  { name: 'Bottom', component: Bottom },
  { name: 'TopLeft', component: TopLeft },
  { name: 'TopRight', component: TopRight },
  { name: 'BottomLeft', component: BottomLeft },
  { name: 'BottomRight', component: BottomRight },
  { name: 'FullScreen', component: FullScreen },
  { name: 'Rank', component: Rank },
  { name: 'Sort', component: Sort },
  { name: 'SortUp', component: SortUp },
  { name: 'SortDown', component: SortDown },
  { name: 'Expand', component: Expand },
  { name: 'Fold', component: Fold },
  { name: 'ScaleToOriginal', component: ScaleToOriginal },
  { name: 'Crop', component: Crop },
  { name: 'Refresh', component: Refresh },
  { name: 'RefreshLeft', component: RefreshLeft },
  { name: 'RefreshRight', component: RefreshRight },
  { name: 'Select', component: Select },
  { name: 'School', component: School },
  { name: 'Ship', component: Ship },
  { name: 'Bicycle', component: Bicycle },
  { name: 'Van', component: Van },
  { name: 'Stamp', component: Stamp },
  { name: 'Switch', component: Switch },
  { name: 'Pointer', component: Pointer },
  { name: 'Share', component: Share },
  { name: 'Printer', component: Printer },
]
</script>

<style scoped>
.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}
.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  border-radius: 8px;
  background: #f9f8fd;
  transition: all 0.2s;
}
.icon-item:hover {
  background: #e8e3f3;
  transform: translateY(-2px);
}
.icon-name {
  font-size: 12px;
  color: #606266;
  text-align: center;
  word-break: break-all;
}
</style>
