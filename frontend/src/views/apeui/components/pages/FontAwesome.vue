<template>
  <div>
    <PageHeader title="Font Awesome Icons" :breadcrumb="['APEUI库', 'Components', 'Font Awesome']" />

    <el-card shadow="hover">
      <template #header>
        <span>Element Plus Icons — 点击复制名称</span>
      </template>
      <div class="icon-grid">
        <div
          v-for="item in icons"
          :key="item.name"
          class="icon-item"
          @click="copyName(item.name)"
        >
          <el-icon :size="28"><component :is="item.component" /></el-icon>
          <span class="icon-name">{{ item.name }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search, Edit, Delete, Plus, Minus, Close, Check, Loading, More, MoreFilled,
  Tools, Setting, House, User, View, Hide, Star, StarFilled, Collection,
  Folder, FolderOpened, Document, Files, Picture, Camera, VideoCamera,
  Monitor, Cellphone, Phone, Message, Bell, ChatRound, ChatLineRound, ChatDotRound,
  Promotion, Position, Location, LocationFilled, Compass, Connection, Aim, Filter,
  School,
} from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const icons: { name: string; component: Component }[] = [
  { name: 'Search', component: Search },
  { name: 'Edit', component: Edit },
  { name: 'Delete', component: Delete },
  { name: 'Plus', component: Plus },
  { name: 'Minus', component: Minus },
  { name: 'Close', component: Close },
  { name: 'Check', component: Check },
  { name: 'Loading', component: Loading },
  { name: 'More', component: More },
  { name: 'MoreFilled', component: MoreFilled },
  { name: 'Tools', component: Tools },
  { name: 'Setting', component: Setting },
  { name: 'House', component: House },
  { name: 'User', component: User },
  { name: 'View', component: View },
  { name: 'Hide', component: Hide },
  { name: 'Star', component: Star },
  { name: 'StarFilled', component: StarFilled },
  { name: 'Collection', component: Collection },
  { name: 'Folder', component: Folder },
  { name: 'FolderOpened', component: FolderOpened },
  { name: 'Document', component: Document },
  { name: 'Files', component: Files },
  { name: 'Picture', component: Picture },
  { name: 'Camera', component: Camera },
  { name: 'VideoCamera', component: VideoCamera },
  { name: 'Monitor', component: Monitor },
  { name: 'Cellphone', component: Cellphone },
  { name: 'Phone', component: Phone },
  { name: 'Message', component: Message },
  { name: 'Bell', component: Bell },
  { name: 'ChatRound', component: ChatRound },
  { name: 'ChatLineRound', component: ChatLineRound },
  { name: 'ChatDotRound', component: ChatDotRound },
  { name: 'Promotion', component: Promotion },
  { name: 'Position', component: Position },
  { name: 'Location', component: Location },
  { name: 'LocationFilled', component: LocationFilled },
  { name: 'Compass', component: Compass },
  { name: 'Connection', component: Connection },
  { name: 'Aim', component: Aim },
  { name: 'Filter', component: Filter },
  { name: 'School', component: School },
]

const copyName = (name: string) => {
  navigator.clipboard.writeText(name)
  ElMessage.success(`已复制: ${name}`)
}
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
  cursor: pointer;
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
