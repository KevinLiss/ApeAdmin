<template>
  <div class="chat-video">
    <PageHeader title="Video Chat" :breadcrumb="['APEUI库', 'Applications', 'Video Chat']" />

    <el-row :gutter="30">
      <!-- Main Video Area -->
      <el-col :xs="24" :md="18">
        <div class="koho-card video-main">
          <!-- Call Info Bar -->
          <div class="call-info-bar">
            <div class="call-info-left">
              <div class="call-timer">
                <el-icon><VideoCamera /></el-icon>
                <span>{{ callDuration }}</span>
              </div>
              <el-tag type="info" size="small" effect="dark" round>
                {{ participants.length }} Participants
              </el-tag>
            </div>
            <div class="call-info-right">
              <el-button text circle :icon="FullScreen" @click="onFullscreen" />
              <el-button text circle :icon="Setting" @click="onSettings" />
            </div>
          </div>

          <!-- Main Video -->
          <div class="video-stage">
            <div class="video-placeholder">
              <el-icon :size="64"><Avatar /></el-icon>
              <p class="video-name">{{ mainSpeaker.name }}</p>
              <p class="video-mic-status">
                <el-icon v-if="mainSpeaker.muted" :size="16"><Mute /></el-icon>
                {{ mainSpeaker.muted ? 'Muted' : 'Speaking' }}
              </p>
            </div>

            <!-- Control Bar -->
            <div class="control-bar">
              <el-button
                :type="micOn ? 'primary' : 'danger'"
                circle
                size="large"
                @click="micOn = !micOn"
              >
                <el-icon :size="20"><component :is="micOn ? Microphone : Mute" /></el-icon>
              </el-button>
              <el-button
                :type="camOn ? 'primary' : 'danger'"
                circle
                size="large"
                @click="camOn = !camOn"
              >
                <el-icon :size="20"><component :is="camOn ? VideoCamera : VideoPause" /></el-icon>
              </el-button>
              <el-button
                :type="sharing ? 'warning' : 'default'"
                circle
                size="large"
                @click="sharing = !sharing"
              >
                <el-icon :size="20"><Share /></el-icon>
              </el-button>
              <el-button circle size="large" @click="onOpenChat" :class="{ 'has-badge': !chatOpen }">
                <el-icon :size="20"><ChatDotRound /></el-icon>
              </el-button>
              <el-button type="danger" circle size="large" @click="onHangup">
                <el-icon :size="20"><PhoneFilled /></el-icon>
              </el-button>
            </div>
          </div>

          <!-- Participant Thumbnails -->
          <div class="participant-strip">
            <div
              v-for="p in participants"
              :key="p.id"
              class="participant-thumb"
              :class="{ active: p.id === activeParticipantId }"
              @click="onSwitchSpeaker(p)"
            >
              <div class="thumb-video">
                <el-avatar :size="48" :src="p.avatar" />
                <el-icon v-if="p.muted" class="thumb-mute-icon" :size="14"><Mute /></el-icon>
              </div>
              <div class="thumb-info">
                <span class="thumb-name">{{ p.name }}</span>
                <span class="thumb-status" :class="p.status">{{ p.status === 'speaking' ? 'Speaking' : p.muted ? 'Muted' : 'Listening' }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Chat Sidebar -->
      <el-col :xs="24" :md="6">
        <div class="koho-card chat-sidebar-card">
          <div class="card-title">
            <el-icon><ChatDotRound /></el-icon>
            <span>In-Call Chat</span>
            <el-button text circle :icon="Close" size="small" style="margin-left: auto" @click="chatOpen = false" />
          </div>

          <div class="chat-messages">
            <div v-for="msg in chatMessages" :key="msg.id" class="chat-msg">
              <el-avatar :size="28" :src="msg.avatar" />
              <div class="chat-msg-body">
                <div class="chat-msg-meta">
                  <span class="chat-msg-author">{{ msg.name }}</span>
                  <span class="chat-msg-time">{{ msg.time }}</span>
                </div>
                <div class="chat-msg-text">{{ msg.text }}</div>
              </div>
            </div>
          </div>

          <div class="chat-input">
            <el-input
              v-model="chatInputText"
              placeholder="Type a message..."
              @keyup.enter="onSendChat"
              clearable
            />
            <el-button type="primary" :icon="Promotion" @click="onSendChat" circle />
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
  VideoCamera, VideoPause, Microphone, Mute, Share, ChatDotRound,
  PhoneFilled, FullScreen, Setting, Avatar, Promotion, Close,
} from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

const avatarBase = 'https://cube.elemecdn.com/'

const micOn = ref(true)
const camOn = ref(true)
const sharing = ref(false)
const chatOpen = ref(true)
const chatInputText = ref('')
const callDuration = ref('00:24:18')
const activeParticipantId = ref(1)

const participants = ref([
  { id: 1, name: 'Alice Chen', avatar: avatarBase + '3/7c/3ea6be94a7beba6d1c0be4dd3f6fbcjpeg.jpeg', muted: false, status: 'speaking' },
  { id: 2, name: 'Bob Smith', avatar: avatarBase + '1/34/19aa971b3b29b1f6c0e4dd3f6fbcjpeg.jpeg', muted: true, status: 'listening' },
  { id: 3, name: 'Carol Johnson', avatar: avatarBase + '9/c2/3b0b0e6e6f6b3b1b3b1b3b1b3b1b3b1b.jpeg', muted: false, status: 'listening' },
  { id: 4, name: 'David Lee', avatar: avatarBase + 'a/3f/a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3.jpeg', muted: true, status: 'listening' },
])

const mainSpeaker = computed(() => {
  return participants.value.find(p => p.id === activeParticipantId.value) || participants.value[0]
})

const chatMessages = ref([
  { id: 1, name: 'Alice Chen', avatar: avatarBase + '3/7c/3ea6be94a7beba6d1c0be4dd3f6fbcjpeg.jpeg', time: '10:20', text: 'Can everyone see my screen?' },
  { id: 2, name: 'Bob Smith', avatar: avatarBase + '1/34/19aa971b3b29b1f6c0e4dd3f6fbcjpeg.jpeg', time: '10:21', text: 'Yes, looks great!' },
  { id: 3, name: 'Carol Johnson', avatar: avatarBase + '9/c2/3b0b0e6e6f6b3b1b3b1b3b1b3b1b3b1b.jpeg', time: '10:22', text: 'Let\'s move to the next slide.' },
  { id: 4, name: 'David Lee', avatar: avatarBase + 'a/3f/a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3.jpeg', time: '10:24', text: 'I\'ll share the document after the call.' },
])

const onSwitchSpeaker = (p: any) => {
  activeParticipantId.value = p.id
  ElMessage.info(`Switched to ${p.name}`)
}
const onHangup = () => ElMessage.warning('Call ended')
const onFullscreen = () => ElMessage.info('Entering fullscreen mode')
const onSettings = () => ElMessage.info('Settings opened')
const onOpenChat = () => { chatOpen.value = true }
const onSendChat = () => {
  if (!chatInputText.value.trim()) return
  ElMessage.success('Message sent')
  chatInputText.value = ''
}
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

/* Call Info Bar */
.call-info-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.call-info-left { display: flex; align-items: center; gap: 16px; }
.call-timer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #534686;
}

/* Video Stage */
.video-stage {
  position: relative;
  background: #1a1a2e;
  border-radius: 16px;
  aspect-ratio: 16 / 9;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.video-placeholder {
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
}
.video-placeholder .el-icon { font-size: 64px; }
.video-name {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 12px 0 4px;
}
.video-mic-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* Control Bar */
.control-bar {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
  background: rgba(0, 0, 0, 0.5);
  padding: 12px 20px;
  border-radius: 32px;
  backdrop-filter: blur(10px);
}
.has-badge {
  position: relative;
}
.has-badge::after {
  content: '';
  position: absolute;
  top: 4px;
  right: 4px;
  width: 8px;
  height: 8px;
  background: #DC0808;
  border-radius: 50%;
}

/* Participant Strip */
.participant-strip {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.participant-thumb {
  flex-shrink: 0;
  width: 120px;
  padding: 10px;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  background: #f8f8f8;
  transition: all 0.2s;
}
.participant-thumb:hover { background: rgba(83, 70, 134, 0.08); }
.participant-thumb.active { border-color: #534686; background: rgba(83, 70, 134, 0.12); }
.thumb-video { position: relative; text-align: center; }
.thumb-mute-icon {
  position: absolute;
  bottom: 0;
  right: 30%;
  color: #DC0808;
  background: #fff;
  border-radius: 50%;
  padding: 2px;
}
.thumb-info { text-align: center; margin-top: 6px; }
.thumb-name {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #2b2b2b;
}
.thumb-status {
  font-size: 11px;
  color: #909399;
}
.thumb-status.speaking { color: #67C100; }

/* Chat Sidebar */
.chat-sidebar-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 500px;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
}
.chat-msg {
  display: flex;
  gap: 10px;
}
.chat-msg-body { flex: 1; }
.chat-msg-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}
.chat-msg-author { font-size: 13px; font-weight: 500; color: #534686; }
.chat-msg-time { font-size: 11px; color: #909399; }
.chat-msg-text {
  font-size: 14px;
  color: #2b2b2b;
  margin-top: 4px;
  background: #f5f5f5;
  padding: 8px 12px;
  border-radius: 10px;
  border-top-left-radius: 2px;
}
.chat-input {
  display: flex;
  gap: 8px;
  align-items: center;
}

:deep(.el-button--primary) {
  --el-color-primary: #534686;
  --el-button-bg-color: #534686;
  --el-button-border-color: #534686;
  --el-button-hover-bg-color: #6b5c9e;
  --el-button-hover-border-color: #6b5c9e;
}
:deep(.el-button--danger) {
  --el-color-primary: #DC0808;
}
</style>
