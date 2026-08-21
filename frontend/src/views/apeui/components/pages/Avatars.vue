<template>
  <div class="avatars-page">
    <PageHeader title="头像" :breadcrumb="['APEUI库', '组件示例', '头像']" />

    <el-row :gutter="30">
      <!-- Sizing -->
      <el-col :span="12">
        <el-card class="avatar-card">
          <template #header>
            <span class="card-title">尺寸</span>
          </template>
          <div class="avatar-row">
            <el-avatar
              v-for="size in [100, 90, 80, 70, 60, 50, 40, 30, 20]"
              :key="size"
              :size="size"
              class="purple-avatar"
            >A</el-avatar>
          </div>
        </el-card>
      </el-col>

      <!-- Initials -->
      <el-col :span="12">
        <el-card class="avatar-card">
          <template #header>
            <span class="card-title">Initials</span>
          </template>
          <div class="avatar-row">
            <el-avatar
              v-for="size in [90, 80, 70, 60, 50, 40, 30, 20]"
              :key="size"
              :size="size"
              class="purple-avatar"
            >A</el-avatar>
          </div>
        </el-card>
      </el-col>

      <!-- Status Indicator -->
      <el-col :span="12">
        <el-card class="avatar-card">
          <template #header>
            <span class="card-title">Status Indicator</span>
          </template>
          <div class="avatar-row">
            <div
              v-for="size in [80, 70, 60, 50, 40, 30, 24, 20]"
              :key="size"
              class="status-wrapper"
              :style="{ width: size + 'px', height: size + 'px' }"
            >
              <el-avatar :size="size" class="purple-avatar">A</el-avatar>
              <span class="status-dot" :style="{ width: size * 0.28 + 'px', height: size * 0.28 + 'px' }"></span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Groups -->
      <el-col :span="12">
        <el-card class="avatar-card">
          <template #header>
            <span class="card-title">Groups</span>
          </template>
          <div class="groups-container">
            <div v-for="group in avatarGroups" :key="group.size" class="avatar-group-row">
              <span class="group-label">{{ group.size }}px</span>
              <div class="avatar-group">
                <el-avatar
                  v-for="(item, index) in group.items"
                  :key="index"
                  :size="group.size"
                  class="purple-avatar group-avatar"
                  :style="{ marginLeft: index === 0 ? '0' : '-' + group.size * 0.3 + 'px', zIndex: 10 - index }"
                >{{ item }}</el-avatar>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Shape -->
      <el-col :span="12">
        <el-card class="avatar-card">
          <template #header>
            <span class="card-title">Shape</span>
          </template>
          <div class="avatar-row">
            <el-avatar
              v-for="shape in shapes"
              :key="shape.label"
              :size="100"
              class="purple-avatar shape-avatar"
              :style="{ borderRadius: shape.radius }"
            >{{ shape.label }}</el-avatar>
          </div>
          <div class="shape-labels">
            <span v-for="shape in shapes" :key="shape.label + '-lbl'" class="shape-label">{{ shape.name }}</span>
          </div>
        </el-card>
      </el-col>

      <!-- Ratio -->
      <el-col :span="12">
        <el-card class="avatar-card">
          <template #header>
            <span class="card-title">Ratio</span>
          </template>
          <div class="avatar-row">
            <el-avatar
              v-for="ratio in ratios"
              :key="ratio.label"
              :size="100"
              class="purple-avatar ratio-avatar"
              :style="{ borderRadius: ratio.radius }"
            >{{ ratio.label }}</el-avatar>
          </div>
          <div class="shape-labels">
            <span v-for="ratio in ratios" :key="ratio.label + '-lbl'" class="shape-label">{{ ratio.name }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'

const avatarGroups = [
  { size: 70, items: ['A', 'B', 'C'] },
  { size: 50, items: ['A', 'B', 'C'] },
  { size: 40, items: ['A', 'B', 'C'] },
]

const shapes = [
  { label: 'S8', name: '8px', radius: '8px' },
  { label: 'S15', name: '15px', radius: '15px' },
  { label: 'S25', name: '25px', radius: '25px' },
  { label: 'S30', name: '30px', radius: '30px' },
  { label: 'S35', name: '35px', radius: '35px' },
  { label: 'CI', name: 'Circle', radius: '50%' },
]

const ratios = [
  { label: 'R1', name: '1:1', radius: '0' },
  { label: 'R2', name: '3:4', radius: '8px' },
  { label: 'R3', name: '2:3', radius: '15px' },
  { label: 'R4', name: '4:5', radius: '25px' },
  { label: 'R5', name: '16:9', radius: '35px' },
  { label: 'R6', name: 'Circle', radius: '50%' },
]
</script>

<style scoped>
.avatars-page {
  width: 100%;
}

.avatar-card {
  margin-bottom: 30px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #5A67F5;
}

.purple-avatar {
  background-color: #5A67F5;
  color: #fff;
  font-weight: 600;
  flex-shrink: 0;
}

.avatar-row {
  display: flex;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 15px;
}

/* Status Indicator */
.status-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.status-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  background-color: #4caf50;
  border-radius: 50%;
  border: 2px solid #fff;
  min-width: 6px;
  min-height: 6px;
}

/* Groups */
.groups-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.avatar-group-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.group-label {
  font-size: 13px;
  color: #909399;
  width: 40px;
  flex-shrink: 0;
}

.avatar-group {
  display: flex;
  align-items: center;
}

.group-avatar {
  border: 2px solid #fff;
}

/* Shape & Ratio labels */
.shape-avatar,
.ratio-avatar {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
}

.shape-labels {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 12px;
}

.shape-label {
  width: 100px;
  text-align: center;
  font-size: 12px;
  color: #909399;
}
</style>
