<template>
  <div class="social-app">
    <PageHeader title="Social App" :breadcrumb="['APEUI库', 'Applications', 'Social App']" />

    <el-row :gutter="30">
      <!-- Left: Friends List -->
      <el-col :xs="24" :md="6">
        <div class="koho-card">
          <div class="card-title">
            <el-icon><User /></el-icon>
            <span>Friends</span>
          </div>
          <div class="friend-list">
            <div v-for="friend in friends" :key="friend.id" class="friend-item">
              <div class="friend-avatar-wrap">
                <el-avatar :size="42" :src="friend.avatar" />
                <span class="status-dot" :class="friend.status"></span>
              </div>
              <div class="friend-info">
                <div class="friend-name">{{ friend.name }}</div>
                <div class="friend-status">{{ friend.status === 'online' ? 'Online' : friend.status === 'away' ? 'Away' : 'Offline' }}</div>
              </div>
              <el-button text circle :icon="ChatDotRound" size="small" @click="onMessage(friend.name)" />
            </div>
          </div>
        </div>
      </el-col>

      <!-- Center: Feed -->
      <el-col :xs="24" :md="12">
        <!-- Post Box -->
        <div class="koho-card">
          <div class="post-box">
            <el-avatar :size="40" :src="currentUser.avatar" />
            <el-input
              v-model="postText"
              type="textarea"
              :rows="2"
              placeholder="What's on your mind?"
              resize="none"
              class="post-input"
            />
          </div>
          <div class="post-actions">
            <el-button text :icon="Picture" @click="onAddImage">Photo</el-button>
            <el-button text :icon="VideoCamera" @click="onAddVideo">Video</el-button>
            <el-button text :icon="Location" @click="onCheckIn">Check-in</el-button>
            <el-button type="primary" :icon="Promotion" @click="onPublish" class="publish-btn">Publish</el-button>
          </div>
        </div>

        <!-- Feed Items -->
        <div v-for="post in posts" :key="post.id" class="koho-card">
          <div class="post-header">
            <el-avatar :size="44" :src="post.avatar" />
            <div class="post-meta">
              <div class="post-author">{{ post.name }}</div>
              <div class="post-time">{{ post.time }} · Public</div>
            </div>
            <el-dropdown trigger="click">
              <el-button text :icon="MoreFilled" circle />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>Save Post</el-dropdown-item>
                  <el-dropdown-item>Copy Link</el-dropdown-item>
                  <el-dropdown-item divided>Report</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="post-content">{{ post.content }}</div>
          <div v-if="post.image" class="post-image">
            <img :src="post.image" alt="" />
          </div>
          <div class="post-stats">
            <span><el-icon><Star /></el-icon> {{ post.likes }}</span>
            <span><el-icon><ChatDotRound /></el-icon> {{ post.comments }} Comments</span>
            <span><el-icon><Share /></el-icon> {{ post.shares }} Shares</span>
          </div>
          <div class="post-buttons">
            <el-button text :icon="Star" @click="onLike(post)">Like ({{ post.likes }})</el-button>
            <el-button text :icon="ChatDotRound" @click="onComment(post)">Comment</el-button>
            <el-button text :icon="Share" @click="onShare(post)">Share</el-button>
          </div>
        </div>
      </el-col>

      <!-- Right: Suggestions & Topics -->
      <el-col :xs="24" :md="6">
        <!-- People You May Know -->
        <div class="koho-card">
          <div class="card-title">
            <el-icon><UserFilled /></el-icon>
            <span>People You May Know</span>
          </div>
          <div class="suggest-list">
            <div v-for="person in suggestions" :key="person.id" class="suggest-item">
              <el-avatar :size="40" :src="person.avatar" />
              <div class="suggest-info">
                <div class="suggest-name">{{ person.name }}</div>
                <div class="suggest-mutual">{{ person.mutual }} mutual friends</div>
              </div>
              <el-button size="small" type="primary" round @click="onFollow(person.name)">Follow</el-button>
            </div>
          </div>
        </div>

        <!-- Trending Topics -->
        <div class="koho-card">
          <div class="card-title">
            <el-icon><TrendCharts /></el-icon>
            <span>Trending Topics</span>
          </div>
          <div class="tag-cloud">
            <el-tag
              v-for="topic in topics"
              :key="topic.name"
              :type="topic.type"
              :size="topic.size"
              class="topic-tag"
              @click="onTopicClick(topic.name)"
            >
              #{{ topic.name }}
            </el-tag>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User, UserFilled, ChatDotRound, MoreFilled, Picture, VideoCamera,
  Promotion, Star, Share, TrendCharts, Location,
} from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

const avatarBase = 'https://cube.elemecdn.com/'

const currentUser = ref({
  name: 'William',
  avatar: avatarBase + '0/88/03b0d432e8c87b879d3e4e37b8f6f6jpeg.jpeg',
})

const postText = ref('')

const friends = ref([
  { id: 1, name: 'Alice Chen', avatar: avatarBase + '3/7c/3ea6be94a7beba6d1c0be4dd3f6fbcjpeg.jpeg', status: 'online' },
  { id: 2, name: 'Bob Smith', avatar: avatarBase + '1/34/19aa971b3b29b1f6c0e4dd3f6fbcjpeg.jpeg', status: 'online' },
  { id: 3, name: 'Carol Johnson', avatar: avatarBase + '9/c2/3b0b0e6e6f6b3b1b3b1b3b1b3b1b3b1b.jpeg', status: 'away' },
  { id: 4, name: 'David Lee', avatar: avatarBase + 'a/3f/a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3.jpeg', status: 'offline' },
  { id: 5, name: 'Emma Wilson', avatar: avatarBase + 'e/13/6734909d0f6c4e0b3b1b3b1b3b1b3b1b.jpeg', status: 'online' },
  { id: 6, name: 'Frank Miller', avatar: avatarBase + '0/88/03b0d432e8c87b879d3e4e37b8f6f6jpeg.jpeg', status: 'away' },
])

const posts = ref([
  {
    id: 1, name: 'Alice Chen', avatar: avatarBase + '3/7c/3ea6be94a7beba6d1c0be4dd3f6fbcjpeg.jpeg',
    time: '2 hours ago', content: 'Just launched our new product design! So excited to share this with everyone. The team has been working incredibly hard over the past few months.',
    image: avatarBase + '0/88/03b0d432e8c87b879d3e4e37b8f6f6jpeg.jpeg',
    likes: 42, comments: 12, shares: 5,
  },
  {
    id: 2, name: 'Bob Smith', avatar: avatarBase + '1/34/19aa971b3b29b1f6c0e4dd3f6fbcjpeg.jpeg',
    time: '5 hours ago', content: 'Amazing conference today! Learned so much about the latest trends in AI and machine learning. Looking forward to applying these insights.',
    image: '', likes: 28, comments: 8, shares: 3,
  },
  {
    id: 3, name: 'Carol Johnson', avatar: avatarBase + '9/c2/3b0b0e6e6f6b3b1b3b1b3b1b3b1b3b1b.jpeg',
    time: 'Yesterday', content: 'Beautiful sunset at the beach today. Sometimes you need to step away from the screen and enjoy nature.',
    image: avatarBase + 'a/3f/a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3.jpeg',
    likes: 156, comments: 24, shares: 18,
  },
  {
    id: 4, name: 'David Lee', avatar: avatarBase + 'a/3f/a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3.jpeg',
    time: '2 days ago', content: 'Just finished reading "Clean Code" by Robert C. Martin. Highly recommend it to every developer. The principles are timeless.',
    image: '', likes: 35, comments: 15, shares: 10,
  },
  {
    id: 5, name: 'Emma Wilson', avatar: avatarBase + 'e/13/6734909d0f6c4e0b3b1b3b1b3b1b3b1b.jpeg',
    time: '3 days ago', content: 'Team dinner was a blast! Great food, great company. These moments remind me why I love working with this team.',
    image: avatarBase + '0/88/03b0d432e8c87b879d3e4e37b8f6f6jpeg.jpeg',
    likes: 89, comments: 20, shares: 7,
  },
])

const suggestions = ref([
  { id: 1, name: 'Grace Park', avatar: avatarBase + '3/7c/3ea6be94a7beba6d1c0be4dd3f6fbcjpeg.jpeg', mutual: 5 },
  { id: 2, name: 'Henry Brown', avatar: avatarBase + '1/34/19aa971b3b29b1f6c0e4dd3f6fbcjpeg.jpeg', mutual: 3 },
  { id: 3, name: 'Ivy Davis', avatar: avatarBase + '9/c2/3b0b0e6e6f6b3b1b3b1b3b1b3b1b3b1b.jpeg', mutual: 8 },
])

const topics = ref([
  { name: 'AI', type: 'primary' as const, size: 'large' as const },
  { name: 'Vue3', type: 'success' as const, size: 'default' as const },
  { name: 'Design', type: 'info' as const, size: 'large' as const },
  { name: 'Startup', type: 'warning' as const, size: 'default' as const },
  { name: 'Remote Work', type: 'danger' as const, size: 'default' as const },
  { name: 'WebDev', type: 'primary' as const, size: 'large' as const },
  { name: 'Coffee', type: 'info' as const, size: 'small' as const },
  { name: 'Travel', type: 'success' as const, size: 'default' as const },
  { name: 'Photography', type: 'warning' as const, size: 'default' as const },
])

const onPublish = () => {
  if (!postText.value.trim()) {
    ElMessage.warning('Please write something first')
    return
  }
  ElMessage.success('Posted successfully!')
  postText.value = ''
}
const onAddImage = () => ElMessage.info('Image picker opened')
const onAddVideo = () => ElMessage.info('Video picker opened')
const onCheckIn = () => ElMessage.info('Check-in opened')
const onLike = (post: any) => { post.likes++; ElMessage.success(`Liked ${post.name}'s post`) }
const onComment = (post: any) => ElMessage.info(`Commenting on ${post.name}'s post`)
const onShare = (post: any) => ElMessage.success(`Shared ${post.name}'s post`)
const onMessage = (name: string) => ElMessage.info(`Messaging ${name}`)
const onFollow = (name: string) => ElMessage.success(`Followed ${name}`)
const onTopicClick = (topic: string) => ElMessage.info(`Browsing #${topic}`)
</script>

<style scoped>
.koho-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 0 20px rgba(8, 21, 66, 0.05);
  margin-bottom: 30px;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 500;
  color: #534686;
  margin-bottom: 16px;
}
.card-title .el-icon { font-size: 20px; }

/* Friend List */
.friend-list { display: flex; flex-direction: column; gap: 4px; }
.friend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}
.friend-item:hover { background: rgba(83, 70, 134, 0.08); }
.friend-avatar-wrap { position: relative; }
.status-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid #fff;
}
.status-dot.online { background: #67C100; }
.status-dot.away { background: #E56809; }
.status-dot.offline { background: #ccc; }
.friend-info { flex: 1; }
.friend-name { font-size: 14px; font-weight: 500; color: #2b2b2b; }
.friend-status { font-size: 12px; color: #909399; }

/* Post Box */
.post-box {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.post-input { flex: 1; }
:deep(.post-input .el-textarea__inner) {
  border: none;
  background: transparent;
  box-shadow: none;
  padding: 8px 0;
  font-size: 15px;
}
.post-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 12px;
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}
.publish-btn { margin-left: auto; }

/* Feed Items */
.post-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.post-meta { flex: 1; }
.post-author { font-size: 15px; font-weight: 600; color: #2b2b2b; }
.post-time { font-size: 12px; color: #909399; }
.post-content {
  font-size: 14px;
  line-height: 1.6;
  color: #2b2b2b;
  margin-bottom: 12px;
}
.post-image {
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 12px;
}
.post-image img { width: 100%; display: block; }
.post-stats {
  display: flex;
  gap: 20px;
  padding: 8px 0;
  font-size: 13px;
  color: #909399;
  border-bottom: 1px solid #f0f0f0;
}
.post-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}
.post-buttons {
  display: flex;
  gap: 4px;
  padding-top: 4px;
}
.post-buttons .el-button { flex: 1; }

/* Suggestions */
.suggest-list { display: flex; flex-direction: column; gap: 12px; }
.suggest-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.suggest-info { flex: 1; }
.suggest-name { font-size: 14px; font-weight: 500; color: #2b2b2b; }
.suggest-mutual { font-size: 12px; color: #909399; }

/* Tag Cloud */
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.topic-tag { cursor: pointer; }

:deep(.el-button--primary) {
  --el-color-primary: #534686;
  --el-button-bg-color: #534686;
  --el-button-border-color: #534686;
  --el-button-hover-bg-color: #6b5c9e;
  --el-button-hover-border-color: #6b5c9e;
}
</style>
