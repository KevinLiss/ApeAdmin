<template>
  <div>
    <PageHeader title="线型标签页" :breadcrumb="['APEUI库', '组件示例', '线型标签页']" />

    <el-card shadow="hover" header="可关闭标签页" style="margin-bottom: 16px">
      <el-tabs v-model="editableTabsValue" type="card" closable @tab-remove="removeTab" @tab-add="addTab">
        <el-tab-pane v-for="item in editableTabs" :key="item.name" :label="item.title" :name="item.name">
          {{ item.title }}的内容
        </el-tab-pane>
        <template #add>
          <el-icon><Plus /></el-icon>
        </template>
      </el-tabs>
    </el-card>

    <el-card shadow="hover" header="自定义标签文字" style="margin-bottom: 16px">
      <el-tabs v-model="customTab">
        <el-tab-pane name="inbox">
          <template #label>
            <span class="custom-label">
              <el-badge is-dot type="danger" style="display: inline-flex">
                <el-icon :size="16"><Message /></el-icon>
              </el-badge>
              收件箱
            </span>
          </template>
          收件箱内容：未读消息以圆点徽章显示。
        </el-tab-pane>
        <el-tab-pane name="sent">
          <template #label>
            <span class="custom-label">
              <el-icon :size="16"><Promotion /></el-icon>
              已发送
            </span>
          </template>
          已发送消息内容。
        </el-tab-pane>
        <el-tab-pane name="drafts">
          <template #label>
            <span class="custom-label">
              <el-icon :size="16"><EditPen /></el-icon>
              Drafts
            </span>
          </template>
          草稿消息内容。
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="hover" header="左侧位置（position=left）" style="margin-bottom: 16px">
      <el-tabs tab-position="left" style="height: 220px">
        <el-tab-pane label="概览">概览内容。</el-tab-pane>
        <el-tab-pane label="分析">分析内容。</el-tab-pane>
        <el-tab-pane label="设置">设置内容。</el-tab-pane>
        <el-tab-pane label="日志">日志内容。</el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="never" header="右侧位置（position=right）" style="margin-bottom: 16px">
      <el-tabs tab-position="right" style="height: 220px">
        <el-tab-pane label="概览">概览内容。</el-tab-pane>
        <el-tab-pane label="分析">分析内容。</el-tab-pane>
        <el-tab-pane label="设置">设置内容。</el-tab-pane>
        <el-tab-pane label="日志">日志内容。</el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="never" header="底部与顶部位置">
      <div style="margin-bottom: 24px">
        <strong style="color: #5a6273; font-size: 13px">底部位置：</strong>
        <el-tabs tab-position="bottom" style="height: 160px">
          <el-tab-pane label="标签A">内容A。</el-tab-pane>
          <el-tab-pane label="标签B">内容B。</el-tab-pane>
        </el-tabs>
      </div>
      <div>
        <strong style="color: #5a6273; font-size: 13px">顶部位置（默认）：</strong>
        <el-tabs tab-position="top" style="height: 160px">
          <el-tab-pane label="标签A">内容A。</el-tab-pane>
          <el-tab-pane label="标签B">内容B。</el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus, Message, Promotion, EditPen } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const editableTabs = ref([
  { title: '标签页 1', name: 'tab1' },
  { title: '标签页 2', name: 'tab2' },
])
const editableTabsValue = ref('tab1')
const customTab = ref('inbox')
let tabIndex = 2

const addTab = () => {
  const newTabName = `tab${++tabIndex}`
  editableTabs.value.push({ title: `标签页 ${tabIndex}`, name: newTabName })
  editableTabsValue.value = newTabName
}

const removeTab = (name: string) => {
  const tabs = editableTabs.value
  let activeName = editableTabsValue.value
  if (activeName === name) {
    tabs.forEach((tab, index) => {
      if (tab.name === name) {
        const nextTab = tabs[index + 1] || tabs[index - 1]
        if (nextTab) activeName = nextTab.name
      }
    })
  }
  editableTabsValue.value = activeName
  editableTabs.value = tabs.filter((tab) => tab.name !== name)
}
</script>

<style scoped>
.custom-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
</style>