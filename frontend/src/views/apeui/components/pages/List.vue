<template>
  <div>
    <PageHeader title="Lists" :breadcrumb="['APEUI库', 'Components', 'Lists']" />

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="可滚动列表 (el-scrollbar)">
          <el-scrollbar height="300px">
            <div class="scroll-list">
              <div class="scroll-list-item" v-for="item in 20" :key="item">
                <el-avatar :size="32" style="background: #534686">{{ item }}</el-avatar>
                <div class="scroll-list-body">
                  <span class="scroll-list-title">列表项 {{ item }}</span>
                  <span class="scroll-list-desc">这是列表项的描述信息内容</span>
                </div>
                <el-tag size="small" type="info">标签</el-tag>
              </div>
            </div>
          </el-scrollbar>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="带图标的列表">
          <div class="icon-list">
            <div class="icon-list-item" v-for="item in iconList" :key="item.title">
              <div class="icon-list-icon" :style="{ background: item.bg }">
                <el-icon :size="20" color="#fff"><component :is="item.icon" /></el-icon>
              </div>
              <div class="icon-list-body">
                <span class="icon-list-title">{{ item.title }}</span>
                <span class="icon-list-desc">{{ item.desc }}</span>
              </div>
              <el-button text type="primary" size="small">查看</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="简单列表">
          <ul class="simple-list">
            <li v-for="(item, idx) in simpleList" :key="idx">
              <span class="simple-list-dot" :style="{ background: item.color }"></span>
              <span>{{ item.text }}</span>
              <span class="simple-list-time">{{ item.time }}</span>
            </li>
          </ul>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="描述列表 (el-descriptions)">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">admin</el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag size="small" type="danger">超级管理员</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">admin@apeadmin.com</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag size="small" type="success">在线</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">2026-08-01 08:00:00</el-descriptions-item>
            <el-descriptions-item label="最后登录">2026-08-20 09:15:32</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" header="通知列表（带状态）">
      <div class="notice-list">
        <div class="notice-item" v-for="item in noticeList" :key="item.id">
          <el-badge is-dot :type="item.read ? 'info' : 'danger'">
            <el-icon :size="20" :color="item.read ? '#c0c4cc' : '#534686'"><component :is="item.icon" /></el-icon>
          </el-badge>
          <div class="notice-body">
            <div class="notice-title" :class="{ 'notice-unread': !item.read }">{{ item.title }}</div>
            <div class="notice-desc">{{ item.desc }}</div>
          </div>
          <span class="notice-time">{{ item.time }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Bell, Message, Setting, UserFilled, Tickets } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const iconList = [
  { title: '系统消息', desc: '系统维护通知已发布', icon: Bell, bg: '#534686' },
  { title: '私信', desc: '收到 2 条新私信', icon: Message, bg: '#7b6fa8' },
  { title: '设置', desc: '安全策略已更新', icon: Setting, bg: '#3EBCB9' },
  { title: '用户', desc: '3 名新用户待审核', icon: UserFilled, bg: '#E56809' },
  { title: '工单', desc: '5 条工单待处理', icon: Tickets, bg: '#DC0808' },
]

const simpleList = [
  { text: '项目启动会议', time: '09:00', color: '#534686' },
  { text: '需求评审完成', time: '10:30', color: '#67C100' },
  { text: '代码审查', time: '14:00', color: '#E56809' },
  { text: '部署测试环境', time: '16:00', color: '#3EBCB9' },
  { text: '提交日报', time: '18:00', color: '#909399' },
]

const noticeList = [
  { id: 1, title: '系统维护通知', desc: '系统将于今晚 22:00-24:00 进行例行维护升级', time: '2分钟前', read: false, icon: Bell },
  { id: 2, title: '新用户审核', desc: '用户 zhangsan 提交了注册申请，请尽快审核', time: '15分钟前', read: false, icon: UserFilled },
  { id: 3, title: '工单更新', desc: '工单 #2024-0820 已被分配给运维组', time: '1小时前', read: false, icon: Tickets },
  { id: 4, title: '安全提醒', desc: '检测到异常登录尝试，已自动拦截', time: '3小时前', read: true, icon: Setting },
  { id: 5, title: '版本更新', desc: 'v1.2.0 已发布，请查看更新日志', time: '昨天', read: true, icon: Setting },
]
</script>

<style scoped>
.scroll-list {
  display: flex;
  flex-direction: column;
}
.scroll-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 4px;
  border-bottom: 1px solid #f0f0f5;
}
.scroll-list-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.scroll-list-title {
  font-weight: 500;
  color: #303133;
}
.scroll-list-desc {
  font-size: 13px;
  color: #909399;
}
.icon-list {
  display: flex;
  flex-direction: column;
}
.icon-list-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f5;
}
.icon-list-item:last-child {
  border-bottom: none;
}
.icon-list-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-list-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.icon-list-title {
  font-weight: 500;
  color: #303133;
}
.icon-list-desc {
  font-size: 13px;
  color: #909399;
}
.simple-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.simple-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f5;
  color: #5a6273;
  font-size: 14px;
}
.simple-list li:last-child {
  border-bottom: none;
}
.simple-list-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.simple-list-time {
  margin-left: auto;
  color: #c0c4cc;
  font-size: 13px;
}
.notice-list {
  display: flex;
  flex-direction: column;
}
.notice-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid #f0f0f5;
}
.notice-item:last-child {
  border-bottom: none;
}
.notice-body {
  flex: 1;
}
.notice-title {
  font-weight: 500;
  color: #5a6273;
}
.notice-unread {
  color: #534686;
  font-weight: 600;
}
.notice-desc {
  font-size: 13px;
  color: #909399;
  margin-top: 2px;
}
.notice-time {
  color: #c0c4cc;
  font-size: 13px;
  white-space: nowrap;
}
</style>
