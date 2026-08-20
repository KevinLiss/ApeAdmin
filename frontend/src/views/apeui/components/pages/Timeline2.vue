<template>
  <div>
    <PageHeader title="Timeline v2" :breadcrumb="['APEUI库', 'Components', 'Timeline v2']" />

    <el-card shadow="hover" header="反向时间线（placement=right）" style="margin-bottom: 16px">
      <el-timeline>
        <el-timeline-item
          v-for="(event, idx) in events"
          :key="idx"
          :timestamp="event.timestamp"
          :type="event.type"
          :color="event.color"
          placement="right"
        >
          <div class="rich-content">
            <div class="rich-header">
              <el-tag size="small" :type="event.tagType" effect="dark">{{ event.category }}</el-tag>
              <h4 style="margin: 0; font-weight: 600; color: #534686">{{ event.title }}</h4>
            </div>
            <div class="rich-body" v-html="event.content"></div>
            <div class="rich-footer">
              <el-avatar :size="20" style="background: #534686">{{ event.author[0] }}</el-avatar>
              <span class="rich-author">{{ event.author }}</span>
              <el-divider direction="vertical" />
              <el-icon color="#909399"><View /></el-icon>
              <span class="rich-meta">{{ event.views }} 浏览</span>
              <el-divider direction="vertical" />
              <el-icon color="#909399"><ChatLineRound /></el-icon>
              <span class="rich-meta">{{ event.comments }} 评论</span>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="左右交替时间线">
          <el-timeline>
            <el-timeline-item
              v-for="(item, idx) in altEvents"
              :key="idx"
              :timestamp="item.timestamp"
              :type="item.type"
              :placement="idx % 2 === 0 ? 'top' : 'bottom'"
            >
              <div style="padding: 4px 0">
                <strong style="color: #534686">{{ item.title }}</strong>
                <p style="margin: 4px 0 0; color: #5a6273; font-size: 13px">{{ item.desc }}</p>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" header="带图标时间线">
          <el-timeline>
            <el-timeline-item
              v-for="(item, idx) in iconEvents"
              :key="idx"
              :timestamp="item.timestamp"
              :type="item.type"
              size="large"
            >
              <template #dot>
                <el-icon :size="20" :color="item.color"><component :is="item.icon" /></el-icon>
              </template>
              <div>
                <span style="font-weight: 600">{{ item.title }}</span>
                <p style="margin: 4px 0 0; color: #909399; font-size: 13px">{{ item.desc }}</p>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { View, ChatLineRound, Check, Upload, Delete, Edit, Bell } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const events = [
  {
    timestamp: '2026-08-20 10:30',
    type: 'primary' as const,
    color: '#534686',
    tagType: '' as const,
    category: '公告',
    title: '系统维护通知',
    content: '<p>系统将于今晚 <strong style="color:#534686">22:00-24:00</strong> 进行例行维护升级，届时服务将短暂中断。</p><p style="margin-top:6px;color:#909399;font-size:13px;">请提前保存工作内容，给您带来的不便敬请谅解。</p>',
    author: '管理员',
    views: 1258,
    comments: 23,
  },
  {
    timestamp: '2026-08-19 15:20',
    type: 'success' as const,
    color: '#67C100',
    tagType: 'success' as const,
    category: '版本',
    title: 'v1.2.0 版本发布',
    content: '<p>新增 <strong style="color:#534686">MCP-SSE 网关</strong>，支持 Tools/Resources/Prompts 三原语。</p><p style="margin-top:6px;color:#909399;font-size:13px;">优化审计日志查询性能，修复角色管理若干问题。</p>',
    author: '开发组',
    views: 862,
    comments: 15,
  },
  {
    timestamp: '2026-08-18 09:00',
    type: 'warning' as const,
    color: '#E56809',
    tagType: 'warning' as const,
    category: '安全',
    title: '安全策略更新',
    content: '<p>JWT Token 过期时间由 <strong>24小时</strong> 调整为 <strong style="color:#E56809">8小时</strong>。</p><p style="margin-top:6px;color:#909399;font-size:13px;">请所有用户重新登录以获取新策略 Token。</p>',
    author: '安全组',
    views: 534,
    comments: 8,
  },
  {
    timestamp: '2026-08-17 14:00',
    type: 'info' as const,
    color: '#909399',
    tagType: 'info' as const,
    category: '通知',
    title: '插件市场上线',
    content: '<p>插件市场已正式上线，支持 <strong style="color:#534686">进程内插件</strong> 扫描注册。</p><p style="margin-top:6px;color:#909399;font-size:13px;">开发者可通过插件系统扩展平台能力，重启后生效。</p>',
    author: '产品组',
    views: 943,
    comments: 31,
  },
  {
    timestamp: '2026-08-15 11:30',
    type: 'danger' as const,
    color: '#DC0808',
    tagType: 'danger' as const,
    category: '故障',
    title: '数据库连接异常修复',
    content: '<p>今晨 <strong style="color:#DC0808">09:12</strong> 出现数据库连接池耗尽，已于 09:18 恢复。</p><p style="margin-top:6px;color:#909399;font-size:13px;">根因：连接池未配置最大空闲数限制，已修复。</p>',
    author: '运维组',
    views: 420,
    comments: 5,
  },
]

const altEvents = [
  { timestamp: '2026-08-20', type: 'primary' as const, title: '需求评审', desc: '评审下一迭代功能需求' },
  { timestamp: '2026-08-18', type: 'success' as const, title: '代码合并', desc: 'feature/mcp-gateway 合入 master' },
  { timestamp: '2026-08-16', type: 'warning' as const, title: '性能测试', desc: 'API 响应时间基线测试' },
  { timestamp: '2026-08-14', type: 'info' as const, title: '文档更新', desc: 'API 文档同步更新' },
  { timestamp: '2026-08-12', type: 'danger' as const, title: 'Bug 修复', desc: '修复登录页 CSRF 校验' },
]

const iconEvents = [
  { timestamp: '已完成', type: 'success' as const, color: '#67C100', icon: Check, title: '环境搭建', desc: '开发环境与 CI/CD 配置完成' },
  { timestamp: '已完成', type: 'success' as const, color: '#67C100', icon: Edit, title: '核心开发', desc: 'RBAC 权限引擎开发完成' },
  { timestamp: '进行中', type: 'warning' as const, color: '#E56809', icon: Bell, title: 'MCP 网关', desc: 'SSE 网关三原语开发中' },
  { timestamp: '待开始', type: 'info' as const, color: '#909399', icon: Upload, title: '部署测试', desc: '生产环境部署与验收' },
  { timestamp: '待开始', type: 'info' as const, color: '#909399', icon: Delete, title: '清理优化', desc: '冗余代码清理与优化' },
]
</script>

<style scoped>
.rich-content {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #f0f0f5;
}
.rich-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.rich-body {
  color: #5a6273;
  font-size: 14px;
  line-height: 1.6;
}
.rich-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f5;
  font-size: 13px;
  color: #909399;
}
.rich-author {
  font-weight: 500;
}
.rich-meta {
  font-size: 12px;
}
</style>
