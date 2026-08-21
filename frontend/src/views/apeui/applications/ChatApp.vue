<template>
  <div class="chat-app">
    <PageHeader title="聊天应用" :breadcrumb="['APEUI库', '应用中心', '聊天应用']" />

    <el-row :gutter="30">
      <!-- Left: Conversation List -->
      <el-col :xs="24" :sm="7" :md="6">
        <div class="koho-card chat-sidebar">
          <div class="card-title">
            <el-icon><ChatDotRound /></el-icon>
            <span>聊天</span>
          </div>
          <el-input
            v-model="searchText"
            placeholder="Search conversations..."
            :prefix-icon="Search"
            clearable
            style="margin-bottom: 12px"
          />
          <div class="conversation-list">
            <div
              v-for="conv in filteredConversations"
              :key="conv.id"
              class="conversation-item"
              :class="{ active: conv.id === activeConvId }"
              @click="onSelectConv(conv)"
            >
              <div class="conv-avatar-wrap">
                <el-avatar :size="44" :src="conv.avatar" />
                <span class="status-dot" :class="conv.status"></span>
              </div>
              <div class="conv-info">
                <div class="conv-top">
                  <span class="conv-name">{{ conv.name }}</span>
                  <span class="conv-time">{{ conv.time }}</span>
                </div>
                <div class="conv-bottom">
                  <span class="conv-last-msg">{{ conv.lastMsg }}</span>
                  <el-badge v-if="conv.unread > 0" :value="conv.unread" class="conv-badge" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Center: Chat Area -->
      <el-col :xs="24" :sm="17" :md="12">
        <div class="koho-card chat-area">
          <!-- Chat Header -->
          <div class="chat-header">
            <div class="chat-header-left">
              <el-avatar :size="40" :src="activeConversation.avatar" />
              <div>
                <div class="chat-header-name">{{ activeConversation.name }}</div>
                <div class="chat-header-status">
                  <span class="status-dot small" :class="activeConversation.status"></span>
                  {{ activeConversation.status === 'online' ? 'Active now' : activeConversation.status === 'away' ? 'Away' : 'Offline' }}
                </div>
              </div>
            </div>
            <div class="chat-header-actions">
              <el-button text circle :icon="Phone" @click="onCall" />
              <el-button text circle :icon="VideoCamera" @click="onVideoCall" />
              <el-button text circle :icon="MoreFilled" @click="onMoreOptions" />
            </div>
          </div>

          <!-- Messages -->
          <div class="messages-area">
            <div
              v-for="msg in activeMessages"
              :key="msg.id"
              class="message-row"
              :class="msg.fromMe ? 'me' : 'other'"
            >
              <el-avatar v-if="!msg.fromMe" :size="32" :src="activeConversation.avatar" class="msg-avatar" />
              <div class="message-bubble" :class="msg.fromMe ? 'bubble-me' : 'bubble-other'">
                <div class="message-text">{{ msg.text }}</div>
                <div class="message-time">{{ msg.time }}</div>
              </div>
              <el-avatar v-if="msg.fromMe" :size="32" :src="myAvatar" class="msg-avatar" />
            </div>
          </div>

          <!-- Input -->
          <div class="chat-input-area">
            <el-button text circle :icon="Promotion" @click="onSendFile" />
            <el-input
              v-model="inputText"
              placeholder="Type a message..."
              @keyup.enter="onSend"
              clearable
            />
            <el-button text circle :icon="Picture" @click="onSendImage" />
            <el-button type="primary" :icon="Promotion" @click="onSend" round>发送</el-button>
          </div>
        </div>
      </el-col>

      <!-- Right: 联系信息 -->
      <el-col :xs="24" :md="6">
        <div class="koho-card">
          <div class="card-title">
            <el-icon><User /></el-icon>
            <span>联系信息</span>
          </div>
          <div class="contact-profile">
            <el-avatar :size="80" :src="activeConversation.avatar" />
            <div class="contact-name">{{ activeConversation.name }}</div>
            <div class="contact-role">{{ activeConversation.role }}</div>
            <div class="contact-status-row">
              <span class="status-dot small" :class="activeConversation.status"></span>
              {{ activeConversation.status === 'online' ? 'Active now' : 'Last seen 2h ago' }}
            </div>
          </div>

          <el-divider />

          <div class="contact-section-title">
            <el-icon><Folder /></el-icon>
            共享文件
          </div>
          <div class="shared-files">
            <div v-for="file in sharedFiles" :key="file.id" class="shared-file-item">
              <div class="file-icon" :style="{ background: file.bg, color: file.color }">
                <el-icon :size="20"><component :is="file.icon" /></el-icon>
              </div>
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">{{ file.size }} · {{ file.date }}</div>
              </div>
              <el-button text circle :icon="Download" @click="onDownload(file)" />
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ChatDotRound, Search, Phone, VideoCamera, MoreFilled,
  Promotion, Picture, User, Folder, Download, Document, Files,
} from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

const avatarBase = 'https://cube.elemecdn.com/'
const myAvatar = avatarBase + '0/88/03b0d432e8c87b879d3e4e37b8f6f6jpeg.jpeg'

const searchText = ref('')
const inputText = ref('')
const activeConvId = ref(1)

const conversations = ref([
  { id: 1, name: 'Alice Chen', avatar: avatarBase + '3/7c/3ea6be94a7beba6d1c0be4dd3f6fbcjpeg.jpeg', lastMsg: 'Sure, I\'ll send the report by Friday', time: '10:42', unread: 2, status: 'online', role: 'Product Manager' },
  { id: 2, name: 'Bob Smith', avatar: avatarBase + '1/34/19aa971b3b29b1f6c0e4dd3f6fbcjpeg.jpeg', lastMsg: 'Great! Let\'s schedule a meeting', time: '09:30', unread: 0, status: 'online', role: 'Frontend Developer' },
  { id: 3, name: 'Carol Johnson', avatar: avatarBase + '9/c2/3b0b0e6e6f6b3b1b3b1b3b1b3b1b3b1b.jpeg', lastMsg: 'The design mockups are ready for review', time: 'Yesterday', unread: 5, status: 'away', role: 'UX Designer' },
  { id: 4, name: 'David Lee', avatar: avatarBase + 'a/3f/a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3.jpeg', lastMsg: 'Thanks for the update!', time: 'Yesterday', unread: 0, status: 'offline', role: 'Backend Developer' },
  { id: 5, name: 'Emma Wilson', avatar: avatarBase + 'e/13/6734909d0f6c4e0b3b1b3b1b3b1b3b1b.jpeg', lastMsg: 'Can you review my pull request?', time: 'Mon', unread: 1, status: 'online', role: 'Data Analyst' },
  { id: 6, name: 'Frank Miller', avatar: avatarBase + '0/88/03b0d432e8c87b879d3e4e37b8f6f6jpeg.jpeg', lastMsg: 'Deployment is complete', time: 'Sun', unread: 0, status: 'offline', role: 'DevOps Engineer' },
  { id: 7, name: 'Grace Park', avatar: avatarBase + '3/7c/3ea6be94a7beba6d1c0be4dd3f6fbcjpeg.jpeg', lastMsg: 'Let\'s catch up next week', time: 'Sun', unread: 3, status: 'away', role: 'QA Engineer' },
])

const messagesData: Record<number, any[]> = {
  1: [
    { id: 1, fromMe: false, text: 'Hi William! How are you doing today?', time: '10:15' },
    { id: 2, fromMe: true, text: 'Hey Alice! I\'m doing great, thanks for asking. How about you?', time: '10:17' },
    { id: 3, fromMe: false, text: 'I\'m good too. I wanted to talk to you about the Q3 report.', time: '10:20' },
    { id: 4, fromMe: true, text: 'Sure, what do you need? I can help with the data analysis part.', time: '10:22' },
    { id: 5, fromMe: false, text: 'That would be perfect! Can you have it ready by this Friday?', time: '10:30' },
    { id: 6, fromMe: true, text: 'Absolutely. I\'ll start working on it right away.', time: '10:35' },
    { id: 7, fromMe: false, text: 'Sure, I\'ll send the report by Friday', time: '10:42' },
    { id: 8, fromMe: true, text: 'Sounds great! Looking forward to seeing the final version.', time: '10:44' },
  ],
  2: [
    { id: 1, fromMe: false, text: 'Hey, did you see the new component library update?', time: '09:10' },
    { id: 2, fromMe: true, text: 'Yes! The new features look amazing. We should upgrade.', time: '09:15' },
    { id: 3, fromMe: false, text: 'Great! Let\'s schedule a meeting to discuss the migration plan.', time: '09:30' },
  ],
  3: [
    { id: 1, fromMe: false, text: 'The design mockups are ready for review', time: 'Yesterday' },
  ],
  4: [
    { id: 1, fromMe: false, text: 'Thanks for the update!', time: 'Yesterday' },
  ],
  5: [
    { id: 1, fromMe: false, text: 'Can you review my pull request?', time: 'Mon' },
  ],
  6: [
    { id: 1, fromMe: false, text: 'Deployment is complete', time: 'Sun' },
  ],
  7: [
    { id: 1, fromMe: false, text: 'Let\'s catch up next week', time: 'Sun' },
  ],
}

const activeConversation = computed(() => conversations.value.find(c => c.id === activeConvId.value) || conversations.value[0])
const activeMessages = computed(() => messagesData[activeConvId.value] || [])

const filteredConversations = computed(() => {
  if (!searchText.value) return conversations.value
  return conversations.value.filter(c => c.name.toLowerCase().includes(searchText.value.toLowerCase()))
})

const sharedFiles = ref([
  { id: 1, name: 'Q3 Report Draft.pdf', size: '2.4 MB', date: 'Aug 15', icon: Document, bg: '#fef0e6', color: '#E56809' },
  { id: 2, name: 'Design Specs.xlsx', size: '1.1 MB', date: 'Aug 12', icon: Files, bg: '#e8f5e9', color: '#67C100' },
  { id: 3, name: 'Meeting Notes.docx', size: '320 KB', date: 'Aug 10', icon: Document, bg: '#e3f2fd', color: '#3EBCB9' },
  { id: 4, name: 'Project Archive.zip', size: '45 MB', date: 'Aug 05', icon: Files, bg: '#EAF1FF', color: '#5A67F5' },
])

const onSelectConv = (conv: any) => {
  activeConvId.value = conv.id
  conv.unread = 0
}
const onSend = () => {
  if (!inputText.value.trim()) return
  ElMessage.success('Message sent')
  inputText.value = ''
}
const onSendFile = () => ElMessage.info('File attachment opened')
const onSendImage = () => ElMessage.info('Image picker opened')
const onCall = () => ElMessage.success('Calling ' + activeConversation.value.name)
const onVideoCall = () => ElMessage.success('Starting video call with ' + activeConversation.value.name)
const onMoreOptions = () => ElMessage.info('More options')
const onDownload = (file: any) => ElMessage.success(`Downloading ${file.name}`)
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
  color: #5A67F5;
  margin-bottom: 16px;
}
.card-title .el-icon { font-size: 20px; }

/* Conversation List */
.conversation-list { display: flex; flex-direction: column; gap: 4px; max-height: 500px; overflow-y: auto; }
.conversation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}
.conversation-item:hover { background: rgba(90, 103, 245, 0.06); }
.conversation-item.active { background: rgba(90, 103, 245, 0.14); }
.conv-avatar-wrap { position: relative; flex-shrink: 0; }
.status-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid #fff;
}
.status-dot.small { width: 8px; height: 8px; }
.status-dot.online { background: #67C100; }
.status-dot.away { background: #E56809; }
.status-dot.offline { background: #ccc; }
.conv-info { flex: 1; min-width: 0; }
.conv-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.conv-name { font-size: 14px; font-weight: 600; color: #2b2b2b; }
.conv-time { font-size: 11px; color: #909399; }
.conv-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.conv-last-msg {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

/* Chat Area */
.chat-area {
  display: flex;
  flex-direction: column;
  min-height: 600px;
}
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}
.chat-header-left { display: flex; align-items: center; gap: 12px; }
.chat-header-name { font-size: 16px; font-weight: 600; color: #2b2b2b; }
.chat-header-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}
.chat-header-actions { display: flex; gap: 4px; }

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.message-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}
.message-row.me { justify-content: flex-end; }
.message-row.other { justify-content: flex-start; }
.msg-avatar { flex-shrink: 0; }
.message-bubble {
  max-width: 70%;
  padding: 10px 16px;
  border-radius: 16px;
}
.bubble-me {
  background: #5A67F5;
  color: #fff;
  border-bottom-right-radius: 4px;
}
.bubble-other {
  background: #f5f5f5;
  color: #2b2b2b;
  border-bottom-left-radius: 4px;
}
.message-text { font-size: 14px; line-height: 1.5; }
.message-time {
  font-size: 11px;
  margin-top: 4px;
  opacity: 0.6;
}

.chat-input-area {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

/* 联系信息 */
.contact-profile {
  text-align: center;
  padding: 12px 0;
}
.contact-name {
  font-size: 18px;
  font-weight: 600;
  color: #2b2b2b;
  margin-top: 12px;
}
.contact-role {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
.contact-status-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  color: #67C100;
  margin-top: 8px;
}
.contact-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #5A67F5;
  margin-bottom: 16px;
}
.shared-files { display: flex; flex-direction: column; gap: 12px; }
.shared-file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 10px;
  transition: background 0.2s;
}
.shared-file-item:hover { background: rgba(90, 103, 245, 0.06); }
.file-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.file-info { flex: 1; min-width: 0; }
.file-name {
  font-size: 13px;
  font-weight: 500;
  color: #2b2b2b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.file-meta { font-size: 12px; color: #909399; }

:deep(.el-button--primary) {
  --el-color-primary: #5A67F5;
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
}
:deep(.el-badge__content) {
  background-color: #DC0808;
}
</style>
