<template>
  <div>
    <PageHeader title="模态框" :breadcrumb="['APEUI库', '组件示例', '模态框']" />

    <el-card shadow="hover" header="基础对话框" style="margin-bottom: 16px">
      <el-button type="primary" @click="basicVisible = true">打开基础对话框</el-button>
      <el-dialog v-model="basicVisible" title="Basic Dialog" width="480px">
        <p>这是一个基础对话框。点击外部区域或按 ESC 键关闭。</p>
        <p style="color: #5a6273">这是用于演示的示例文本，仅用于展示对话框内的内容效果。</p>
        <template #footer>
          <el-button @click="basicVisible = false">取消</el-button>
          <el-button type="primary" @click="basicVisible = false">确认</el-button>
        </template>
      </el-dialog>
    </el-card>

    <el-card shadow="hover" header="对话框尺寸" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 12px">
        <el-button type="primary" @click="openSize('small')">小</el-button>
        <el-button type="primary" @click="openSize('medium')">中</el-button>
        <el-button type="primary" @click="openSize('large')">大</el-button>
        <el-button type="primary" @click="openSize('fullscreen')">全屏</el-button>
      </div>
      <el-dialog v-model="sizeVisible" :title="`${sizeLabel} Dialog`" :width="sizeWidth" :fullscreen="isFullscreen">
        <p>This is a <strong>{{ sizeLabel }}</strong> dialog.</p>
        <p style="color: #5a6273">
          Fullscreen dialogs cover the entire viewport and are great for complex workflows like editing,
          previewing, or detailed configuration panels.
        </p>
        <template #footer>
          <el-button @click="sizeVisible = false">关闭</el-button>
        </template>
      </el-dialog>
    </el-card>

    <el-card shadow="hover" header="表单对话框" style="margin-bottom: 16px">
      <el-button type="primary" @click="formVisible = true">打开表单对话框</el-button>
      <el-dialog v-model="formVisible" title="User Form" width="520px" @close="resetForm">
        <el-form ref="userFormRef" :model="userForm" label-width="90px">
          <el-form-item label="Username" required>
            <el-input v-model="userForm.name" placeholder="Please enter username" />
          </el-form-item>
          <el-form-item label="Email" required>
            <el-input v-model="userForm.email" placeholder="Please enter email" />
          </el-form-item>
          <el-form-item label="Role">
            <el-select v-model="userForm.role" placeholder="Select role" style="width: 100%">
              <el-option label="Admin" value="admin" />
              <el-option label="Editor" value="editor" />
              <el-option label="Viewer" value="viewer" />
            </el-select>
          </el-form-item>
          <el-form-item label="Status">
            <el-switch v-model="userForm.active" active-text="Active" inactive-text="Disabled" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="formVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">提交</el-button>
        </template>
      </el-dialog>
    </el-card>

    <el-card shadow="hover" header="嵌套对话框">
      <el-button type="primary" @click="outerVisible = true">打开外层对话框</el-button>
      <el-dialog v-model="outerVisible" title="Outer Dialog" width="600px" append-to-body>
        <p>This is the outer dialog. Open the inner dialog below.</p>
        <div style="margin-top: 16px">
          <el-button type="primary" @click="innerVisible = true">打开内层对话框</el-button>
        </div>
        <el-dialog v-model="innerVisible" title="Inner Dialog" width="400px" append-to-body>
          <p>This is the inner (nested) dialog.</p>
          <template #footer>
            <el-button type="primary" @click="innerVisible = false">OK</el-button>
          </template>
        </el-dialog>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '../PageHeader.vue'

const basicVisible = ref(false)

const sizeVisible = ref(false)
const sizeLabel = ref('Small')
const sizeWidth = ref('30%')
const isFullscreen = ref(false)

const openSize = (size: string) => {
  sizeLabel.value = size.charAt(0).toUpperCase() + size.slice(1)
  isFullscreen.value = size === 'fullscreen'
  sizeWidth.value = size === 'small' ? '30%' : size === 'medium' ? '50%' : '70%'
  sizeVisible.value = true
}

const formVisible = ref(false)
const userFormRef = ref()
const userForm = ref({
  name: '',
  email: '',
  role: 'viewer',
  active: true,
})

const resetForm = () => {
  userForm.value = { name: '', email: '', role: 'viewer', active: true }
}

const submitForm = () => {
  if (!userForm.value.name || !userForm.value.email) {
    ElMessage.warning('请填写用户名和邮箱')
    return
  }
  ElMessage.success(`User "${userForm.value.name}" created successfully`)
  formVisible.value = false
}

const outerVisible = ref(false)
const innerVisible = ref(false)
</script>