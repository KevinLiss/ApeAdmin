<template>
  <div>
    <PageHeader title="Users Cards" :breadcrumb="['APEUI库', 'Users', 'Users Cards']" />

    <el-row :gutter="16">
      <el-col v-for="user in users" :key="user.id" :span="8" style="margin-bottom: 16px">
        <el-card shadow="hover" body-style="text-align: center; padding: 24px">
          <el-avatar :size="80" :src="user.avatar" style="margin-bottom: 12px" />
          <h3 style="margin: 0 0 4px 0">{{ user.name }}</h3>
          <p style="color: #888; margin: 0 0 12px 0">{{ user.role }}</p>
          <div style="display: flex; justify-content: center; gap: 12px; margin-bottom: 16px">
            <el-link :underline="false" href="#" class="social-link">
              <el-icon :size="18"><Message /></el-icon>
            </el-link>
            <el-link :underline="false" href="#" class="social-link">
              <el-icon :size="18"><ChatDotRound /></el-icon>
            </el-link>
            <el-link :underline="false" href="#" class="social-link">
              <el-icon :size="18"><Share /></el-icon>
            </el-link>
          </div>
          <el-button type="primary" round @click="onFollow(user.name)">Follow</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { Message, ChatDotRound, Share } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

const avatarBase = 'https://cube.elemecdn.com/'

const users = [
  { id: 1, name: 'Alice Chen', role: 'Product Manager', avatar: avatarBase + '0/88/03b0d432e8c87b879d3e4e37b8f6jpeg.jpeg' },
  { id: 2, name: 'Bob Smith', role: 'Frontend Developer', avatar: avatarBase + '3/7c/3ea6be94a7beba6d1c0be4dd3f6fbcjpeg.jpeg' },
  { id: 3, name: 'Carol Johnson', role: 'UX Designer', avatar: avatarBase + '9/c2/3b0b0e6e6f6b3b1b3b1b3b1b3b1b3b1b.jpeg' },
  { id: 4, name: 'David Lee', role: 'Backend Developer', avatar: avatarBase + '1/34/19aa971b3b29b1f6c0e4dd3f6fbcjpeg.jpeg' },
  { id: 5, name: 'Emma Wilson', role: 'Data Analyst', avatar: avatarBase + 'a/3f/a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3.jpeg' },
  { id: 6, name: 'Frank Miller', role: 'DevOps Engineer', avatar: avatarBase + 'e/13/6734909d0f6c4e0b3b1b3b1b3b1b3b1b.jpeg' },
]

const onFollow = (name: string) => {
  ElMessage.success(`Followed ${name}`)
}
</script>

<style scoped>
:deep(.el-button--primary) {
  --el-color-primary: #5A67F5;
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}

.social-link .el-icon {
  color: #999;
  transition: color 0.2s;
}

.social-link:hover .el-icon {
  color: #5A67F5;
}
</style>
