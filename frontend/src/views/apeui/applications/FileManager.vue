<template>
  <div class="file-manager">
    <PageHeader title="File Manager" :breadcrumb="['APEUI库', 'Applications', 'File Manager']" />

    <el-row :gutter="30">
      <!-- Left: Folder Tree -->
      <el-col :xs="24" :sm="6">
        <div class="koho-card">
          <div class="card-title">
            <el-icon><FolderOpened /></el-icon>
            <span>Folders</span>
          </div>
          <el-tree
            :data="folderTree"
            :props="{ label: 'name', children: 'children' }"
            node-key="id"
            default-expand-all
            highlight-current
            @node-click="onFolderClick"
          />
        </div>
      </el-col>

      <!-- Right: File List -->
      <el-col :xs="24" :sm="18">
        <div class="koho-card">
          <!-- Toolbar -->
          <div class="toolbar">
            <div class="toolbar-left">
              <el-button type="primary" :icon="Upload" @click="onUpload">Upload</el-button>
              <el-button-group style="margin-left: 12px">
                <el-button :type="viewMode === 'grid' ? 'primary' : 'default'" @click="viewMode = 'grid'">
                  <el-icon><Grid /></el-icon>
                </el-button>
                <el-button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'">
                  <el-icon><List /></el-icon>
                </el-button>
              </el-button-group>
            </div>
            <div class="toolbar-right">
              <el-input
                v-model="searchText"
                placeholder="Search files..."
                :prefix-icon="Search"
                clearable
                style="width: 200px; margin-right: 12px"
              />
              <el-select v-model="sortBy" placeholder="Sort by" style="width: 140px">
                <el-option label="Name (A-Z)" value="name" />
                <el-option label="Size (Largest first)" value="size" />
                <el-option label="Date (Newest first)" value="date" />
              </el-select>
            </div>
          </div>

          <div class="current-folder">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item>Root</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentFolder }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <!-- Grid View -->
          <div v-if="viewMode === 'grid'" class="file-grid">
            <div v-for="file in filteredFiles" :key="file.id" class="file-card">
              <div class="file-icon" :style="{ background: file.iconBg, color: file.iconColor }">
                <el-icon :size="32"><component :is="file.icon" /></el-icon>
              </div>
              <div class="file-name" :title="file.name">{{ file.name }}</div>
              <div class="file-size">{{ file.size }}</div>
              <el-dropdown trigger="click" @command="onFileAction($event, file)">
                <el-button text :icon="MoreFilled" circle size="small" />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="download">Download</el-dropdown-item>
                    <el-dropdown-item command="rename">Rename</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>Delete</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <!-- List View -->
          <el-table v-else :data="filteredFiles" style="width: 100%" stripe>
            <el-table-column prop="name" label="File Name" min-width="200">
              <template #default="{ row }">
                <div class="table-file-name">
                  <el-icon :size="20" :style="{ color: row.iconColor }"><component :is="row.icon" /></el-icon>
                  <span>{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="size" label="Size" width="120" />
            <el-table-column prop="date" label="Modified Date" width="180" />
            <el-table-column prop="type" label="Type" width="100">
              <template #default="{ row }">
                <el-tag :type="row.tagType" size="small">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="180" align="center">
              <template #default="{ row }">
                <el-button text type="primary" :icon="Download" @click="onFileAction('download', row)" />
                <el-button text type="warning" :icon="Edit" @click="onFileAction('rename', row)" />
                <el-button text type="danger" :icon="Delete" @click="onFileAction('delete', row)" />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  FolderOpened, Grid, List, Search, Upload, MoreFilled,
  Download, Edit, Delete, Document, Picture, VideoPlay, Files, Folder,
} from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

const viewMode = ref<'grid' | 'list'>('grid')
const searchText = ref('')
const sortBy = ref('name')
const currentFolder = ref('Documents')

const folderTree = [
  {
    id: 1, name: 'Documents',
    children: [
      { id: 11, name: 'Reports' },
      { id: 12, name: 'Invoices' },
      { id: 13, name: 'Contracts' },
    ],
  },
  {
    id: 2, name: 'Images',
    children: [
      { id: 21, name: 'Photos' },
      { id: 22, name: 'Screenshots' },
    ],
  },
  { id: 3, name: 'Videos' },
  { id: 4, name: 'Downloads' },
]

const files = ref([
  { id: 1, name: 'Annual Report 2025.pdf', size: '2.4 MB', date: '2025-08-15', type: 'PDF', icon: Document, iconBg: '#fef0e6', iconColor: '#E56809', tagType: 'warning' as const },
  { id: 2, name: 'Q3 Invoice.xlsx', size: '1.2 MB', date: '2025-08-12', type: 'Excel', icon: Files, iconBg: '#e8f5e9', iconColor: '#67C100', tagType: 'success' as const },
  { id: 3, name: 'Service Contract.docx', size: '856 KB', date: '2025-08-10', type: 'Word', icon: Document, iconBg: '#e3f2fd', iconColor: '#3EBCB9', tagType: 'info' as const },
  { id: 4, name: 'Profile Photo.jpg', size: '3.8 MB', date: '2025-08-08', type: 'Image', icon: Picture, iconBg: '#EAF1FF', iconColor: '#5A67F5', tagType: 'primary' as const },
  { id: 5, name: 'Dashboard Screenshot.png', size: '1.6 MB', date: '2025-08-06', type: 'Image', icon: Picture, iconBg: '#EAF1FF', iconColor: '#5A67F5', tagType: 'primary' as const },
  { id: 6, name: 'Product Demo.mp4', size: '124 MB', date: '2025-08-03', type: 'Video', icon: VideoPlay, iconBg: '#ffe0e0', iconColor: '#DC0808', tagType: 'danger' as const },
  { id: 7, name: 'Backup Archive.zip', size: '45 MB', date: '2025-07-28', type: 'Archive', icon: Files, iconBg: '#fff3e0', iconColor: '#E56809', tagType: 'warning' as const },
  { id: 8, name: 'Budget Plan.xlsx', size: '780 KB', date: '2025-07-25', type: 'Excel', icon: Files, iconBg: '#e8f5e9', iconColor: '#67C100', tagType: 'success' as const },
])

const filteredFiles = computed(() => {
  let result = files.value
  if (searchText.value) {
    result = result.filter(f => f.name.toLowerCase().includes(searchText.value.toLowerCase()))
  }
  if (sortBy.value === 'name') {
    result = [...result].sort((a, b) => a.name.localeCompare(b.name))
  } else if (sortBy.value === 'size') {
    result = [...result].sort((a, b) => parseFloat(b.size) - parseFloat(a.size))
  } else if (sortBy.value === 'date') {
    result = [...result].sort((a, b) => b.date.localeCompare(a.date))
  }
  return result
})

const onFolderClick = (data: any) => {
  currentFolder.value = data.name
}

const onUpload = () => {
  ElMessage.success('Upload dialog opened')
}

const onFileAction = (command: string, file: any) => {
  if (command === 'download') ElMessage.success(`Downloading ${file.name}`)
  else if (command === 'rename') ElMessage.info(`Renaming ${file.name}`)
  else if (command === 'delete') ElMessage.warning(`Deleted ${file.name}`)
}
</script>

<style scoped>
.koho-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 0 20px rgba(8, 21, 66, 0.05);
  margin-bottom: 30px;
  height: 100%;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 500;
  color: #5A67F5;
  margin-bottom: 16px;
}
.card-title .el-icon { font-size: 20px; }

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
}
.current-folder {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}
.file-card {
  position: relative;
  text-align: center;
  padding: 20px 12px;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  transition: all 0.25s;
}
.file-card:hover {
  border-color: #5A67F5;
  box-shadow: 0 4px 16px rgba(90, 103, 245, 0.12);
}
.file-card .el-button {
  position: absolute;
  top: 8px;
  right: 8px;
}
.file-icon {
  width: 64px;
  height: 64px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}
.file-name {
  font-size: 13px;
  font-weight: 500;
  color: #2b2b2b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}
.file-size {
  font-size: 12px;
  color: #909399;
}

.table-file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-button--primary) {
  --el-color-primary: #5A67F5;
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
}
:deep(.el-tree-node__content:hover) {
  background-color: rgba(90, 103, 245, 0.08);
}
:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: rgba(90, 103, 245, 0.14);
}
:deep(.el-tree-node.is-current > .el-tree-node__content .el-tree-node__label) {
  color: #5A67F5;
  font-weight: 500;
}
:deep(.el-breadcrumb__inner) {
  color: #5A67F5;
  font-weight: 500;
}
</style>
