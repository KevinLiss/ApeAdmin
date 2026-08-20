<template>
  <div>
    <PageHeader title="Tabs Line Style" :breadcrumb="['APEUI库', 'Components', 'Tabs Line']" />

    <el-card shadow="hover" header="Closable Tabs" style="margin-bottom: 16px">
      <el-tabs v-model="editableTabsValue" type="card" closable @tab-remove="removeTab" @tab-add="addTab">
        <el-tab-pane v-for="item in editableTabs" :key="item.name" :label="item.title" :name="item.name">
          Content of {{ item.title }}
        </el-tab-pane>
        <template #add>
          <el-icon><Plus /></el-icon>
        </template>
      </el-tabs>
    </el-card>

    <el-card shadow="hover" header="Custom Tab Labels" style="margin-bottom: 16px">
      <el-tabs v-model="customTab">
        <el-tab-pane name="inbox">
          <template #label>
            <span class="custom-label">
              <el-badge is-dot type="danger" style="display: inline-flex">
                <el-icon :size="16"><Message /></el-icon>
              </el-badge>
              Inbox
            </span>
          </template>
          Inbox content: unread messages show a dot badge.
        </el-tab-pane>
        <el-tab-pane name="sent">
          <template #label>
            <span class="custom-label">
              <el-icon :size="16"><Promotion /></el-icon>
              Sent
            </span>
          </template>
          Sent messages content.
        </el-tab-pane>
        <el-tab-pane name="drafts">
          <template #label>
            <span class="custom-label">
              <el-icon :size="16"><EditPen /></el-icon>
              Drafts
            </span>
          </template>
          Draft messages content.
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="hover" header="Left Position (position=&quot;left&quot;)" style="margin-bottom: 16px">
      <el-tabs tab-position="left" style="height: 220px">
        <el-tab-pane label="Overview">Overview content.</el-tab-pane>
        <el-tab-pane label="Analytics">Analytics content.</el-tab-pane>
        <el-tab-pane label="Settings">Settings content.</el-tab-pane>
        <el-tab-pane label="Logs">Logs content.</el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="never" header="Right Position (position=&quot;right&quot;)" style="margin-bottom: 16px">
      <el-tabs tab-position="right" style="height: 220px">
        <el-tab-pane label="Overview">Overview content.</el-tab-pane>
        <el-tab-pane label="Analytics">Analytics content.</el-tab-pane>
        <el-tab-pane label="Settings">Settings content.</el-tab-pane>
        <el-tab-pane label="Logs">Logs content.</el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="never" header="Bottom &amp; Top Position">
      <div style="margin-bottom: 24px">
        <strong style="color: #5a6273; font-size: 13px">Bottom:</strong>
        <el-tabs tab-position="bottom" style="height: 160px">
          <el-tab-pane label="Tab A">Content A.</el-tab-pane>
          <el-tab-pane label="Tab B">Content B.</el-tab-pane>
        </el-tabs>
      </div>
      <div>
        <strong style="color: #5a6273; font-size: 13px">Top (default):</strong>
        <el-tabs tab-position="top" style="height: 160px">
          <el-tab-pane label="Tab A">Content A.</el-tab-pane>
          <el-tab-pane label="Tab B">Content B.</el-tab-pane>
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
  { title: 'Tab 1', name: 'tab1' },
  { title: 'Tab 2', name: 'tab2' },
])
const editableTabsValue = ref('tab1')
const customTab = ref('inbox')
let tabIndex = 2

const addTab = () => {
  const newTabName = `tab${++tabIndex}`
  editableTabs.value.push({ title: `Tab ${tabIndex}`, name: newTabName })
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