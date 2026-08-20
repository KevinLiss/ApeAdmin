<template>
  <div>
    <PageHeader title="Modal / Dialog" :breadcrumb="['APEUI库', 'Components', 'Modal']" />

    <el-card shadow="hover" header="Basic Dialog" style="margin-bottom: 16px">
      <el-button type="primary" @click="basicVisible = true">Open Basic Dialog</el-button>
      <el-dialog v-model="basicVisible" title="Basic Dialog" width="480px">
        <p>This is a basic dialog. Click outside or press ESC to close.</p>
        <p style="color: #5a6273">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
        <template #footer>
          <el-button @click="basicVisible = false">Cancel</el-button>
          <el-button type="primary" @click="basicVisible = false">Confirm</el-button>
        </template>
      </el-dialog>
    </el-card>

    <el-card shadow="hover" header="Dialog Sizes" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 12px">
        <el-button type="primary" @click="openSize('small')">Small</el-button>
        <el-button type="primary" @click="openSize('medium')">Medium</el-button>
        <el-button type="primary" @click="openSize('large')">Large</el-button>
        <el-button type="primary" @click="openSize('fullscreen')">Fullscreen</el-button>
      </div>
      <el-dialog v-model="sizeVisible" :title="`${sizeLabel} Dialog`" :width="sizeWidth" :fullscreen="isFullscreen">
        <p>This is a <strong>{{ sizeLabel }}</strong> dialog.</p>
        <p style="color: #5a6273">
          Fullscreen dialogs cover the entire viewport and are great for complex workflows like editing,
          previewing, or detailed configuration panels.
        </p>
        <template #footer>
          <el-button @click="sizeVisible = false">Close</el-button>
        </template>
      </el-dialog>
    </el-card>

    <el-card shadow="hover" header="Dialog with Form" style="margin-bottom: 16px">
      <el-button type="primary" @click="formVisible = true">Open Form Dialog</el-button>
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
          <el-button @click="formVisible = false">Cancel</el-button>
          <el-button type="primary" @click="submitForm">Submit</el-button>
        </template>
      </el-dialog>
    </el-card>

    <el-card shadow="hover" header="Nested Dialog">
      <el-button type="primary" @click="outerVisible = true">Open Outer Dialog</el-button>
      <el-dialog v-model="outerVisible" title="Outer Dialog" width="600px" append-to-body>
        <p>This is the outer dialog. Open the inner dialog below.</p>
        <div style="margin-top: 16px">
          <el-button type="primary" @click="innerVisible = true">Open Inner Dialog</el-button>
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
    ElMessage.warning('Please fill in username and email')
    return
  }
  ElMessage.success(`User "${userForm.value.name}" created successfully`)
  formVisible.value = false
}

const outerVisible = ref(false)
const innerVisible = ref(false)
</script>