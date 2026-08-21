<template>
  <div>
    <PageHeader title="Scrollable" :breadcrumb="['APEUI库', 'Components', 'Scrollable']" />

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="基础滚动 (height=200px)">
          <el-scrollbar height="200px">
            <p v-for="i in 20" :key="i" style="margin: 0 0 12px; color: #5a6273; line-height: 1.8">
              这是第 {{ i }} 行内容。滚动条组件 el-scrollbar 提供自定义样式的滚动容器，支持垂直和水平滚动。
            </p>
          </el-scrollbar>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="不同高度 (max-height=150px)">
          <el-scrollbar max-height="150px">
            <p v-for="i in 15" :key="i" style="margin: 0 0 12px; color: #5a6273; line-height: 1.8">
              max-height 模式：内容不足 150px 时不显示滚动条，超出后自动出现。
              当前第 {{ i }} 行。
            </p>
          </el-scrollbar>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" header="水平滚动" style="margin-bottom: 16px">
      <p style="margin: 0 0 12px; color: #909399; font-size: 13px">内容超出容器宽度时出现水平滚动条</p>
      <div class="horizontal-wrapper">
        <el-scrollbar>
          <div class="horizontal-content">
            <div class="horizontal-card" v-for="i in 12" :key="i">
              <el-icon :size="24" color="#5A67F5"><component :is="horizontalIcons[(i - 1) % horizontalIcons.length]" /></el-icon>
              <span style="margin-top: 8px; font-size: 13px; color: #5a6273">卡片 {{ i }}</span>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="自定义滚动样式（紫色）">
          <el-scrollbar height="200px" class="purple-scrollbar">
            <div class="custom-scroll-content">
              <div class="custom-scroll-item" v-for="i in 10" :key="i">
                <el-avatar :size="36" style="background: linear-gradient(135deg, #5A67F5, #7F8AF8)">{{ i }}</el-avatar>
                <div>
                  <div style="font-weight: 500; color: #5A67F5">自定义滚动项 {{ i }}</div>
                  <div style="font-size: 13px; color: #909399">紫色主题滚动条样式</div>
                </div>
              </div>
            </div>
          </el-scrollbar>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Always Visible">
          <el-scrollbar height="200px" always>
            <p v-for="i in 12" :key="i" style="margin: 0 0 10px; color: #5a6273; line-height: 1.8">
              always 属性：滚动条始终可见（不随鼠标移出隐藏）。第 {{ i }} 行。
            </p>
          </el-scrollbar>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" header="嵌套滚动 + 虚拟场景">
      <el-row :gutter="16">
        <el-col :span="12">
          <div class="chat-wrapper">
            <div class="chat-header">
              <span style="font-weight: 600; color: #5A67F5">实时消息</span>
              <el-tag size="small" type="success">在线</el-tag>
            </div>
            <el-scrollbar height="240px" class="chat-scrollbar">
              <div class="chat-list">
                <div class="chat-item" v-for="msg in chatMessages" :key="msg.id" :class="msg.self ? 'chat-self' : ''">
                  <el-avatar :size="28" :style="{ background: msg.self ? '#5A67F5' : '#7F8AF8' }">{{ msg.user[0] }}</el-avatar>
                  <div class="chat-bubble" :class="msg.self ? 'chat-bubble-self' : 'chat-bubble-other'">
                    {{ msg.text }}
                  </div>
                </div>
              </div>
            </el-scrollbar>
            <div class="chat-input">
              <el-input placeholder="输入消息..." size="small" />
              <el-button type="primary" size="small">发送</el-button>
            </div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="terminal-wrapper">
            <div class="terminal-header">
              <span class="terminal-dot" style="background:#DC0808"></span>
              <span class="terminal-dot" style="background:#E56809"></span>
              <span class="terminal-dot" style="background:#67C100"></span>
              <span style="color:#909399;font-size:12px;margin-left:8px">bash — apeadmin@server</span>
            </div>
            <el-scrollbar height="240px" class="terminal-scrollbar">
              <div class="terminal-body">
                <p v-for="(line, idx) in terminalLines" :key="idx" class="terminal-line">
                  <span class="terminal-prompt">$</span> {{ line }}
                </p>
              </div>
            </el-scrollbar>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Cpu, Monitor, Bell, Setting, Box, DataLine, Star, ChatLineRound } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const horizontalIcons = [Cpu, Monitor, Bell, Setting, Box, DataLine, Star, ChatLineRound]

const chatMessages = [
  { id: 1, user: '张三', text: '你好，系统维护安排在今晚几点？', self: false },
  { id: 2, user: 'admin', text: '22:00-24:00，预计 2 小时内完成。', self: true },
  { id: 3, user: '张三', text: '期间服务完全不可用吗？', self: false },
  { id: 4, user: 'admin', text: '短暂中断，约 15 分钟。请提前保存工作。', self: true },
  { id: 5, user: '李四', text: '收到，我安排推迟提交操作。', self: false },
  { id: 6, user: 'admin', text: '感谢配合，维护完成后会通知大家。', self: true },
  { id: 7, user: '张三', text: '好的，辛苦了！', self: false },
  { id: 8, user: 'admin', text: '不客气，有问题随时联系。', self: true },
]

const terminalLines = [
  'cd /opt/apeadmin/backend',
  'source venv/bin/activate',
  'pip install -r requirements.txt',
  'Requirement already satisfied: fastapi',
  'Requirement already satisfied: sqlalchemy',
  'alembic upgrade head',
  'INFO  [alembic.runtime.migration] Running upgrade',
  'uvicorn src.main:app --host 0.0.0.0 --port 8000',
  'INFO:     Uvicorn running on http://0.0.0.0:8000',
  'INFO:     Application startup complete.',
]
</script>

<style scoped>
.horizontal-wrapper {
  width: 100%;
}
.horizontal-content {
  display: flex;
  gap: 12px;
  padding-bottom: 4px;
}
.horizontal-card {
  flex-shrink: 0;
  width: 120px;
  height: 100px;
  background: #f5f4fa;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid #ece9f5;
}
.purple-scrollbar :deep(.el-scrollbar__thumb) {
  background-color: #5A67F5;
}
.purple-scrollbar :deep(.el-scrollbar__thumb:hover) {
  background-color: #3B46C8;
}
.custom-scroll-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.custom-scroll-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}
.chat-wrapper {
  border: 1px solid #e9e7f3;
  border-radius: 10px;
  overflow: hidden;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #f5f4fa;
  border-bottom: 1px solid #e9e7f3;
}
.chat-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
}
.chat-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.chat-self {
  flex-direction: row-reverse;
}
.chat-bubble {
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
}
.chat-bubble-other {
  background: #f0eef7;
  color: #5a6273;
}
.chat-bubble-self {
  background: #5A67F5;
  color: #fff;
}
.chat-input {
  display: flex;
  gap: 8px;
  padding: 10px 16px;
  border-top: 1px solid #e9e7f3;
  background: #fafafa;
}
.terminal-wrapper {
  border: 1px solid #2a2438;
  border-radius: 10px;
  overflow: hidden;
  background: #1a1622;
}
.terminal-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #2a2438;
}
.terminal-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.terminal-scrollbar :deep(.el-scrollbar__thumb) {
  background-color: #5A67F5;
}
.terminal-body {
  padding: 14px 16px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
}
.terminal-line {
  margin: 0 0 4px;
  color: #c0b8d8;
}
.terminal-prompt {
  color: #A5ACFA;
  font-weight: bold;
  margin-right: 6px;
}
</style>
