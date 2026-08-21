<template>
  <div>
    <PageHeader title="Dropdown" :breadcrumb="['APEUI库', 'Components', 'Dropdown']" />

    <el-card shadow="hover" header="Basic Dropdown" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-dropdown @command="handleCommand">
          <el-button type="primary">
            Actions<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="create">Create</el-dropdown-item>
              <el-dropdown-item command="edit">Edit</el-dropdown-item>
              <el-dropdown-item command="delete" divided>Delete</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-dropdown>
          <el-button>Plain Dropdown<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>Option 1</el-dropdown-item>
              <el-dropdown-item>Option 2</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-dropdown split-button type="primary" @click="onSplitMain" @command="handleCommand">
          Split Button
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="view">View</el-dropdown-item>
              <el-dropdown-item command="export">Export</el-dropdown-item>
              <el-dropdown-item command="archive" disabled>Archive (disabled)</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-card>

    <el-card shadow="hover" header="With Icons & Description" style="margin-bottom: 16px">
      <el-dropdown trigger="click">
        <span class="dropdown-link">
          Hover to expand
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item :icon="Plus">Create</el-dropdown-item>
            <el-dropdown-item :icon="Edit">Edit</el-dropdown-item>
            <el-dropdown-item :icon="Download">Download</el-dropdown-item>
            <el-dropdown-item :icon="Delete" divided>Delete</el-dropdown-item>
            <el-dropdown-item :icon="Setting" disabled>Settings (disabled)</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <div style="margin-top: 16px">
        <el-dropdown trigger="click">
          <el-button type="primary">With Descriptions<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <div>
                  <div style="font-weight: 600">Profile</div>
                  <div style="font-size: 12px; color: #909399">Manage your account info</div>
                </div>
              </el-dropdown-item>
              <el-dropdown-item command="security">
                <div>
                  <div style="font-weight: 600">Security</div>
                  <div style="font-size: 12px; color: #909399">Password & 2FA</div>
                </div>
              </el-dropdown-item>
              <el-dropdown-item command="billing" divided>
                <div>
                  <div style="font-weight: 600">Billing</div>
                  <div style="font-size: 12px; color: #909399">Plans & invoices</div>
                </div>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-card>

    <el-card shadow="hover" header="Trigger Types" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-dropdown trigger="hover">
          <el-button>Hover Trigger<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>Item A</el-dropdown-item>
              <el-dropdown-item>Item B</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-dropdown trigger="click">
          <el-button>Click Trigger<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>Item A</el-dropdown-item>
              <el-dropdown-item>Item B</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-dropdown trigger="contextmenu">
          <el-button>Right-Click Trigger<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>Item A</el-dropdown-item>
              <el-dropdown-item>Item B</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-card>

    <el-card shadow="hover" header="Nested / Multi-level Dropdown">
      <el-dropdown trigger="click">
        <el-button type="primary">
          Multi-Level Menu
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="dashboard">Dashboard</el-dropdown-item>
            <el-dropdown-item command="projects">Projects</el-dropdown-item>
            <el-dropdown-item divided command="reports">Reports</el-dropdown-item>
            <el-dropdown-item command="analytics">Analytics</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      <span style="color: #909399; font-size: 13px; margin-left: 12px">多级下拉通过 el-dropdown-item 分组 + command 路由实现；深层嵌套可用 el-menu 的 el-sub-menu。</span>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ArrowDown, Plus, View, Edit, Download, Delete, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '../PageHeader.vue'

const handleCommand = (command: string) => {
  ElMessage.info(`Command: ${command}`)
}

const handleSplitMain = () => {
  ElMessage.info('Split button main action')
}
</script>

<style scoped>
.dropdown-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #5A67F5;
  font-weight: 600;
  cursor: pointer;
  outline: none;
}
</style>