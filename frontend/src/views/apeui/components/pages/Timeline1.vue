<template>
  <div>
    <PageHeader title="Timeline v1" :breadcrumb="['APEUI库', 'Components', 'Timeline v1']" />

    <el-card shadow="hover" header="项目开发进度" style="margin-bottom: 16px">
      <el-timeline>
        <el-timeline-item
          v-for="(event, idx) in events"
          :key="idx"
          :timestamp="event.timestamp"
          :type="event.type"
          :hollow="event.hollow"
          placement="top"
        >
          <el-card shadow="hover" :body-style="{ padding: '12px 16px' }">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px">
              <el-icon :color="event.color"><component :is="event.icon" /></el-icon>
              <h4 style="margin: 0; font-weight: 600; color: #534686">{{ event.title }}</h4>
            </div>
            <p style="margin: 0; color: #5a6273; font-size: 13px">{{ event.desc }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="系统更新日志">
          <el-timeline>
            <el-timeline-item
              v-for="log in sysLogs"
              :key="log.id"
              :timestamp="log.timestamp"
              :type="log.type"
              size="large"
            >
              <span style="font-weight: 600; color: #534686">{{ log.version }}</span>
              <p style="margin: 4px 0 0; color: #5a6273; font-size: 13px">{{ log.content }}</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="用户操作记录">
          <el-timeline reverse>
            <el-timeline-item
              v-for="log in userLogs"
              :key="log.id"
              :timestamp="log.timestamp"
              :type="log.type"
            >
              <div style="display: flex; align-items: center; gap: 8px">
                <el-avatar :size="24" style="background: #534686">{{ log.user[0] }}</el-avatar>
                <span style="font-size: 13px">{{ log.user }} {{ log.action }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { Check, Close, Loading, Clock, Document, Upload, Edit, Setting } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const events = [
  { timestamp: '2026-08-01', title: '项目启动', desc: '完成需求评审和技术方案设计', type: 'primary' as const, hollow: false, icon: Document, color: '#534686' },
  { timestamp: '2026-08-05', title: '架构搭建', desc: 'FastAPI + Vue3 项目脚手架完成', type: 'primary' as const, hollow: false, icon: Setting, color: '#534686' },
  { timestamp: '2026-08-10', title: '核心功能开发', desc: 'RBAC 权限系统和 CRUD 引擎开发中', type: 'warning' as const, hollow: false, icon: Edit, color: '#E56809' },
  { timestamp: '2026-08-15', title: '插件系统', desc: '进程内插件扫描和注册机制完成', type: 'success' as const, hollow: false, icon: Check, color: '#67C100' },
  { timestamp: '2026-08-18', title: 'MCP 网关', desc: 'MCP-SSE 网关三原语开发进行中', type: 'warning' as const, hollow: true, icon: Loading, color: '#E56809' },
  { timestamp: '2026-08-25', title: '测试验收', desc: '端到端测试与性能验收（计划中）', type: 'info' as const, hollow: true, icon: Clock, color: '#909399' },
  { timestamp: '2026-08-30', title: '正式上线', desc: '生产环境部署（计划中）', type: 'info' as const, hollow: true, icon: Upload, color: '#909399' },
]

const sysLogs = [
  { id: 1, timestamp: '2026-08-18 14:30', version: 'v1.2.0', content: '新增 MCP-SSE 网关，优化审计日志查询性能', type: 'primary' as const },
  { id: 2, timestamp: '2026-08-15 10:12', version: 'v1.1.5', content: '修复角色管理页面数据范围映射问题', type: 'success' as const },
  { id: 3, timestamp: '2026-08-12 09:00', version: 'v1.1.0', content: '新增插件市场，支持进程内插件扫描', type: 'success' as const },
  { id: 4, timestamp: '2026-08-08 16:45', version: 'v1.0.3', content: '修复登录页 CSRF 校验异常', type: 'warning' as const },
  { id: 5, timestamp: '2026-08-01 08:00', version: 'v1.0.0', content: 'ApeAdmin 正式发布，初始版本上线', type: 'primary' as const },
]

const userLogs = [
  { id: 1, timestamp: '刚刚', user: 'admin', action: '登录系统', type: 'primary' as const },
  { id: 2, timestamp: '10分钟前', user: '张三', action: '修改了角色权限', type: 'warning' as const },
  { id: 3, timestamp: '30分钟前', user: '李四', action: '导出了审计日志', type: 'success' as const },
  { id: 4, timestamp: '1小时前', user: '王五', action: '删除了过期插件', type: 'danger' as const },
  { id: 5, timestamp: '2小时前', user: '赵六', action: '更新了系统配置', type: 'info' as const },
]
</script>
