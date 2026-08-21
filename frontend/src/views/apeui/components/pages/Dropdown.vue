<template>
  <div>
    <PageHeader title="下拉菜单" :breadcrumb="['APEUI库', '组件示例', '下拉菜单']" />

    <el-card shadow="hover" header="基础下拉" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-dropdown @command="handleCommand">
          <el-button type="primary">
            操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="create">创建</el-dropdown-item>
              <el-dropdown-item command="edit">编辑</el-dropdown-item>
              <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
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

    <el-card shadow="hover" header="带图标与描述" style="margin-bottom: 16px">
      <el-dropdown trigger="click">
        <span class="dropdown-link">
          Hover to expand
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item :icon="Plus">创建</el-dropdown-item>
            <el-dropdown-item :icon="Edit">编辑</el-dropdown-item>
            <el-dropdown-item :icon="Download">Download</el-dropdown-item>
            <el-dropdown-item :icon="Delete" divided>删除</el-dropdown-item>
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
                  <div style="font-weight: 600">资料</div>
                  <div style="font-size: 12px; color: #909399">管理您的账户信息</div>
                </div>
              </el-dropdown-item>
              <el-dropdown-item command="security">
                <div>
                  <div style="font-weight: 600">安全</div>
                  <div style="font-size: 12px; color: #909399">Password & 2FA</div>
                </div>
              </el-dropdown-item>
              <el-dropdown-item command="billing" divided>
                <div>
                  <div style="font-weight: 600">账单</div>
                  <div style="font-size: 12px; color: #909399">Plans & invoices</div>
                </div>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-card>

    <el-card shadow="hover" header="触发方式" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-dropdown trigger="hover">
          <el-button>Hover Trigger<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>项目 A</el-dropdown-item>
              <el-dropdown-item>项目 B</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-dropdown trigger="click">
          <el-button>Click Trigger<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>项目 A</el-dropdown-item>
              <el-dropdown-item>项目 B</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-dropdown trigger="contextmenu">
          <el-button>Right-Click Trigger<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>项目 A</el-dropdown-item>
              <el-dropdown-item>项目 B</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-card>

    <el-card shadow="hover" header="嵌套/多级下拉">
      <el-dropdown trigger="click">
        <el-button type="primary">
          Multi-Level Menu
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="dashboard">看板</el-dropdown-item>
            <el-dropdown-item command="projects">项目</el-dropdown-item>
            <el-dropdown-item divided command="reports">报表</el-dropdown-item>
            <el-dropdown-item command="analytics">分析</el-dropdown-item>
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
  ElMessage.info('拆分按钮主操作')
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