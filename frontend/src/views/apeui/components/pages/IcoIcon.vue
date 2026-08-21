<template>
  <div>
    <PageHeader title="Ico 图标" :breadcrumb="['APEUI库', '组件示例', 'Ico 图标']" />

    <el-card shadow="hover">
      <template #header>Element Plus Icons — Data &amp; Media</template>
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
  Upload, Download, Cloudy, Sunny, Moon, Lightning, Umbrella, Coffee, IceCream,
  Pear, Apple, Cherry, Watermelon, Grape, Burger, Football, Basketball, Soccer, Comment,
  TrendCharts, DataLine, DataBoard, DataAnalysis, PieChart, Histogram, Guide,
  Management, Operation, Platform, Remove, CircleCheck, CircleCheckFilled,
  CircleClose, CircleCloseFilled, Warning, WarningFilled, Help, HelpFilled,
  InfoFilled, RemoveFilled, SuccessFilled, QuestionFilled, Film, Lollipop,
} from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const icons: { name: string; component: Component }[] = [
  { name: 'Upload', component: Upload },
  { name: 'Download', component: Download },
  { name: 'Cloudy', component: Cloudy },
  { name: 'Sunny', component: Sunny },
  { name: 'Moon', component: Moon },
  { name: 'Lightning', component: Lightning },
  { name: 'Umbrella', component: Umbrella },
  { name: 'Coffee', component: Coffee },
  { name: 'IceCream', component: IceCream },
  { name: 'Pear', component: Pear },
  { name: 'Apple', component: Apple },
  { name: 'Cherry', component: Cherry },
  { name: 'Watermelon', component: Watermelon },
  { name: 'Grape', component: Grape },
  { name: 'Burger', component: Burger },
  { name: 'Football', component: Football },
  { name: 'Basketball', component: Basketball },
  { name: 'Soccer', component: Soccer },
  { name: 'TrendCharts', component: TrendCharts },
  { name: 'DataLine', component: DataLine },
  { name: 'DataBoard', component: DataBoard },
  { name: 'DataAnalysis', component: DataAnalysis },
  { name: 'PieChart', component: PieChart },
  { name: 'Histogram', component: Histogram },
  { name: 'Guide', component: Guide },
  { name: 'Management', component: Management },
  { name: 'Operation', component: Operation },
  { name: 'Platform', component: Platform },
  { name: 'Remove', component: Remove },
  { name: 'CircleCheck', component: CircleCheck },
  { name: 'CircleCheckFilled', component: CircleCheckFilled },
  { name: 'CircleClose', component: CircleClose },
  { name: 'CircleCloseFilled', component: CircleCloseFilled },
  { name: 'Warning', component: Warning },
  { name: 'WarningFilled', component: WarningFilled },
  { name: 'Help', component: Help },
  { name: 'HelpFilled', component: HelpFilled },
  { name: 'InfoFilled', component: InfoFilled },
  { name: 'RemoveFilled', component: RemoveFilled },
  { name: 'SuccessFilled', component: SuccessFilled },
  { name: 'QuestionFilled', component: QuestionFilled },
  { name: 'Film', component: Film },
  { name: 'Lollipop', component: Lollipop },
  { name: 'Comment', component: Comment },
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
