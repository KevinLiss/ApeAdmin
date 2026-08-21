<template>
  <div>
    <PageHeader title="Bootstrap 标签页" :breadcrumb="['APEUI库', '组件示例', 'Bootstrap 标签页']" />

    <el-card shadow="hover" header="基础标签页（默认样式）" style="margin-bottom: 16px">
      <el-tabs v-model="activeName1">
        <el-tab-pane label="看板" name="dashboard">这里是看板面板内容。</el-tab-pane>
        <el-tab-pane label="分析" name="analytics">这里是分析面板内容。</el-tab-pane>
        <el-tab-pane label="报表" name="reports">这里是报表面板内容。</el-tab-pane>
        <el-tab-pane label="设置" name="settings">这里是设置面板内容。</el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="hover" header="卡片式标签页（type=card）" style="margin-bottom: 16px">
      <el-tabs v-model="activeName2" type="card">
        <el-tab-pane label="概览" name="overview">概览面板内容。</el-tab-pane>
        <el-tab-pane label="活动" name="activity">活动面板内容。</el-tab-pane>
        <el-tab-pane label="用户" name="users">用户面板内容。</el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="hover" header="边框卡片标签页（type=border-card）" style="margin-bottom: 16px">
      <el-tabs v-model="activeName3" type="border-card">
        <el-tab-pane label="概览" name="overview">边框卡片内的概览面板内容。</el-tab-pane>
        <el-tab-pane label="活动" name="activity">活动面板内容。</el-tab-pane>
        <el-tab-pane label="用户" name="users">用户面板内容。</el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="hover" header="带图标">
      <el-tabs v-model="activeName4" type="card">
        <el-tab-pane name="dashboard">
          <template #label>
            <span class="tab-label"><el-icon><Odometer /></el-icon> 看板</span>
          </template>
          看板面板内容。
        </el-tab-pane>
        <el-tab-pane name="users">
          <template #label>
            <span class="tab-label"><el-icon><User /></el-icon> 用户</span>
          </template>
          用户面板内容。
        </el-tab-pane>
        <el-tab-pane name="settings">
          <template #label>
            <span class="tab-label"><el-icon><Setting /></el-icon> 设置</span>
          </template>
          设置面板内容。
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Odometer, User, Setting } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const activeName1 = ref('dashboard')
const activeName2 = ref('overview')
const activeName3 = ref('overview')
const activeName4 = ref('dashboard')
</script>

<style scoped>
.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
</style>