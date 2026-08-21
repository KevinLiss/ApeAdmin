<template>
  <div>
    <PageHeader title="日历" :breadcrumb="['APEUI库', '应用中心', '日历']" />

    <el-row :gutter="30">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="cal-header">
              <span class="card-title">月历视图</span>
              <div class="cal-nav">
                <el-button :icon="ArrowLeft" size="small" @click="prevMonth" />
                <span class="cal-month">{{ calTitle }}</span>
                <el-button :icon="ArrowRight" size="small" @click="nextMonth" />
                <el-button size="small" @click="goToday">今天</el-button>
              </div>
            </div>
          </template>
          <el-calendar v-model="currentDate">
            <template #header-title>
              <span style="display: none"></span>
            </template>
            <template #date-cell="{ data }">
              <div class="cal-cell" :class="{ today: data.isSelected }">
                <div class="cal-day">{{ data.day.split('-').slice(2).join('') }}</div>
                <div class="cal-dots" v-if="hasEvent(data.day)">
                  <span class="event-dot"></span>
                  <span class="event-count">{{ eventCount(data.day) }} 事件</span>
                </div>
              </div>
            </template>
          </el-calendar>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span class="card-title">{{ selectedDateLabel }} 事件</span>
          </template>
          <div class="event-list">
            <div v-for="evt in selectedEvents" :key="evt.id" class="event-item">
              <div class="event-time">{{ evt.time }}</div>
              <div class="event-info">
                <div class="event-title">{{ evt.title }}</div>
                <div class="event-desc">{{ evt.desc }}</div>
                <el-tag :type="eventTagType(evt.type)" size="small" effect="light">{{ evt.type }}</el-tag>
              </div>
            </div>
            <el-empty v-if="selectedEvents.length === 0" description="当日暂无事件" :image-size="80" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

interface CalEvent {
  id: number
  date: string
  time: string
  title: string
  desc: string
  type: string
}

const currentDate = ref(new Date())

const calTitle = computed(() => {
  const y = currentDate.value.getFullYear()
  const m = String(currentDate.value.getMonth() + 1).padStart(2, '0')
  return `${y} 年 ${m} 月`
})

const selectedDateStr = computed(() => {
  const y = currentDate.value.getFullYear()
  const m = String(currentDate.value.getMonth() + 1).padStart(2, '0')
  const d = String(currentDate.value.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
})

const selectedDateLabel = computed(() => {
  return selectedDateStr.value
})

const events: CalEvent[] = [
  { id: 1, date: '', time: '09:00', title: '晨会同步', desc: '团队每日站会，汇报进度与阻塞', type: '工作' },
  { id: 2, date: '', time: '14:00', title: '需求评审', desc: '用户管理模块需求评审会议', type: '会议' },
  { id: 3, date: '', time: '16:30', title: '代码审查', desc: '权限系统重构 PR 审查', type: '工作' },
  { id: 4, date: '', time: '10:00', title: '客户演示', desc: '向客户演示 V3 UI 原型', type: '会议' },
  { id: 5, date: '', time: '15:00', title: '技术分享', desc: '前端架构演进与最佳实践', type: '学习' },
  { id: 6, date: '', time: '11:00', title: '项目复盘', desc: '首页重构项目复盘总结', type: '工作' },
  { id: 7, date: '', time: '13:30', title: '数据库优化讨论', desc: '索引优化与慢查询排查', type: '工作' },
  { id: 8, date: '', time: '17:00', title: '周报整理', desc: '本周工作总结与下周计划', type: '工作' },
]

// 为当前月生成事件日期
const eventMap = computed<Record<string, CalEvent[]>>(() => {
  const y = currentDate.value.getFullYear()
  const m = currentDate.value.getMonth()
  const dates = [
    new Date(y, m, 8),
    new Date(y, m, 12),
    new Date(y, m, 18),
    new Date(y, m, 21),
  ]
  const fmt = (d: Date) => {
    const yy = d.getFullYear()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    return `${yy}-${mm}-${dd}`
  }
  const map: Record<string, CalEvent[]> = {}
  const groups = [
    [events[0], events[1], events[2]],
    [events[3], events[4]],
    [events[5], events[6]],
    [events[7]],
  ]
  dates.forEach((d, i) => {
    const key = fmt(d)
    groups[i].forEach((e) => (e.date = key))
    map[key] = groups[i]
  })
  return map
})

const hasEvent = (day: string) => !!eventMap.value[day]
const eventCount = (day: string) => eventMap.value[day]?.length || 0

const selectedEvents = computed(() => {
  return eventMap.value[selectedDateStr.value] || []
})

const eventTagType = (type: string) => {
  const map: Record<string, string> = {
    工作: 'primary',
    会议: 'warning',
    学习: 'success',
  }
  return map[type] || 'info'
}

const prevMonth = () => {
  const d = new Date(currentDate.value)
  d.setMonth(d.getMonth() - 1)
  currentDate.value = d
}

const nextMonth = () => {
  const d = new Date(currentDate.value)
  d.setMonth(d.getMonth() + 1)
  currentDate.value = d
}

const goToday = () => {
  currentDate.value = new Date()
}
</script>

<style scoped>
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #5A67F5;
}

.cal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cal-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cal-month {
  font-size: 15px;
  font-weight: 500;
  min-width: 100px;
  text-align: center;
}

.cal-cell {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 4px;
}

.cal-day {
  font-size: 14px;
  font-weight: 500;
}

.cal-dots {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 4px;
}

.event-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #5A67F5;
  display: inline-block;
}

.event-count {
  font-size: 11px;
  color: #5A67F5;
  margin-top: 2px;
}

.cal-cell.today .cal-day {
  color: #5A67F5;
  font-weight: 700;
}

.event-list {
  max-height: 600px;
  overflow-y: auto;
}

.event-item {
  display: flex;
  gap: 14px;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.event-item:last-child {
  border-bottom: none;
}

.event-time {
  font-size: 14px;
  font-weight: 600;
  color: #5A67F5;
  min-width: 50px;
  text-align: center;
  padding-top: 2px;
}

.event-info {
  flex: 1;
}

.event-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.event-desc {
  font-size: 13px;
  color: #888;
  margin-bottom: 8px;
  line-height: 1.4;
}

:deep(.el-calendar) {
  --el-calendar-selected-bg-color: #edeaf4;
}

:deep(.el-calendar-day:hover) {
  background: #f9f8fc;
}

:deep(.el-button--primary) {
  --el-color-primary: #5A67F5;
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}
</style>
