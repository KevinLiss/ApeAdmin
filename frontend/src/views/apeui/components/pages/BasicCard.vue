<template>
  <div class="basic-card-page">
    <PageHeader title="Basic Card" :breadcrumb="['APEUI库', 'Components', 'Basic Card']" />

    <el-row :gutter="30">
      <!-- 1. Basic Card -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Basic Card</span>
          </template>
          <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p class="card-text">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </el-card>
      </el-col>

      <!-- 2. Flat Card -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover" class="flat-card">
          <template #header>
            <span class="card-title">Flat Card</span>
          </template>
          <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p class="card-text">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </el-card>
      </el-col>

      <!-- 3. Without Shadow -->
      <el-col :span="12" class="col-item">
        <el-card shadow="never" class="border-card">
          <template #header>
            <span class="card-title">Without Shadow</span>
          </template>
          <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p class="card-text">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </el-card>
      </el-col>

      <!-- 4. Icon in Heading -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover">
          <template #header>
            <div class="header-with-icon">
              <el-icon class="header-icon"><Star /></el-icon>
              <span class="card-title">Icon in Heading</span>
            </div>
          </template>
          <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p class="card-text">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </el-card>
      </el-col>

      <!-- 5. Card with Sub Title -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover">
          <template #header>
            <div class="header-subtitle">
              <span class="card-title">Card with Sub Title</span>
              <span class="card-subtitle">这是一个副标题描述</span>
            </div>
          </template>
          <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p class="card-text">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </el-card>
      </el-col>

      <!-- 6. Card with Footer -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Card with Footer</span>
          </template>
          <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p class="card-text">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
          <template #footer>
            <div class="card-footer-content">Card Footer</div>
          </template>
        </el-card>
      </el-col>

      <!-- 7. Primary Color Card -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover" class="card-primary-full">
          <template #header>
            <span class="card-title-light">Primary Color Card</span>
          </template>
          <p class="card-text-light">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p class="card-text-light">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </el-card>
      </el-col>

      <!-- 8. Success Color Card -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover" class="card-success-full">
          <template #header>
            <span class="card-title-light">Success Color Card</span>
          </template>
          <p class="card-text-light">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p class="card-text-light">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </el-card>
      </el-col>

      <!-- 9. Primary Color Header -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover" class="card-primary-header">
          <template #header>
            <span class="card-title-light">Primary Color Header</span>
          </template>
          <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p class="card-text">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </el-card>
      </el-col>

      <!-- 10. Primary Color Body -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover" class="card-primary-body">
          <template #header>
            <span class="card-title">Primary Color Body</span>
          </template>
          <p class="card-text-light">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p class="card-text-light">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </el-card>
      </el-col>

      <!-- 11. With Action Buttons -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover">
          <template #header>
            <div class="header-with-actions">
              <span class="card-title">With Action Buttons</span>
              <div class="header-actions">
                <el-button text size="small" class="action-btn"><el-icon><Setting /></el-icon></el-button>
                <el-button text size="small" class="action-btn"><el-icon><Refresh /></el-icon></el-button>
                <el-button text size="small" class="action-btn"><el-icon><Close /></el-icon></el-button>
              </div>
            </div>
          </template>
          <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p class="card-text">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </el-card>
      </el-col>

      <!-- 12. With List -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">With List</span>
          </template>
          <ul class="card-list">
            <li class="card-list-item" v-for="(item, idx) in listItems" :key="idx">
              <span class="list-text">{{ item }}</span>
              <el-icon class="list-arrow"><ArrowRight /></el-icon>
            </li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { Star, Setting, Refresh, Close, ArrowRight } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const listItems = [
  '账户设置',
  '安全中心',
  '通知偏好',
  '隐私管理',
  '退出登录'
]
</script>

<style scoped>
.col-item {
  margin-bottom: 30px;
}
.card-title {
  font-weight: 600;
  color: #5A67F5;
  font-size: 15px;
}
.card-title-light {
  font-weight: 600;
  color: #ffffff;
  font-size: 15px;
}
.card-subtitle {
  display: block;
  font-size: 12px;
  font-weight: 400;
  color: #909399;
  margin-top: 2px;
}
.card-text {
  margin: 0 0 12px 0;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.7;
}
.card-text:last-child {
  margin-bottom: 0;
}
.card-text-light {
  margin: 0 0 12px 0;
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
  line-height: 1.7;
}
.card-text-light:last-child {
  margin-bottom: 0;
}

/* 2. Flat Card */
.flat-card {
  border-radius: 0 !important;
}

/* 3. Without Shadow + Border */
.border-card {
  border: 1px solid #e4e7ed;
}

/* 4. Icon in Heading */
.header-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
}
.header-icon {
  color: #5A67F5;
  font-size: 18px;
}

/* 5. Card with Sub Title */
.header-subtitle {
  display: flex;
  flex-direction: column;
}

/* 6. Card with Footer */
.card-footer-content {
  text-align: right;
  font-size: 13px;
  color: #909399;
  padding: 4px 0;
}

/* 7. Primary Color Card */
.card-primary-full {
  background: #5A67F5 !important;
  border-color: #5A67F5 !important;
}
.card-primary-full :deep(.el-card__header) {
  background: #5A67F5;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

/* 8. Success Color Card */
.card-success-full {
  background: #67C100 !important;
  border-color: #67C100 !important;
}
.card-success-full :deep(.el-card__header) {
  background: #67C100;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

/* 9. Primary Color Header */
.card-primary-header :deep(.el-card__header) {
  background: #5A67F5;
  border-bottom: none;
}

/* 10. Primary Color Body */
.card-primary-body :deep(.el-card__body) {
  background: #5A67F5;
}

/* 11. With Action Buttons */
.header-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-actions {
  display: flex;
  gap: 4px;
}
.action-btn {
  color: #5A67F5 !important;
  padding: 4px 6px !important;
}
.action-btn:hover {
  color: #4755E6 !important;
}

/* 12. With List */
.card-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.card-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f5;
  cursor: pointer;
  transition: color 0.2s;
}
.card-list-item:last-child {
  border-bottom: none;
}
.card-list-item:hover .list-text {
  color: #5A67F5;
}
.list-text {
  font-size: 13px;
  color: #6b7280;
  transition: color 0.2s;
}
.list-arrow {
  color: #c0c4cc;
  font-size: 12px;
}
</style>
