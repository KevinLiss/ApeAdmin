<template>
  <div>
    <PageHeader title="Create New Project" :breadcrumb="['APEUI库', 'Applications', 'Create New Project']" />

    <el-card>
      <el-form :model="form" label-width="140px" style="max-width: 640px">
        <el-form-item label="Project Title">
          <el-input v-model="form.title" placeholder="Enter project title" />
        </el-form-item>
        <el-form-item label="Client">
          <el-input v-model="form.client" placeholder="Enter client name" />
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="form.type" placeholder="Select type" style="width: 100%">
            <el-option label="Web Development" value="web" />
            <el-option label="Mobile App" value="mobile" />
            <el-option label="Cloud Infrastructure" value="cloud" />
            <el-option label="Data Analytics" value="data" />
            <el-option label="UI/UX Design" value="design" />
          </el-select>
        </el-form-item>
        <el-form-item label="Priority">
          <el-select v-model="form.priority" placeholder="Select priority" style="width: 100%">
            <el-option label="Low" value="low" />
            <el-option label="Medium" value="medium" />
            <el-option label="High" value="high" />
            <el-option label="Critical" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="Start Date">
          <el-date-picker v-model="form.startDate" type="date" placeholder="Select start date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="End Date">
          <el-date-picker v-model="form.endDate" type="date" placeholder="Select end date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="Enter project description" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit">Submit</el-button>
          <el-button @click="onCancel">Cancel</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'

const form = ref({
  title: '',
  client: '',
  type: '',
  priority: '',
  startDate: '',
  endDate: '',
  description: '',
})

const onSubmit = () => {
  if (!form.value.title || !form.value.client) {
    ElMessage.warning('Please fill in the required fields')
    return
  }
  ElMessage.success('Project created successfully')
}

const onCancel = () => {
  form.value = {
    title: '',
    client: '',
    type: '',
    priority: '',
    startDate: '',
    endDate: '',
    description: '',
  }
}
</script>

<style scoped>
:deep(.el-button--primary) {
  --el-color-primary: #5A67F5;
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}
</style>
