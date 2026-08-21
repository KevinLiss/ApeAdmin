<template>
  <div class="timeline1-page">
    <PageHeader title="时间轴一" :breadcrumb="['APEUI库', '组件示例', '时间轴一']" />

    <el-row :gutter="30">
      <el-col :span="24" class="col-item">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">垂直时间轴</span>
          </template>
          <el-timeline>
            <!-- Node 1 -->
            <el-timeline-item
              timestamp="Jan 14"
              type="primary"
              size="large"
              placement="top"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot primary-dot">
                  <Edit />
                </el-icon>
              </template>
              <div class="timeline-section">
                <h4 class="section-title">1. Start with this</h4>
                <p class="section-text">
                  新年伊始，祝贺你开启全新职业旅程！今天是你在新岗位的第一天，
                  满怀期待地迎接未来的每一天。愿你在新团队中如鱼得水，将过往积累的经验
                  转化为前行的动力，在新的赛道上书写属于自己的精彩篇章。保持好奇心，
                  保持热爱，每一个伟大的成就都始于迈出的第一步。
                </p>
                <div class="section-meta">
                  <el-tag size="small" type="primary" effect="plain">入职</el-tag>
                  <el-tag size="small" type="info" effect="plain" class="ml-8">新起点</el-tag>
                </div>
              </div>
            </el-timeline-item>

            <!-- Node 2 -->
            <el-timeline-item
              timestamp="Jan 18"
              type="success"
              size="large"
              placement="top"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot success-dot">
                  <VideoCamera />
                </el-icon>
              </template>
              <div class="timeline-section">
                <h4 class="section-title">Title of section 2</h4>
                <p class="section-text">
                  团队分享会议录像 — 新项目技术选型与架构方案讨论。
                </p>
                <div class="media-placeholder video-placeholder">
                  <el-icon :size="56" color="#fff" class="play-icon">
                    <VideoPlay />
                  </el-icon>
                  <span class="video-duration">32:14</span>
                </div>
                <div class="section-meta">
                  <el-tag size="small" type="success" effect="plain">视频会议</el-tag>
                  <el-tag size="small" type="info" effect="plain" class="ml-8">技术选型</el-tag>
                </div>
              </div>
            </el-timeline-item>

            <!-- Node 3 -->
            <el-timeline-item
              timestamp="Jan 24"
              type="success"
              size="large"
              placement="top"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot success-dot">
                  <Picture />
                </el-icon>
              </template>
              <div class="timeline-section">
                <h4 class="section-title">Title of section 3</h4>
                <p class="section-text">
                  项目架构图 — 采用 FastAPI + Vue3 微服务插件架构，
                  内置 RBAC 权限体系与 MCP-SSE 网关。
                </p>
                <div class="media-placeholder image-placeholder">
                  <el-icon :size="48" color="#909399">
                    <Picture />
                  </el-icon>
                </div>
                <div class="section-meta">
                  <el-tag size="small" type="primary" effect="plain">架构设计</el-tag>
                  <el-tag size="small" type="info" effect="plain" class="ml-8">PNG 1920×1080</el-tag>
                </div>
              </div>
            </el-timeline-item>

            <!-- Node 4 -->
            <el-timeline-item
              timestamp="Feb 14"
              type="info"
              size="large"
              placement="top"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot info-dot">
                  <Headset />
                </el-icon>
              </template>
              <div class="timeline-section">
                <h4 class="section-title">Title of section 4</h4>
                <p class="section-text">
                  产品需求语音备忘 — 关于下一迭代功能优先级与排期的口头记录。
                </p>
                <div class="audio-player-placeholder">
                  <el-icon :size="24" color="#5A67F5" class="audio-play-btn">
                    <VideoPlay />
                  </el-icon>
                  <div class="audio-wave">
                    <span v-for="n in 28" :key="n" class="wave-bar" :style="{ height: barHeights[n - 1] }"></span>
                  </div>
                  <span class="audio-time">04:52</span>
                </div>
                <div class="section-meta">
                  <el-tag size="small" type="info" effect="plain">语音备忘</el-tag>
                  <el-tag size="small" type="warning" effect="plain" class="ml-8">4分52秒</el-tag>
                </div>
              </div>
            </el-timeline-item>

            <!-- Node 5 -->
            <el-timeline-item
              timestamp="Feb 18"
              type="warning"
              size="large"
              placement="top"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot warning-dot">
                  <Picture />
                </el-icon>
              </template>
              <div class="timeline-section">
                <h4 class="section-title">Title of section 5</h4>
                <p class="section-text">
                  界面原型截图 — ApeAdmin 后台管理系统主界面预览，
                  蓝白灰现代 SaaS 风格，侧边栏导航 + 卡片式仪表盘布局。
                </p>
                <div class="media-placeholder image-placeholder">
                  <el-icon :size="48" color="#909399">
                    <Picture />
                  </el-icon>
                </div>
                <div class="section-meta">
                  <el-tag size="small" type="warning" effect="plain">原型设计</el-tag>
                  <el-tag size="small" type="info" effect="plain" class="ml-8">UI/UX</el-tag>
                </div>
              </div>
            </el-timeline-item>

            <!-- Node 6 -->
            <el-timeline-item
              timestamp="Feb 26"
              type="danger"
              size="large"
              placement="top"
            >
              <template #dot>
                <el-icon :size="20" color="#fff" class="custom-dot danger-dot">
                  <Edit />
                </el-icon>
              </template>
              <div class="timeline-section">
                <h4 class="section-title">Final Section</h4>
                <p class="section-text">
                  历时一个半月的迭代周期正式收尾。从最初的架构选型到最终的产品交付，
                  每一个环节都凝聚着团队的智慧与汗水。感谢每一位伙伴的付出，
                  让我们一起期待下一个里程碑的到来。前路漫漫，唯有热爱与坚持不可辜负。
                </p>
                <div class="section-meta">
                  <el-tag size="small" type="danger" effect="plain">里程碑完成</el-tag>
                  <el-tag size="small" type="success" effect="plain" class="ml-8">项目交付</el-tag>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="30">
      <el-col :span="24" class="col-item">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Compact Timeline</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="item in compactEvents"
              :key="item.id"
              :timestamp="item.timestamp"
              :type="item.type"
              size="normal"
              placement="top"
            >
              <div class="compact-item">
                <el-icon :size="16" :color="item.color"><component :is="item.icon" /></el-icon>
                <span class="compact-title">{{ item.title }}</span>
                <span class="compact-desc">{{ item.desc }}</span>
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
  Edit,
  VideoCamera,
  Picture,
  Headset,
  VideoPlay,
  Document,
  Check,
  Bell,
  Upload,
} from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const barHeights = [
  '8px', '14px', '20px', '12px', '24px', '18px', '10px', '28px',
  '16px', '22px', '6px', '30px', '14px', '20px', '12px', '26px',
  '10px', '18px', '24px', '8px', '16px', '28px', '14px', '20px',
  '12px', '22px', '10px', '18px',
]

const compactEvents = [
  { id: 1, timestamp: 'Feb 26', type: 'primary' as const, color: '#5A67F5', icon: Document, title: '项目立项', desc: '完成需求评审与技术方案确定' },
  { id: 2, timestamp: 'Feb 20', type: 'success' as const, color: '#67C100', icon: Check, title: '核心开发完成', desc: 'RBAC 权限引擎与 CRUD 体系交付' },
  { id: 3, timestamp: 'Feb 14', type: 'warning' as const, color: '#E56809', icon: Bell, title: '集成测试', desc: '插件系统与 MCP 网关联调进行中' },
  { id: 4, timestamp: 'Feb 8', type: 'info' as const, color: '#909399', icon: Upload, title: '部署预演', desc: '预生产环境部署验证通过' },
  { id: 5, timestamp: 'Feb 1', type: 'danger' as const, color: '#DC0808', icon: Edit, title: '问题修复', desc: '修复审计日志查询性能瓶颈' },
]
</script>

<style scoped>
.timeline1-page {
  padding: 0;
}

.col-item {
  margin-bottom: 20px;
}

.card-title {
  font-weight: 700;
  font-size: 15px;
  color: #5A67F5;
}

/* ---- Custom dot styles ---- */
.custom-dot {
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.primary-dot {
  background: linear-gradient(135deg, #4D9FFF, #5A67F5);
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

/* ---- Timeline section ---- */
.timeline-section {
  padding: 4px 0 4px 12px;
}

.section-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 700;
  color: #5A67F5;
}

.section-text {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.75;
  color: #5a6273;
}

.section-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ml-8 {
  margin-left: 0;
}

/* ---- Media placeholders ---- */
.media-placeholder {
  background: #f5f7fa;
  border-radius: 12px;
  aspect-ratio: 16 / 9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
}

.video-placeholder {
  background: #1a1a2e;
}

.video-placeholder .play-icon {
  cursor: pointer;
  transition: transform 0.2s;
}

.video-placeholder .play-icon:hover {
  transform: scale(1.15);
}

.video-duration {
  position: absolute;
  bottom: 10px;
  right: 12px;
  color: #fff;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.6);
  padding: 2px 8px;
  border-radius: 4px;
}

.image-placeholder {
  background: #f5f7fa;
  border: 2px dashed #dcdfe6;
}

/* ---- Audio player placeholder ---- */
.audio-player-placeholder {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 12px;
}

.audio-play-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #fff;
  border: 1px solid #e0e0eb;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: box-shadow 0.2s;
}

.audio-play-btn:hover {
  box-shadow: 0 2px 12px rgba(90, 103, 245, 0.2);
}

.audio-wave {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 3px;
  height: 32px;
}

.wave-bar {
  width: 3px;
  background: #5A67F5;
  border-radius: 2px;
  opacity: 0.7;
}

.audio-time {
  font-size: 13px;
  color: #909399;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}

/* ---- Compact timeline ---- */
.compact-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.compact-title {
  font-weight: 600;
  font-size: 14px;
  color: #5A67F5;
}

.compact-desc {
  font-size: 13px;
  color: #909399;
}
</style>
