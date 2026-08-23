<template>
  <div>
    <PageHeader title="面包屑" :breadcrumb="['APEUI库', '组件示例', '面包屑']" />

    <el-row :gutter="30">
      <!-- 1. 默认面包屑 -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">默认面包屑</span>
            </div>
          </template>
          <div class="breadcrumb-sections">
            <div class="breadcrumb-section">
              <div class="section-label">1 级</div>
              <el-breadcrumb separator="/">
                <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <div class="breadcrumb-section">
              <div class="section-label">2 级</div>
              <el-breadcrumb separator="/">
                <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
                <el-breadcrumb-item>Library</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <div class="breadcrumb-section">
              <div class="section-label">3 级</div>
              <el-breadcrumb separator="/">
                <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
                <el-breadcrumb-item :to="{ path: '/' }">Library</el-breadcrumb-item>
                <el-breadcrumb-item>Data</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <div class="breadcrumb-section">
              <div class="section-label">带图标</div>
              <el-breadcrumb separator="/">
                <el-breadcrumb-item :to="{ path: '/' }">
                  <el-icon><HomeFilled /></el-icon>
                  Home
                </el-breadcrumb-item>
                <el-breadcrumb-item>Library</el-breadcrumb-item>
                <el-breadcrumb-item>Data</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 2. Breadcrumb Styles -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">Breadcrumb Styles</span>
            </div>
          </template>
          <div class="breadcrumb-sections">
            <div class="breadcrumb-section">
              <div class="section-label">标准</div>
              <el-breadcrumb :separator-icon="ArrowRight">
                <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
                <el-breadcrumb-item :to="{ path: '/' }">Library</el-breadcrumb-item>
                <el-breadcrumb-item>ApeAdmin</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <div class="breadcrumb-section">
              <div class="section-label">图标分隔</div>
              <el-breadcrumb :separator-icon="ArrowRight">
                <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
                <el-breadcrumb-item :to="{ path: '/' }">Library</el-breadcrumb-item>
                <el-breadcrumb-item>ApeAdmin</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <div class="breadcrumb-section">
              <div class="section-label">无分隔符</div>
              <div class="no-separator-breadcrumb">
                <span class="no-sep-item">Home</span>
                <span class="no-sep-item">Library</span>
                <span class="no-sep-item">ApeAdmin</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 3. Colored Breadcrumb -->
    <el-row :gutter="30">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">Colored Breadcrumb</span>
            </div>
          </template>
          <div class="colored-breadcrumb-grid">
            <div
              v-for="item in coloredBreadcrumbs"
              :key="item.name"
              class="colored-breadcrumb-item"
              :style="{ background: item.bg }"
            >
              <el-breadcrumb
                :separator="item.separator"
                :class="['colored-breadcrumb', item.isLight ? 'colored-breadcrumb--light' : '']"
              >
                <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
                <el-breadcrumb-item>Library</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ArrowRight, HomeFilled } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const coloredBreadcrumbs = [
  { name: 'Primary', bg: '#5A67F5', separator: '/', isLight: false },
  { name: 'Secondary', bg: '#FFA47A', separator: '/', isLight: false },
  { name: 'Success', bg: '#67C100', separator: '/', isLight: false },
  { name: 'Info', bg: '#3EBCB9', separator: '/', isLight: false },
  { name: 'Warning', bg: '#E56809', separator: '/', isLight: false },
  { name: 'Danger', bg: '#DC0808', separator: '/', isLight: false },
  { name: 'Light', bg: '#F4F4F4', separator: '/', isLight: true },
  { name: 'Dark', bg: '#2C323F', separator: '/', isLight: false },
]
</script>

<style scoped>
.card-col {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-title {
  font-weight: 600;
  font-size: 15px;
  color: #5A67F5;
}

.breadcrumb-sections {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.breadcrumb-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid #f0f0f5;
}

.breadcrumb-section:last-child {
  border-bottom: none;
}

.section-label {
  width: 80px;
  flex-shrink: 0;
  color: #909399;
  font-size: 13px;
  font-weight: 500;
}

/* 无分隔符面包屑 */
.no-separator-breadcrumb {
  display: flex;
  align-items: center;
}

.no-sep-item {
  font-size: 14px;
  color: #5A67F5;
  margin-right: 24px;
  position: relative;
}

.no-sep-item:last-child {
  color: #606266;
  margin-right: 0;
}

/* 彩色面包屑网格 */
.colored-breadcrumb-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.colored-breadcrumb-item {
  padding: 12px 16px;
  border-radius: 6px;
  display: flex;
  align-items: center;
}

/* 深色背景 - 白色文字 */
.colored-breadcrumb :deep(.el-breadcrumb__item) {
  font-size: 14px;
}

.colored-breadcrumb :deep(.el-breadcrumb__inner) {
  color: #fff !important;
  font-weight: 500;
}

.colored-breadcrumb :deep(.el-breadcrumb__inner a) {
  color: rgba(255, 255, 255, 0.85) !important;
  font-weight: 500;
}

.colored-breadcrumb :deep(.el-breadcrumb__inner a:hover) {
  color: #fff !important;
}

.colored-breadcrumb :deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.6) !important;
}

/* 浅色背景 - 深色文字 */
.colored-breadcrumb--light :deep(.el-breadcrumb__inner) {
  color: #2C323F !important;
}

.colored-breadcrumb--light :deep(.el-breadcrumb__inner a) {
  color: #5A67F5 !important;
}

.colored-breadcrumb--light :deep(.el-breadcrumb__inner a:hover) {
  color: #2C323F !important;
}

.colored-breadcrumb--light :deep(.el-breadcrumb__separator) {
  color: #909399 !important;
}
</style>
