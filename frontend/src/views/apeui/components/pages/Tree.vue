<template>
  <div class="apeui-page">
    <PageHeader title="Tree View" breadcrumb="Components / Tree View" />
    <el-card shadow="never" class="apeui-card">
      <template #header>
        <div class="card-header">
          <span>Tree View</span>
        </div>
      </template>
      <el-tree
        :data="treeData"
        :props="defaultProps"
        show-checkbox
        node-key="id"
        default-expand-all
        highlight-current
        @node-click="handleNodeClick"
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <el-icon v-if="data.children" size="14"><Folder /></el-icon>
            <el-icon v-else size="14"><Document /></el-icon>
            <span style="margin-left: 4px">{{ node.label }}</span>
          </span>
        </template>
      </el-tree>

      <el-divider />

      <h4>Tree with Context Menu (Right Click)</h4>
      <el-tree
        :data="treeData"
        :props="defaultProps"
        node-key="id"
        default-expand-all
        @node-contextmenu="handleContextMenu"
      />

      <!-- Context Menu -->
      <div
        v-show="contextMenu.visible"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
        class="context-menu"
      >
        <div class="context-item" @click="handleContextAction('add')">Add Child</div>
        <div class="context-item" @click="handleContextAction('edit')">Edit</div>
        <div class="context-item" @click="handleContextAction('delete')">Delete</div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { Folder, Document } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

interface TreeNode {
  id: number
  label: string
  children?: TreeNode[]
}

const treeData: TreeNode[] = [
  {
    id: 1,
    label: 'Main Directory',
    children: [
      {
        id: 2,
        label: 'Sub Directory 1',
        children: [
          { id: 5, label: 'File 1-1' },
          { id: 6, label: 'File 1-2' },
        ],
      },
      {
        id: 3,
        label: 'Sub Directory 2',
        children: [
          { id: 7, label: 'File 2-1' },
          { id: 8, label: 'File 2-2' },
        ],
      },
      { id: 4, label: 'File Root' },
    ],
  },
]

const defaultProps = {
  children: 'children',
  label: 'label',
}

const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
})

const handleNodeClick = (data: TreeNode) => {
  console.log('Node clicked:', data)
}

const handleContextMenu = (_e: MouseEvent, _data: TreeNode, _node: any) => {
  contextMenu.visible = true
  contextMenu.x = _e.clientX
  contextMenu.y = _e.clientY
}

const handleContextAction = (action: string) => {
  console.log('Context action:', action)
  contextMenu.visible = false
}

// Close context menu on click elsewhere
document.addEventListener('click', () => {
  contextMenu.visible = false
})
</script>

<style scoped>
.tree-node {
  display: flex;
  align-items: center;
}

.context-menu {
  position: fixed;
  z-index: 9999;
  background: #fff;
  border: 1px solid var(--el-border-color, #dcdfe6);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  padding: 4px 0;
}

.context-item {
  padding: 6px 16px;
  cursor: pointer;
  font-size: 14px;
}

.context-item:hover {
  background: var(--el-color-primary-light-9, #f5f7fa);
  color: var(--el-color-primary, #534686);
}
</style>
