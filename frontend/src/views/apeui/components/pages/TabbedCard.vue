<template>
  <div>
    <PageHeader title="Tabbed Card" :breadcrumb="['APEUI库', 'Components', 'Tabbed Card']" />

    <el-card shadow="hover" style="margin-bottom: 16px">
      <template #header>
        <span style="font-weight: 600; color: #534686">用户管理</span>
      </template>
      <el-tabs v-model="activeTab1" type="card">
        <el-tab-pane label="全部用户" name="all">
          <el-table :data="users" style="width: 100%">
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="role" label="角色" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === '在线' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="在线用户" name="online">
          <el-table :data="users.filter(u => u.status === '在线')" style="width: 100%">
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="role" label="角色" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="离线用户" name="offline">
          <el-table :data="users.filter(u => u.status === '离线')" style="width: 100%">
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="role" label="角色" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span style="font-weight: 600; color: #534686">系统日志</span>
          </template>
          <el-tabs v-model="activeTab2" type="border-card">
            <el-tab-pane label="Info" name="info">
              <div class="log-list">
                <div class="log-item" v-for="log in logsInfo" :key="log.time">
                  <span class="log-time">{{ log.time }}</span>
                  <el-tag type="info" size="small">INFO</el-tag>
                  <span>{{ log.msg }}</span>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="Warning" name="warning">
              <div class="log-list">
                <div class="log-item" v-for="log in logsWarn" :key="log.time">
                  <span class="log-time">{{ log.time }}</span>
                  <el-tag type="warning" size="small">WARN</el-tag>
                  <span>{{ log.msg }}</span>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="Error" name="error">
              <div class="log-list">
                <div class="log-item" v-for="log in logsError" :key="log.time">
                  <span class="log-time">{{ log.time }}</span>
                  <el-tag type="danger" size="small">ERROR</el-tag>
                  <span>{{ log.msg }}</span>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span style="font-weight: 600; color: #534686">数据统计</span>
          </template>
          <el-tabs v-model="activeTab3" type="line">
            <el-tab-pane label="今日" name="today">
              <div class="stat-block">
                <div class="stat-item">
                  <div class="stat-num" style="color: #534686">1,248</div>
                  <div class="stat-label">访问量</div>
                </div>
                <div class="stat-item">
                  <div class="stat-num" style="color: #67C100">326</div>
                  <div class="stat-label">新增用户</div>
                </div>
                <div class="stat-item">
                  <div class="stat-num" style="color: #E56809">89</div>
                  <div class="stat-label">订单数</div>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="本周" name="week">
              <div class="stat-block">
                <div class="stat-item">
                  <div class="stat-num" style="color: #534686">8,920</div>
                  <div class="stat-label">访问量</div>
                </div>
                <div class="stat-item">
                  <div class="stat-num" style="color: #67C100">2,105</div>
                  <div class="stat-label">新增用户</div>
                </div>
                <div class="stat-item">
                  <div class="stat-num" style="color: #E56809">612</div>
                  <div class="stat-label">订单数</div>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="本月" name="month">
              <div class="stat-block">
                <div class="stat-item">
                  <div class="stat-num" style="color: #534686">35,640</div>
                  <div class="stat-label">访问量</div>
                </div>
                <div class="stat-item">
                  <div class="stat-num" style="color: #67C100">9,872</div>
                  <div class="stat-label">新增用户</div>
                </div>
                <div class="stat-item">
                  <div class="stat-num" style="color: #E56809">2,430</div>
                  <div class="stat-label">订单数</div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover">
      <template #header>
        <span style="font-weight: 600; color: #534686">可关闭标签页</span>
      </template>
      <el-tabs v-model="activeTab4" type="card" closable @tab-remove="handleRemove">
        <el-tab-pane
          v-for="tab in closableTabs"
          :key="tab.name"
          :label="tab.label"
          :name="tab.name"
          :closable="tab.closable"
        >
          <p style="margin: 0; color: #5a6273">{{ tab.content }}</p>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '../PageHeader.vue'

const activeTab1 = ref('all')
const activeTab2 = ref('info')
const activeTab3 = ref('today')
const activeTab4 = ref('tab1')

const users = [
  { name: '张三', role: '管理员', status: '在线' },
  { name: '李四', role: '编辑', status: '在线' },
  { name: '王五', role: '访客', status: '离线' },
  { name: '赵六', role: '编辑', status: '离线' },
]

const logsInfo = [
  { time: '08:30:12', msg: '系统启动完成' },
  { time: '09:15:33', msg: '用户 admin 登录' },
  { time: '10:02:07', msg: '数据备份完成' },
]
const logsWarn = [
  { time: '11:20:45', msg: 'CPU 使用率超过 80%' },
  { time: '13:05:10', msg: '磁盘剩余空间不足 15%' },
]
const logsError = [
  { time: '14:30:22', msg: '数据库连接超时' },
  { time: '15:10:08', msg: 'API 接口返回 500 错误' },
]

const closableTabs = ref([
  { label: '首页', name: 'tab1', content: '首页内容：欢迎来到 ApeAdmin 管理系统。', closable: false },
  { label: '用户列表', name: 'tab2', content: '用户列表：共 1,248 名注册用户。', closable: true },
  { label: '系统设置', name: 'tab3', content: '系统设置：配置全局参数。', closable: true },
  { label: '审计日志', name: 'tab4', content: '审计日志：查看操作记录。', closable: true },
])

const handleRemove = (name: string) => {
  closableTabs.value = closableTabs.value.filter(t => t.name !== name)
}
</script>

<style scoped>
.log-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #5a6273;
}
.log-time {
  color: #909399;
  font-family: monospace;
  white-space: nowrap;
}
.stat-block {
  display: flex;
  justify-content: space-around;
  padding: 12px 0;
}
.stat-item {
  text-align: center;
}
.stat-num {
  font-size: 28px;
  font-weight: 800;
  line-height: 1.2;
}
.stat-label {
  color: #909399;
  font-size: 13px;
  margin-top: 4px;
}
</style>
