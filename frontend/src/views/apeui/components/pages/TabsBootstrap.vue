<template>
  <div>
    <PageHeader title="Tabs Bootstrap Style" :breadcrumb="['APEUI库', 'Components', 'Tabs Bootstrap']" />

    <el-card shadow="hover" header="Basic Tabs (default style)" style="margin-bottom: 16px">
      <el-tabs v-model="activeName1">
        <el-tab-pane label="Dashboard" name="dashboard">Dashboard content goes here.</el-tab-pane>
        <el-tab-pane label="Analytics" name="analytics">Analytics content goes here.</el-tab-pane>
        <el-tab-pane label="Reports" name="reports">Reports content goes here.</el-tab-pane>
        <el-tab-pane label="Settings" name="settings">Settings content goes here.</el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="hover" header="Card Tabs (type=&quot;card&quot;)" style="margin-bottom: 16px">
      <el-tabs v-model="activeName2" type="card">
        <el-tab-pane label="Overview" name="overview">Overview panel content.</el-tab-pane>
        <el-tab-pane label="Activity" name="activity">Activity panel content.</el-tab-pane>
        <el-tab-pane label="Users" name="users">Users panel content.</el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="hover" header="Border Card Tabs (type=&quot;border-card&quot;)" style="margin-bottom: 16px">
      <el-tabs v-model="activeName3" type="border-card">
        <el-tab-pane label="Overview" name="overview">Overview panel content inside a bordered card.</el-tab-pane>
        <el-tab-pane label="Activity" name="activity">Activity panel content.</el-tab-pane>
        <el-tab-pane label="Users" name="users">Users panel content.</el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="hover" header="With Icons">
      <el-tabs v-model="activeName4" type="card">
        <el-tab-pane name="dashboard">
          <template #label>
            <span class="tab-label"><el-icon><Odometer /></el-icon> Dashboard</span>
          </template>
          Dashboard content.
        </el-tab-pane>
        <el-tab-pane name="users">
          <template #label>
            <span class="tab-label"><el-icon><User /></el-icon> Users</span>
          </template>
          Users content.
        </el-tab-pane>
        <el-tab-pane name="settings">
          <template #label>
            <span class="tab-label"><el-icon><Setting /></el-icon> Settings</span>
          </template>
          Settings content.
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Odometer, User, Setting } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const activeName1 = ref('dashboard')
const activeName2 = ref('overview')
const activeName3 = ref('overview')
const activeName4 = ref('dashboard')
</script>

<style scoped>
.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
</style>