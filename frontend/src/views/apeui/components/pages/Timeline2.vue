<template>
  <div class="timeline2-page">
    <PageHeader title="Timeline v2" :breadcrumb="['APEUI库', 'Components', 'Timeline v2']" />

    <el-row :gutter="30">
      <!-- Left column: Activity Timeline -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Activity Timeline</span>
          </template>
          <el-timeline>
            <!-- Activity 1 -->
            <el-timeline-item
              timestamp="2 hours ago"
              type="primary"
              size="large"
              placement="right"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot primary-dot">
                  <Document />
                </el-icon>
              </template>
              <div class="timeline-content">
                <div class="content-header">
                  <h4 class="content-title">Published a new blog post</h4>
                  <el-tag size="small" type="primary" effect="dark">Blog</el-tag>
                </div>
                <p class="content-text">
                  发布了一篇关于 FastAPI 异步架构最佳实践的技术文章，
                  涵盖连接池管理、中间件链式调用、依赖注入等核心主题。
                </p>
                <div class="content-tags">
                  <el-tag size="small" type="info" effect="plain">FastAPI</el-tag>
                  <el-tag size="small" type="info" effect="plain">Python</el-tag>
                  <el-tag size="small" type="info" effect="plain">Async</el-tag>
                </div>
                <div class="content-footer">
                  <el-avatar :size="24" style="background: #534686">李</el-avatar>
                  <span class="footer-author">李明 · 高级后端工程师</span>
                  <el-divider direction="vertical" />
                  <el-icon color="#909399"><View /></el-icon>
                  <span class="footer-meta">328 浏览</span>
                </div>
              </div>
            </el-timeline-item>

            <!-- Activity 2 -->
            <el-timeline-item
              timestamp="5 hours ago"
              type="success"
              size="large"
              placement="right"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot success-dot">
                  <EditPen />
                </el-icon>
              </template>
              <div class="timeline-content">
                <div class="content-header">
                  <h4 class="content-title">Updated project documentation</h4>
                  <el-tag size="small" type="success" effect="dark">Docs</el-tag>
                </div>
                <p class="content-text">
                  更新了项目 API 文档，补充了 MCP-SSE 网关三原语（Tools / Resources / Prompts）
                  的完整接口定义与示例请求，并新增了插件开发指南章节。
                </p>
                <div class="content-footer">
                  <el-avatar :size="24" style="background: #67C100">王</el-avatar>
                  <span class="footer-author">王芳 · 技术文档工程师</span>
                </div>
              </div>
            </el-timeline-item>

            <!-- Activity 3 -->
            <el-timeline-item
              timestamp="1 day ago"
              type="warning"
              size="large"
              placement="right"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot warning-dot">
                  <ChatDotRound />
                </el-icon>
              </template>
              <div class="timeline-content">
                <div class="content-header">
                  <h4 class="content-title">Commented on a task</h4>
                  <el-tag size="small" type="warning" effect="dark">Comment</el-tag>
                </div>
                <p class="content-text">
                  建议将角色权限的级联删除策略改为软删除标记，避免误操作导致权限链断裂。
                  同时可以在回收站中提供 7 天恢复窗口。
                </p>
                <div class="comment-box">
                  <el-avatar :size="32" style="background: #E56809">陈</el-avatar>
                  <div class="comment-detail">
                    <span class="comment-author">陈晨 · 产品经理</span>
                    <span class="comment-task">→ 任务：RBAC 权限优化</span>
                  </div>
                </div>
              </div>
            </el-timeline-item>

            <!-- Activity 4 -->
            <el-timeline-item
              timestamp="2 days ago"
              type="primary"
              size="large"
              placement="right"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot primary-dot">
                  <CircleCheck />
                </el-icon>
              </template>
              <div class="timeline-content">
                <div class="content-header">
                  <h4 class="content-title">Completed sprint review</h4>
                  <el-tag size="small" type="primary" effect="dark">Sprint 12</el-tag>
                </div>
                <p class="content-text">
                  第 12 轮迭代评审完成，共交付 18 个功能点，修复 24 个缺陷，
                  整体完成度 92%。
                </p>
                <div class="progress-section">
                  <div class="progress-label">
                    <span>迭代完成度</span>
                    <span class="progress-value">92%</span>
                  </div>
                  <el-progress :percentage="92" :color="progressColors" :stroke-width="10" />
                </div>
                <div class="stat-row">
                  <div class="stat-item">
                    <span class="stat-num">18</span>
                    <span class="stat-label">功能交付</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-num">24</span>
                    <span class="stat-label">缺陷修复</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-num">7</span>
                    <span class="stat-label">团队成员</span>
                  </div>
                </div>
              </div>
            </el-timeline-item>

            <!-- Activity 5 -->
            <el-timeline-item
              timestamp="3 days ago"
              type="info"
              size="large"
              placement="right"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot info-dot">
                  <Star />
                </el-icon>
              </template>
              <div class="timeline-content">
                <div class="content-header">
                  <h4 class="content-title">Started new feature development</h4>
                  <el-tag size="small" type="info" effect="dark">Planning</el-tag>
                </div>
                <p class="content-text">
                  启动「智能审计分析」功能开发，计划引入 AI 辅助异常行为检测，
                  实现操作风险自动预警与周报生成。
                </p>
                <div class="content-tags">
                  <el-tag size="small" type="info" effect="plain">AI</el-tag>
                  <el-tag size="small" type="info" effect="plain">审计</el-tag>
                  <el-tag size="small" type="info" effect="plain">预警</el-tag>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>

      <!-- Right column: Project Milestones -->
      <el-col :span="12" class="col-item">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Project Milestones</span>
          </template>
          <el-timeline>
            <!-- Milestone 1 -->
            <el-timeline-item
              timestamp="Jan 10"
              type="primary"
              size="large"
              placement="left"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot primary-dot">
                  <Flag />
                </el-icon>
              </template>
              <div class="timeline-content">
                <div class="content-header">
                  <h4 class="content-title">Project Kickoff</h4>
                  <el-tag size="small" type="primary" effect="dark">启动</el-tag>
                </div>
                <p class="content-text">
                  ApeAdmin 管理底座项目正式启动，明确产品定位与技术选型，
                  组建跨职能开发团队。
                </p>
                <div class="team-section">
                  <span class="team-label">团队成员：</span>
                  <div class="avatar-group">
                    <el-avatar :size="32" style="background: #534686">李</el-avatar>
                    <el-avatar :size="32" style="background: #67C100">王</el-avatar>
                    <el-avatar :size="32" style="background: #E56809">陈</el-avatar>
                    <el-avatar :size="32" style="background: #909399">张</el-avatar>
                    <el-avatar :size="32" style="background: #DC0808">刘</el-avatar>
                    <el-avatar :size="32" class="more-avatar">+3</el-avatar>
                  </div>
                </div>
              </div>
            </el-timeline-item>

            <!-- Milestone 2 -->
            <el-timeline-item
              timestamp="Jan 25"
              type="success"
              size="large"
              placement="left"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot success-dot">
                  <Brush />
                </el-icon>
              </template>
              <div class="timeline-content">
                <div class="content-header">
                  <h4 class="content-title">Design Phase Complete</h4>
                  <el-tag size="small" type="success" effect="dark">设计</el-tag>
                </div>
                <p class="content-text">
                  完成全部 UI 设计稿与交互原型，蓝白灰现代 SaaS 风格通过评审，
                  确立 Element Plus + Tailwind 组件体系。
                </p>
                <div class="file-list">
                  <div class="file-item">
                    <el-icon color="#534686" :size="18"><Document /></el-icon>
                    <span class="file-name">UI-Design-Master-v2.fig</span>
                    <span class="file-size">24.5 MB</span>
                  </div>
                  <div class="file-item">
                    <el-icon color="#534686" :size="18"><Document /></el-icon>
                    <span class="file-name">Prototype-Interactive.html</span>
                    <span class="file-size">8.2 MB</span>
                  </div>
                  <div class="file-item">
                    <el-icon color="#534686" :size="18"><Picture /></el-icon>
                    <span class="file-name">Design-Tokens.json</span>
                    <span class="file-size">128 KB</span>
                  </div>
                </div>
              </div>
            </el-timeline-item>

            <!-- Milestone 3 -->
            <el-timeline-item
              timestamp="Feb 5"
              type="warning"
              size="large"
              placement="left"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot warning-dot">
                  <Cpu />
                </el-icon>
              </template>
              <div class="timeline-content">
                <div class="content-header">
                  <h4 class="content-title">Development Sprint 1</h4>
                  <el-tag size="small" type="warning" effect="dark">Sprint 1</el-tag>
                </div>
                <p class="content-text">
                  完成核心后端架构搭建与前端脚手架，RBAC 四层权限体系开发进度过半。
                </p>
                <div class="progress-section">
                  <div class="progress-label">
                    <span>后端进度</span>
                    <span class="progress-value">78%</span>
                  </div>
                  <el-progress :percentage="78" color="#E56809" :stroke-width="10" />
                </div>
                <div class="progress-section">
                  <div class="progress-label">
                    <span>前端进度</span>
                    <span class="progress-value">65%</span>
                  </div>
                  <el-progress :percentage="65" color="#534686" :stroke-width="10" />
                </div>
              </div>
            </el-timeline-item>

            <!-- Milestone 4 -->
            <el-timeline-item
              timestamp="Feb 20"
              type="info"
              size="large"
              placement="left"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot info-dot">
                  <UserFilled />
                </el-icon>
              </template>
              <div class="timeline-content">
                <div class="content-header">
                  <h4 class="content-title">User Testing</h4>
                  <el-tag size="small" type="info" effect="dark">测试</el-tag>
                </div>
                <p class="content-text">
                  完成 30 名内部用户的可用性测试，收集有效反馈 47 条，
                  整体满意度评分 4.3 / 5.0。
                </p>
                <div class="stat-row stat-row-grid">
                  <div class="stat-item">
                    <span class="stat-num stat-num-lg">30</span>
                    <span class="stat-label">测试用户</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-num stat-num-lg">47</span>
                    <span class="stat-label">反馈条目</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-num stat-num-lg">4.3</span>
                    <span class="stat-label">满意度</span>
                  </div>
                </div>
                <div class="satisfaction-bar">
                  <div class="progress-label">
                    <span>整体满意度</span>
                    <span class="progress-value">86%</span>
                  </div>
                  <el-progress :percentage="86" color="#909399" :stroke-width="10" />
                </div>
              </div>
            </el-timeline-item>

            <!-- Milestone 5 -->
            <el-timeline-item
              timestamp="Mar 1"
              type="danger"
              size="large"
              placement="left"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot danger-dot">
                  <Trophy />
                </el-icon>
              </template>
              <div class="timeline-content">
                <div class="content-header">
                  <h4 class="content-title">Final Release</h4>
                  <el-tag size="small" type="danger" effect="dark">v1.0.0</el-tag>
                </div>
                <p class="content-text">
                  ApeAdmin v1.0.0 正式发布！内置 RBAC 权限、CRUD 引擎、插件市场、
                  审计日志与 MCP-SSE 网关，已部署至内网生产环境。
                </p>
                <div class="release-section">
                  <div class="release-version">
                    <el-icon color="#DC0808" :size="24"><Trophy /></el-icon>
                    <span class="version-number">v1.0.0</span>
                    <el-tag size="small" type="danger" effect="dark">Stable</el-tag>
                  </div>
                  <div class="download-stats">
                    <div class="download-item">
                      <el-icon color="#534686"><Download /></el-icon>
                      <span class="download-value">12,486</span>
                      <span class="download-label">下载量</span>
                    </div>
                    <el-divider direction="vertical" />
                    <div class="download-item">
                      <el-icon color="#534686"><Star /></el-icon>
                      <span class="download-value">1,024</span>
                      <span class="download-label">收藏</span>
                    </div>
                    <el-divider direction="vertical" />
                    <div class="download-item">
                      <el-icon color="#534686"><ChatDotRound /></el-icon>
                      <span class="download-value">186</span>
                      <span class="download-label">评论</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import {
  Document,
  EditPen,
  ChatDotRound,
  CircleCheck,
  Star,
  Flag,
  Brush,
  Cpu,
  UserFilled,
  Trophy,
  Picture,
  View,
  Download,
} from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const progressColors = [
  { color: '#534686', percentage: 50 },
  { color: '#67C100', percentage: 100 },
]
</script>

<style scoped>
.timeline2-page {
  padding: 0;
}

.col-item {
  margin-bottom: 20px;
}

.card-title {
  font-weight: 700;
  font-size: 15px;
  color: #534686;
}

/* ---- Custom dots ---- */
.custom-dot {
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.primary-dot {
  background: linear-gradient(135deg, #6c5ce7, #534686);
}

.success-dot {
  background: linear-gradient(135deg, #67C100, #4e9d00);
}

.info-dot {
  background: linear-gradient(135deg, #909399, #6c7077);
}

.warning-dot {
  background: linear-gradient(135deg, #E56809, #b85000);
}

.danger-dot {
  background: linear-gradient(135deg, #DC0808, #a00606);
}

/* ---- Timeline content ---- */
.timeline-content {
  padding: 4px 0 4px 12px;
}

.content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.content-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: #534686;
}

.content-text {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.7;
  color: #5a6273;
}

.content-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.content-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f5;
  font-size: 13px;
  color: #909399;
}

.footer-author {
  font-weight: 500;
}

.footer-meta {
  font-size: 12px;
}

/* ---- Comment box ---- */
.comment-box {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
}

.comment-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.comment-author {
  font-size: 13px;
  font-weight: 600;
  color: #534686;
}

.comment-task {
  font-size: 12px;
  color: #909399;
}

/* ---- Progress section ---- */
.progress-section {
  margin-bottom: 12px;
}

.progress-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
  color: #5a6273;
}

.progress-value {
  font-weight: 700;
  color: #534686;
}

/* ---- Stat row ---- */
.stat-row {
  display: flex;
  gap: 24px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f5;
}

.stat-row-grid {
  border-top: none;
  padding-top: 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-num {
  font-size: 18px;
  font-weight: 700;
  color: #534686;
}

.stat-num-lg {
  font-size: 22px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

/* ---- Team section ---- */
.team-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.team-label {
  font-size: 13px;
  color: #909399;
  flex-shrink: 0;
}

.avatar-group {
  display: flex;
  align-items: center;
}

.avatar-group .el-avatar {
  margin-left: -8px;
  border: 2px solid #fff;
}

.avatar-group .el-avatar:first-child {
  margin-left: 0;
}

.more-avatar {
  background: #c0c4cc !important;
  font-size: 12px !important;
  font-weight: 600;
}

/* ---- File list ---- */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: background 0.2s;
}

.file-item:hover {
  background: #eef0f5;
}

.file-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: #5a6273;
}

.file-size {
  font-size: 12px;
  color: #909399;
}

/* ---- Release section ---- */
.release-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 8px;
}

.release-version {
  display: flex;
  align-items: center;
  gap: 10px;
}

.version-number {
  font-size: 22px;
  font-weight: 800;
  color: #DC0808;
}

.download-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.download-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.download-value {
  font-size: 16px;
  font-weight: 700;
  color: #534686;
}

.download-label {
  font-size: 13px;
  color: #909399;
}

.satisfaction-bar {
  margin-top: 12px;
}
</style>
