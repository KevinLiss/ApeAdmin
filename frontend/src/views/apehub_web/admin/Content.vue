<template>
  <div class="content-admin">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card total">
        <div class="stat-icon">📝</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">内容块总数</div>
        </div>
      </div>
      <div class="stat-card active">
        <div class="stat-icon">✅</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.enabled }}</div>
          <div class="stat-label">已启用</div>
        </div>
      </div>
      <div class="stat-card disabled">
        <div class="stat-icon">⛔</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.disabled }}</div>
          <div class="stat-label">已禁用</div>
        </div>
      </div>
    </div>

    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>内容管理</span>
          <el-button type="primary" size="small" @click="openDialog()">新增内容块</el-button>
        </div>
      </template>

      <el-table :data="contentList" v-loading="loading" stripe>
        <el-table-column prop="block_key" label="区块标识" width="130">
          <template #default="{ row }">
            <span class="block-key-tag">{{ row.block_key }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="160" />
        <el-table-column prop="subtitle" label="副标题" min-width="160" show-overflow-tooltip />
        <el-table-column prop="sort" label="排序" width="70" align="center" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small" effect="light" round>{{ row.enabled ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" text type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="暂无内容" /></template>
      </el-table>

      <!-- 编辑弹窗 -->
      <el-dialog v-model="dialogVisible" :title="editing.id ? '编辑内容块' : '新增内容块'" width="640px" destroy-on-close>
        <div class="dialog-body">
          <div class="dialog-hint">
            <el-icon><InfoFilled /></el-icon>
            <span>内容块用于官网各区块的动态展示（Hero 区、特性区、页脚等）。</span>
          </div>
          <el-form :model="editing" label-position="top">
            <el-form-item label="区块标识">
              <el-input v-model="editing.block_key" placeholder="hero / features / footer 等" />
            </el-form-item>
            <el-form-item label="标题">
              <el-input v-model="editing.title" placeholder="区块标题" />
            </el-form-item>
            <el-form-item label="副标题">
              <el-input v-model="editing.subtitle" placeholder="区块副标题" />
            </el-form-item>
            <el-form-item label="正文">
              <el-input v-model="editing.body" type="textarea" :rows="4" placeholder="支持 Markdown" />
            </el-form-item>
            <el-form-item label="图片 URL">
              <el-input v-model="editing.image" placeholder="区块配图地址" />
            </el-form-item>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="排序">
                  <el-input-number v-model="editing.sort" :min="0" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="启用状态">
                  <el-switch v-model="editing.enabled" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { getAdminContent, createAdminContent, updateAdminContent, deleteAdminContent } from '@/api/apehub_web'

const contentList = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)

const editing = ref<any>({
  block_key: '', title: '', subtitle: '', body: '', image: '', sort: 0, enabled: true,
})

const stats = computed(() => {
  const total = contentList.value.length
  const enabled = contentList.value.filter(c => c.enabled).length
  return { total, enabled, disabled: total - enabled }
})

const loadList = async () => {
  loading.value = true
  try { contentList.value = await getAdminContent() } finally { loading.value = false }
}

const openDialog = (row?: any) => {
  if (row) {
    editing.value = { ...row }
  } else {
    editing.value = { block_key: '', title: '', subtitle: '', body: '', image: '', sort: 0, enabled: true }
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    if (editing.value.id) {
      await updateAdminContent(editing.value.id, editing.value)
    } else {
      await createAdminContent(editing.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadList()
  } finally { saving.value = false }
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm('确认删除该内容块？', '提示', { type: 'warning' })
  await deleteAdminContent(row.id)
  ElMessage.success('已删除')
  loadList()
}

onMounted(loadList)
</script>

<style scoped>
.stats-row { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.stat-card {
  display: flex; align-items: center; gap: 14px;
  padding: 18px 24px; border-radius: 12px;
  background: var(--el-fill-color-lighter);
  border: 1px solid var(--el-border-color-lighter);
  min-width: 160px; flex: 1; transition: all 0.2s;
}
.stat-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.stat-icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.stat-card.total .stat-icon { background: #e6f0ff; }
.stat-card.active .stat-icon { background: #e8f5e9; }
.stat-card.disabled .stat-icon { background: #f0f0f0; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--el-text-color-primary); }
.stat-label { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 2px; }

.card-header { display: flex; justify-content: space-between; align-items: center; }

.block-key-tag {
  font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px;
  padding: 2px 8px; border-radius: 6px; background: var(--el-fill-color-light);
  color: var(--el-color-primary);
}

.dialog-body { padding: 4px 0; }
.dialog-hint {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 12px 14px; margin-bottom: 16px;
  background: #e6f4ec; border-radius: 8px; font-size: 13px; color: #2e7d32;
}
.dialog-hint .el-icon { margin-top: 1px; flex-shrink: 0; }
</style>
