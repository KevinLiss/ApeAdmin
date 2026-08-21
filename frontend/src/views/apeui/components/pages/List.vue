<template>
  <div class="list-page">
    <PageHeader title="Lists" :breadcrumb="['APEUI库', 'Components', 'Lists']" />

    <el-row :gutter="30">
      <!-- 1. Default List -->
      <el-col :span="12" class="koho-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Default List</span>
          </template>
          <div>
            <div class="koho-list-item" v-for="(item, idx) in defaultList" :key="idx">
              {{ item }}
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 2. Links and Buttons -->
      <el-col :span="12" class="koho-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Links and Buttons</span>
          </template>
          <div>
            <div
              class="koho-list-item link-item"
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
      <el-col :span="12" class="koho-col">
        <el-card shadow="hover" :body-style="{ padding: 0 }">
          <template #header>
            <span class="card-title">Flush Style</span>
          </template>
          <div>
            <div class="koho-list-item" v-for="(item, idx) in flushList" :key="idx">
              {{ item }}
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 4. Contextual Classes -->
      <el-col :span="12" class="koho-col">
        <el-card shadow="hover" :body-style="{ padding: 0 }">
          <template #header>
            <span class="card-title">Contextual Classes</span>
          </template>
          <div>
            <div
              class="koho-list-item"
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
      <el-col :span="12" class="koho-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">With Badges</span>
          </template>
          <div>
            <div class="koho-list-item badge-item" v-for="(item, idx) in badgeList" :key="idx">
              <span class="badge-label">{{ item.text }}</span>
              <el-badge :value="item.badge" :type="item.type" class="list-badge" />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 6. Custom Content -->
      <el-col :span="12" class="koho-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Custom Content</span>
          </template>
          <div>
            <div class="koho-list-item custom-content-item" v-for="(item, idx) in customContentList" :key="idx">
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
      <el-col :span="12" class="koho-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">JavaScript Behavior</span>
          </template>
          <el-tabs v-model="jsTab" tab-position="left" class="js-tabs">
            <el-tab-pane label="Home" name="home">
              <h4 class="js-tab-heading">Home</h4>
              <p class="lorem">Welcome to the home tab! This is where your dashboard overview lives, showing key metrics and recent activity at a glance. Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
              <p class="lorem">Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
            </el-tab-pane>
            <el-tab-pane label="Profile" name="profile">
              <h4 class="js-tab-heading">Profile</h4>
              <p class="lorem">Your profile settings are managed here. Update your personal information, change your avatar, and configure privacy preferences. Duis aute irure dolor in reprehenderit.</p>
              <p class="lorem">In voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt.</p>
            </el-tab-pane>
            <el-tab-pane label="Messages" name="messages">
              <h4 class="js-tab-heading">Messages</h4>
              <p class="lorem">All your conversations in one place. View, reply, and manage your message threads with team members and clients. Nemo enim ipsam voluptatem quia voluptas.</p>
              <p class="lorem">Sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt neque porro quisquam est.</p>
            </el-tab-pane>
            <el-tab-pane label="Settings" name="settings">
              <h4 class="js-tab-heading">Settings</h4>
              <p class="lorem">Configure system-wide settings including security policies, notification preferences, and integration options. At vero eos et accusamus et iusto odio dignissimos.</p>
              <p class="lorem">Ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.</p>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 8. With Icon -->
      <el-col :span="12" class="koho-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">With Icon</span>
          </template>
          <div>
            <div class="koho-list-item icon-list-item" v-for="(item, idx) in iconList" :key="idx">
              <el-icon :size="18" color="#534686"><component :is="item.icon" /></el-icon>
              <span class="icon-list-text">{{ item.text }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 9. With Images -->
      <el-col :span="12" class="koho-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">With Images</span>
          </template>
          <div>
            <div class="koho-list-item avatar-list-item" v-for="(item, idx) in imageList" :key="idx">
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
      <el-col :span="12" class="koho-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">With Image Rounded</span>
          </template>
          <div>
            <div class="koho-list-item avatar-list-item" v-for="(item, idx) in roundedImageList" :key="idx">
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

// 1. Default List
const defaultList = [
  'Cras justo odio',
  'Dapibus ac facilisis in',
  'Morbi leo risus',
  'Porta ac consectetur ac',
  'Vestibulum at eros',
]

// 2. Links and Buttons
const linkList = [
  { text: 'The current active link item', active: true, disabled: false },
  { text: 'A second link item', active: false, disabled: false },
  { text: 'A third link item', active: false, disabled: false },
  { text: 'A fourth link item', active: false, disabled: false },
  { text: 'A disabled link item', active: false, disabled: true },
]

// 3. Flush Style
const flushList = [
  'Cras justo odio',
  'Dapibus ac facilisis in',
  'Morbi leo risus',
  'Porta ac consectetur ac',
  'Vestibulum at eros',
  'Cras justo odio',
  'Dapibus ac facilisis in',
  'Morbi leo risus',
  'Porta ac consectetur ac',
]

// 4. Contextual Classes
type CtxType = 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light' | 'dark' | 'brand'
const contextualList: { text: string; ctx: CtxType }[] = [
  { text: 'A simple primary list item', ctx: 'primary' },
  { text: 'A simple secondary list item', ctx: 'secondary' },
  { text: 'A simple success list item', ctx: 'success' },
  { text: 'A simple danger list item', ctx: 'danger' },
  { text: 'A simple warning list item', ctx: 'warning' },
  { text: 'A simple info list item', ctx: 'info' },
  { text: 'A simple light list item', ctx: 'light' },
  { text: 'A simple dark list item', ctx: 'dark' },
  { text: 'A simple brand list item', ctx: 'brand' },
]

// 5. With Badges
type BadgeType = 'primary' | 'success' | 'warning' | 'info' | 'danger'
const badgeList: { text: string; badge: string | number; type: BadgeType }[] = [
  { text: 'Inbox messages', badge: 14, type: 'primary' },
  { text: 'Draft emails', badge: 2, type: 'success' },
  { text: 'Sent items', badge: 1, type: 'warning' },
  { text: 'Storage used', badge: '100%', type: 'info' },
  { text: 'Pending tasks', badge: 2, type: 'danger' },
  { text: 'Promotional offer', badge: 'sale', type: 'primary' },
  { text: 'Unread notifications', badge: 14, type: 'danger' },
]

// 6. Custom Content
const customContentList = [
  {
    title: 'List item heading',
    subtitle: 'Featured',
    time: '3 days ago',
    desc: 'Some placeholder content in a paragraph that goes a little deeper for discussion and provides more detail about the topic at hand.',
  },
  {
    title: 'A second list item heading',
    subtitle: 'New',
    time: '5 days ago',
    desc: 'Another piece of placeholder content. This text is here to demonstrate how the list item will render with longer descriptive content.',
  },
  {
    title: 'A third list item heading',
    subtitle: 'Updated',
    time: '1 week ago',
    desc: 'A final piece of placeholder content to round out the demonstration. This shows how multiple list items stack vertically with rich content.',
  },
]

// 7. JavaScript Behavior
const jsTab = ref('home')

// 8. With Icon
const iconList: { text: string; icon: Component }[] = [
  { text: 'Home dashboard', icon: HomeFilled },
  { text: 'Favorite items', icon: Star },
  { text: 'Message center', icon: Message },
  { text: 'System settings', icon: Setting },
]

// 9. With Images (square rounded)
const imageList = [
  { name: 'Alice Anderson', desc: 'Project Manager', initials: 'AA', color: '#534686' },
  { name: 'Bob Brown', desc: 'Lead Developer', initials: 'BB', color: '#67C100' },
  { name: 'Charlie Clark', desc: 'UI Designer', initials: 'CC', color: '#E56809' },
  { name: 'Diana Davis', desc: 'QA Engineer', initials: 'DD', color: '#3EBCB9' },
]

// 10. With Image Rounded
const roundedImageList = [
  { name: 'Evan Evans', desc: 'DevOps Engineer', initials: 'EE', color: '#7b6fa8' },
  { name: 'Fiona Foster', desc: 'Product Owner', initials: 'FF', color: '#DC0808' },
  { name: 'George Green', desc: 'Backend Developer', initials: 'GG', color: '#E56809' },
  { name: 'Hannah Hill', desc: 'Data Analyst', initials: 'HH', color: '#534686' },
]
</script>

<style scoped>
.card-title {
  font-weight: 600;
  color: #534686;
}

.koho-col {
  margin-bottom: 30px;
}

/* Base list item */
.koho-list-item {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(83, 70, 134, 0.08);
  color: #5a6273;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.koho-list-item:last-child {
  border-bottom: none;
}

/* Active state */
.koho-list-item.active {
  background-color: rgba(83, 70, 134, 0.08);
  color: #534686;
  font-weight: 500;
  cursor: pointer;
}

/* Disabled state */
.koho-list-item.disabled {
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
  background-color: rgba(83, 70, 134, 0.04);
  color: #534686;
}

/* Contextual Classes */
.ctx-primary {
  background-color: rgba(83, 70, 134, 0.1);
  color: #534686;
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
  color: #7b6fa8;
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
  color: #534686;
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
