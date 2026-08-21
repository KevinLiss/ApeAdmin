<template>
  <div class="list-page">
    <PageHeader title="列表" :breadcrumb="['APEUI库', '组件示例', '列表']" />

    <el-row :gutter="30">
      <!-- 1. 默认列表 -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">默认列表</span>
          </template>
          <div>
            <div class="ape-list-item" v-for="(item, idx) in defaultList" :key="idx">
              {{ item }}
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 2. Links and Buttons -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">链接与按钮</span>
          </template>
          <div>
            <div
              class="ape-list-item link-item"
              :class="{ active: item.active, disabled: item.disabled }"
              v-for="(item, idx) in linkList"
              :key="idx"
            >
              {{ item.text }}
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 3. Flush Style -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover" :body-style="{ padding: 0 }">
          <template #header>
            <span class="card-title">紧凑样式</span>
          </template>
          <div>
            <div class="ape-list-item" v-for="(item, idx) in flushList" :key="idx">
              {{ item }}
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 4. Contextual Classes -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover" :body-style="{ padding: 0 }">
          <template #header>
            <span class="card-title">上下文样式</span>
          </template>
          <div>
            <div
              class="ape-list-item"
              :class="`ctx-${item.ctx}`"
              v-for="(item, idx) in contextualList"
              :key="idx"
            >
              {{ item.text }}
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 5. With Badges -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">带徽章</span>
          </template>
          <div>
            <div class="ape-list-item badge-item" v-for="(item, idx) in badgeList" :key="idx">
              <span class="badge-label">{{ item.text }}</span>
              <el-badge :value="item.badge" :type="item.type" class="list-badge" />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 6. Custom Content -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">自定义内容</span>
          </template>
          <div>
            <div class="ape-list-item custom-content-item" v-for="(item, idx) in customContentList" :key="idx">
              <div class="custom-content-header">
                <span class="custom-content-title">{{ item.title }}</span>
                <el-tag size="small" type="warning" effect="light">{{ item.subtitle }}</el-tag>
                <span class="custom-content-time">{{ item.time }}</span>
              </div>
              <p class="custom-content-desc">{{ item.desc }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 7. JavaScript Behavior -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">JavaScript 行为</span>
          </template>
          <el-tabs v-model="jsTab" tab-position="left" class="js-tabs">
            <el-tab-pane label="首页" name="home">
              <h4 class="js-tab-heading">首页</h4>
              <p class="lorem">欢迎来到首页标签页！这里是仪表盘概览，可以一目了然地查看关键指标和近期动态。这是用于演示的占位文本，展示段落内容的排版效果。</p>
              <p class="lorem">第二段占位文本，用于演示多段落内容在标签页中的展示效果，帮助开发者了解组件在不同内容长度下的渲染表现。</p>
            </el-tab-pane>
            <el-tab-pane label="个人资料" name="profile">
              <h4 class="js-tab-heading">个人资料</h4>
              <p class="lorem">您的个人资料设置在此管理。可以更新个人信息、更换头像以及配置隐私偏好。这是用于演示的占位文本内容。</p>
              <p class="lorem">第二段占位文本，展示较长的描述性内容在标签页中的排版效果，帮助您了解组件对多段落内容的适配能力。</p>
            </el-tab-pane>
            <el-tab-pane label="消息" name="messages">
              <h4 class="js-tab-heading">消息</h4>
              <p class="lorem">所有对话集中在此。查看、回复并管理与团队成员和客户的消息线程。这是用于演示的占位文本内容。</p>
              <p class="lorem">第二段占位文本，展示较长内容的排版效果，帮助开发者了解组件在不同内容长度下的渲染表现。</p>
            </el-tab-pane>
            <el-tab-pane label="设置" name="settings">
              <h4 class="js-tab-heading">设置</h4>
              <p class="lorem">在此配置系统级设置，包括安全策略、通知偏好和集成选项。这是用于演示的占位文本内容。</p>
              <p class="lorem">第二段占位文本，展示较长内容的排版效果，帮助您了解组件对多段落内容的适配能力。</p>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 8. With Icon -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">带图标</span>
          </template>
          <div>
            <div class="ape-list-item icon-list-item" v-for="(item, idx) in iconList" :key="idx">
              <el-icon :size="18" color="#5A67F5"><component :is="item.icon" /></el-icon>
              <span class="icon-list-text">{{ item.text }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 9. With Images -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">带方形头像</span>
          </template>
          <div>
            <div class="ape-list-item avatar-list-item" v-for="(item, idx) in imageList" :key="idx">
              <el-avatar :size="44" shape="square" :style="{ background: item.color, borderRadius: '10px' }">{{ item.initials }}</el-avatar>
              <div class="avatar-list-body">
                <span class="avatar-list-name">{{ item.name }}</span>
                <span class="avatar-list-desc">{{ item.desc }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 10. With Image Rounded -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">带圆形头像</span>
          </template>
          <div>
            <div class="ape-list-item avatar-list-item" v-for="(item, idx) in roundedImageList" :key="idx">
              <el-avatar :size="44" :style="{ background: item.color }">{{ item.initials }}</el-avatar>
              <div class="avatar-list-body">
                <span class="avatar-list-name">{{ item.name }}</span>
                <span class="avatar-list-desc">{{ item.desc }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { HomeFilled, Star, Message, Setting } from '@element-plus/icons-vue'
import type { Component } from 'vue'
import PageHeader from '../PageHeader.vue'

// 1. 默认列表
const defaultList = [
  '第一条列表项',
  '第二条列表项',
  '第三条列表项',
  '第四条列表项',
  '第五条列表项',
]

// 2. Links and Buttons
const linkList = [
  { text: '当前激活的链接项', active: true, disabled: false },
  { text: '第二个链接项', active: false, disabled: false },
  { text: '第三个链接项', active: false, disabled: false },
  { text: '第四个链接项', active: false, disabled: false },
  { text: '禁用的链接项', active: false, disabled: true },
]

// 3. Flush Style
const flushList = [
  '第一条列表项',
  '第二条列表项',
  '第三条列表项',
  '第四条列表项',
  '第五条列表项',
  '第六条列表项',
  '第七条列表项',
  '第八条列表项',
  '第九条列表项',
]

// 4. Contextual Classes
type CtxType = 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light' | 'dark' | 'brand'
const contextualList: { text: string; ctx: CtxType }[] = [
  { text: '主要样式的列表项', ctx: 'primary' },
  { text: '次要样式的列表项', ctx: 'secondary' },
  { text: '成功样式的列表项', ctx: 'success' },
  { text: '危险样式的列表项', ctx: 'danger' },
  { text: '警告样式的列表项', ctx: 'warning' },
  { text: '信息样式的列表项', ctx: 'info' },
  { text: '浅色样式的列表项', ctx: 'light' },
  { text: '深色样式的列表项', ctx: 'dark' },
  { text: '品牌色样式的列表项', ctx: 'brand' },
]

// 5. With Badges
type BadgeType = 'primary' | 'success' | 'warning' | 'info' | 'danger'
const badgeList: { text: string; badge: string | number; type: BadgeType }[] = [
  { text: '收件箱消息', badge: 14, type: 'primary' },
  { text: '草稿邮件', badge: 2, type: 'success' },
  { text: '已发送', badge: 1, type: 'warning' },
  { text: '已用存储', badge: '100%', type: 'info' },
  { text: '待办任务', badge: 2, type: 'danger' },
  { text: '促销优惠', badge: '特惠', type: 'primary' },
  { text: '未读通知', badge: 14, type: 'danger' },
]

// 6. Custom Content
const customContentList = [
  {
    title: '列表项标题',
    subtitle: '推荐',
    time: '3天前',
    desc: '这是一段用于演示的占位内容，展示列表项在带有详细描述时的排版效果，帮助您了解组件对丰富内容的适配能力。',
  },
  {
    title: '第二个列表项标题',
    subtitle: '新增',
    time: '5天前',
    desc: '另一段占位内容，用于演示列表项在较长描述文本下的渲染效果，展示组件对多行内容的支持。',
  },
  {
    title: '第三个列表项标题',
    subtitle: '已更新',
    time: '1周前',
    desc: '最后一段占位内容，用于展示多个列表项纵向排列时丰富内容的效果，帮助您全面了解组件的展示能力。',
  },
]

// 7. JavaScript Behavior
const jsTab = ref('home')

// 8. With Icon
const iconList: { text: string; icon: Component }[] = [
  { text: '首页看板', icon: HomeFilled },
  { text: '收藏项', icon: Star },
  { text: '消息中心', icon: Message },
  { text: '系统设置', icon: Setting },
]

// 9. With Images (square rounded)
const imageList = [
  { name: '艾丽斯·安德森', desc: '项目经理', initials: '艾', color: '#5A67F5' },
  { name: '鲍勃·布朗', desc: '首席开发', initials: '鲍', color: '#67C100' },
  { name: '查理·克拉克', desc: 'UI设计师', initials: '查', color: '#E56809' },
  { name: '戴安娜·戴维斯', desc: '测试工程师', initials: '戴', color: '#3EBCB9' },
]

// 10. With Image Rounded
const roundedImageList = [
  { name: '伊万·埃文斯', desc: '运维工程师', initials: '伊', color: '#7F8AF8' },
  { name: '菲奥娜·福斯特', desc: '产品负责人', initials: '菲', color: '#DC0808' },
  { name: '乔治·格林', desc: '后端开发', initials: '乔', color: '#E56809' },
  { name: '汉娜·希尔', desc: '数据分析师', initials: '汉', color: '#5A67F5' },
]
</script>

<style scoped>
.card-title {
  font-weight: 600;
  color: #5A67F5;
}

.ape-col {
  margin-bottom: 30px;
}

/* Base list item */
.ape-list-item {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(90, 103, 245, 0.08);
  color: #5a6273;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.ape-list-item:last-child {
  border-bottom: none;
}

/* Active state */
.ape-list-item.active {
  background-color: rgba(90, 103, 245, 0.08);
  color: #5A67F5;
  font-weight: 500;
  cursor: pointer;
}

/* Disabled state */
.ape-list-item.disabled {
  color: #c0c4cc;
  cursor: not-allowed;
  pointer-events: none;
  background-color: #f9f9fb;
}

/* Links and Buttons */
.link-item {
  cursor: pointer;
}

.link-item:not(.active):not(.disabled):hover {
  background-color: rgba(90, 103, 245, 0.04);
  color: #5A67F5;
}

/* Contextual Classes */
.ctx-primary {
  background-color: rgba(90, 103, 245, 0.1);
  color: #5A67F5;
}

.ctx-secondary {
  background-color: rgba(108, 117, 125, 0.1);
  color: #6c757d;
}

.ctx-success {
  background-color: rgba(103, 193, 0, 0.1);
  color: #529c00;
}

.ctx-danger {
  background-color: rgba(220, 8, 8, 0.1);
  color: #DC0808;
}

.ctx-warning {
  background-color: rgba(229, 104, 9, 0.1);
  color: #E56809;
}

.ctx-info {
  background-color: rgba(62, 188, 185, 0.1);
  color: #2da8a5;
}

.ctx-light {
  background-color: #f8f9fa;
  color: #1f2329;
  border-bottom-color: rgba(0, 0, 0, 0.05);
}

.ctx-dark {
  background-color: #343a40;
  color: #ffffff;
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.ctx-brand {
  background-color: rgba(123, 111, 168, 0.1);
  color: #7F8AF8;
}

/* With Badges */
.badge-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.badge-label {
  flex: 1;
}

.badge-item :deep(.el-badge__content) {
  position: static;
  top: auto;
  right: auto;
  transform: none;
}

/* Custom Content */
.custom-content-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px;
}

.custom-content-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.custom-content-title {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
}

.custom-content-time {
  margin-left: auto;
  color: #909399;
  font-size: 13px;
  white-space: nowrap;
}

.custom-content-desc {
  margin: 0;
  color: #5a6273;
  font-size: 13px;
  line-height: 1.6;
}

/* JavaScript Behavior - vertical tabs */
.js-tabs {
  min-height: 220px;
}

.js-tabs :deep(.el-tabs__content) {
  padding: 8px 0 8px 20px;
  overflow: hidden;
}

.js-tab-heading {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 600;
  color: #5A67F5;
}

.lorem {
  margin: 0 0 10px;
  color: #5a6273;
  line-height: 1.7;
  font-size: 14px;
}

.lorem:last-child {
  margin-bottom: 0;
}

/* With Icon */
.icon-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-list-text {
  color: #5a6273;
}

/* With Images / With Image Rounded */
.avatar-list-item {
  display: flex;
  align-items: center;
  gap: 14px;
}

.avatar-list-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.avatar-list-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.avatar-list-desc {
  font-size: 13px;
  color: #909399;
}
</style>
