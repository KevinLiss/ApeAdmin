<template>
  <div>
    <PageHeader title="编辑资料" :breadcrumb="['APEUI库', '用户中心', '编辑资料']" />

    <el-card>
      <el-form :model="form" label-width="120px" style="max-width: 600px">
        <el-form-item label="姓">
          <el-input v-model="form.firstName" placeholder="请输入姓" />
        </el-form-item>
        <el-form-item label="名">
          <el-input v-model="form.lastName" placeholder="请输入名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model="form.phone" placeholder="请输入手机号码" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.bio" type="textarea" :rows="4" placeholder="介绍一下你自己" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSave">保存</el-button>
          <el-button @click="onCancel">取消</el-button>
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
  firstName: '张',
  lastName: '伟',
  email: 'zhangwei@example.com',
  phone: '13800138000',
  bio: '',
})

const onSave = () => {
  ElMessage.success('资料保存成功')
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
