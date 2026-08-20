<template>
  <div>
    <PageHeader title="Breadcrumb" :breadcrumb="['APEUI库', 'Components', 'Breadcrumb']" />

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="基础面包屑">
          <el-breadcrumb :separator-icon="ArrowRight" style="font-size: 14px">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>系统管理</el-breadcrumb-item>
            <el-breadcrumb-item>用户列表</el-breadcrumb-item>
          </el-breadcrumb>
          <el-divider />
          <el-breadcrumb separator="/" style="font-size: 14px">
            <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
            <el-breadcrumb-item>Components</el-breadcrumb-item>
            <el-breadcrumb-item>Breadcrumb</el-breadcrumb-item>
          </el-breadcrumb>
          <el-divider />
          <el-breadcrumb separator=">" style="font-size: 14px">
            <el-breadcrumb-item>Level 1</el-breadcrumb-item>
            <el-breadcrumb-item>Level 2</el-breadcrumb-item>
            <el-breadcrumb-item>Level 3</el-breadcrumb-item>
          </el-breadcrumb>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="带图标">
          <el-breadcrumb :separator-icon="ArrowRight">
            <el-breadcrumb-item :to="{ path: '/' }">
              <el-icon><HomeFilled /></el-icon>
              <span> 首页</span>
            </el-breadcrumb-item>
            <el-breadcrumb-item>
              <el-icon><Setting /></el-icon>
              <span> 系统管理</span>
            </el-breadcrumb-item>
            <el-breadcrumb-item>
              <el-icon><User /></el-icon>
              <span> 用户管理</span>
            </el-breadcrumb-item>
          </el-breadcrumb>
          <el-divider />
          <el-breadcrumb separator="|">
            <el-breadcrumb-item :to="{ path: '/' }">
              <el-icon color="#534686"><Monitor /></el-icon>
              <span> Dashboard</span>
            </el-breadcrumb-item>
            <el-breadcrumb-item>
              <el-icon color="#534686"><Document /></el-icon>
              <span> 文档</span>
            </el-breadcrumb-item>
            <el-breadcrumb-item>
              <el-icon color="#534686"><EditPen /></el-icon>
              <span> 编辑</span>
            </el-breadcrumb-item>
          </el-breadcrumb>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" header="不同分隔符" style="margin-bottom: 16px">
      <div class="breadcrumb-list">
        <div class="breadcrumb-row" v-for="item in separators" :key="item.label">
          <span class="sep-label">{{ item.label }}</span>
          <el-breadcrumb :separator="item.sep">
            <el-breadcrumb-item>首页</el-breadcrumb-item>
            <el-breadcrumb-item>分类</el-breadcrumb-item>
            <el-breadcrumb-item>详情</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover" header="紫色主题面包屑">
      <el-breadcrumb :separator-icon="ArrowRight" class="purple-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">
          <el-icon><HomeFilled /></el-icon>
          <span>ApeAdmin</span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>
          <el-icon><Grid /></el-icon>
          <span>APEUI 库</span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>
          <el-icon><Document /></el-icon>
          <span>Components</span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>
          <el-icon><MoreFilled /></el-icon>
          <span>Breadcrumb</span>
        </el-breadcrumb-item>
      </el-breadcrumb>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ArrowRight, HomeFilled, Setting, User, Monitor, Document, EditPen, Grid, MoreFilled } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const separators = [
  { label: 'separator="/"', sep: '/' },
  { label: 'separator="-"', sep: '-' },
  { label: 'separator=">"', sep: '>' },
  { label: 'separator="·"', sep: '·' },
  { label: 'separator="|"', sep: '|' },
]
</script>

<style scoped>
.breadcrumb-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.breadcrumb-row {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f5;
}
.breadcrumb-row:last-child {
  border-bottom: none;
}
.sep-label {
  width: 130px;
  color: #909399;
  font-size: 13px;
  font-family: monospace;
  white-space: nowrap;
}
.purple-breadcrumb :deep(.el-breadcrumb__item) {
  font-size: 15px;
}
.purple-breadcrumb :deep(.el-breadcrumb__item .el-icon) {
  margin-right: 4px;
}
.purple-breadcrumb :deep(.el-breadcrumb__inner) {
  color: #534686;
  font-weight: 500;
}
.purple-breadcrumb :deep(.el-breadcrumb__inner a) {
  color: #7b6fa8;
  font-weight: 500;
}
.purple-breadcrumb :deep(.el-breadcrumb__inner a:hover) {
  color: #534686;
}
.purple-breadcrumb :deep(.el-breadcrumb__separator) {
  color: #c0b8d8;
}
</style>
