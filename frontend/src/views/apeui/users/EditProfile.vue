<template>
  <div>
    <PageHeader title="Users Edit" :breadcrumb="['APEUI库', 'Users', 'Users Edit']" />

    <el-card>
      <el-form :model="form" label-width="120px" style="max-width: 600px">
        <el-form-item label="First Name">
          <el-input v-model="form.firstName" placeholder="Enter first name" />
        </el-form-item>
        <el-form-item label="Last Name">
          <el-input v-model="form.lastName" placeholder="Enter last name" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="form.email" placeholder="Enter email address" />
        </el-form-item>
        <el-form-item label="Phone">
          <el-input v-model="form.phone" placeholder="Enter phone number" />
        </el-form-item>
        <el-form-item label="Bio">
          <el-input v-model="form.bio" type="textarea" :rows="4" placeholder="Tell us about yourself" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSave">Save</el-button>
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
  firstName: 'John',
  lastName: 'Doe',
  email: 'john.doe@example.com',
  phone: '+1 (555) 123-4567',
  bio: '',
})

const onSave = () => {
  ElMessage.success('Profile saved successfully')
}

const onCancel = () => {
  form.value = {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    bio: '',
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
