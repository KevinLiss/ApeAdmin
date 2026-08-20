<template>
  <div>
    <PageHeader title="Basic Card" :breadcrumb="['APEUI库', 'Components', 'Basic Card']" />

    <el-row :gutter="16">
      <el-col :span="8" style="margin-bottom: 16px">
        <el-card shadow="always" header="Shadow Always">
          <p style="margin: 0; color: #5a6273">始终显示阴影的卡片。适用于需要持续强调的重要信息区域。</p>
        </el-card>
      </el-col>
      <el-col :span="8" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Shadow Hover">
          <p style="margin: 0; color: #5a6273">鼠标悬浮时显示阴影。最常用的卡片阴影模式。</p>
        </el-card>
      </el-col>
      <el-col :span="8" style="margin-bottom: 16px">
        <el-card shadow="never" header="Shadow Never">
          <p style="margin: 0; color: #5a6273">从不显示阴影，扁平风格。适合紧凑的列表场景。</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" header="Header + Body 结构" style="margin-bottom: 16px">
      <template #header>
        <div class="card-header-flex">
          <span class="card-title">自定义 Header</span>
          <el-button type="primary" size="small">操作按钮</el-button>
        </div>
      </template>
      <p style="margin: 0 0 12px; color: #5a6273">卡片由 Header 和 Body 两个区域组成，Header 可通过 #header 插槽自定义。</p>
      <p style="margin: 0; color: #909399; font-size: 13px">This is the card body content area.</p>
    </el-card>

    <el-card shadow="hover" header="带分隔线" style="margin-bottom: 16px">
      <div class="divider-list">
        <div class="divider-item" v-for="item in listItems" :key="item">
          <span>{{ item }}</span>
          <el-icon color="#534686"><ArrowRight /></el-icon>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover">
      <template #header>
        <span class="card-title">简洁卡片</span>
      </template>
      <div style="display: flex; gap: 24px; align-items: center">
        <el-avatar :size="48" style="background: #534686">
          <el-icon :size="22"><User /></el-icon>
        </el-avatar>
        <div>
          <h4 style="margin: 0 0 4px; font-weight: 600">用户名：ApeAdmin</h4>
          <p style="margin: 0; color: #909399; font-size: 13px">角色：超级管理员 | 状态：在线</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ArrowRight, User } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const listItems = ['账户设置', '安全中心', '通知偏好', '隐私管理', '退出登录']

</script>

<style scoped>
.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-title {
  font-weight: 600;
  color: #534686;
}
.divider-list {
  display: flex;
  flex-direction: column;
}
.divider-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid #f0f0f5;
  cursor: pointer;
  transition: color 0.2s;
}
.divider-item:last-child {
  border-bottom: none;
}
.divider-item:hover {
  color: #534686;
}
</style>
