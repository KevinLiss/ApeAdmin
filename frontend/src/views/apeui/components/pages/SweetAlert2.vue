<template>
  <div>
    <PageHeader title="SweetAlert2" :breadcrumb="['APEUI库', 'Components', 'SweetAlert2']" />

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="ElMessageBox.confirm 确认弹窗">
          <div class="btn-group-vertical">
            <el-button type="danger" @click="confirmDelete">删除确认</el-button>
            <el-button type="warning" @click="confirmSubmit">提交确认</el-button>
            <el-button @click="confirmCancel">普通确认</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="ElMessageBox.alert 提示弹窗">
          <div class="btn-group-vertical">
            <el-button type="success" @click="alertSuccess">成功提示</el-button>
            <el-button type="warning" @click="alertWarning">警告提示</el-button>
            <el-button type="danger" @click="alertError">错误提示</el-button>
            <el-button type="info" @click="alertInfo">信息提示</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="ElMessageBox.prompt 输入弹窗">
          <div class="btn-group-vertical">
            <el-button type="primary" @click="promptName">输入用户名</el-button>
            <el-button type="primary" @click="promptEmail">输入邮箱（带校验）</el-button>
            <el-button @click="promptRemark">输入备注</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="ElMessage Toast 通知">
          <div class="btn-group-vertical">
            <el-button type="success" @click="showToast('success')">Success Toast</el-button>
            <el-button type="warning" @click="showToast('warning')">Warning Toast</el-button>
            <el-button type="danger" @click="showToast('error')">Error Toast</el-button>
            <el-button @click="showToast('info')">Info Toast</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" header="综合演示">
      <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center">
        <el-button type="primary" @click="multiStep">多步骤交互演示</el-button>
        <el-button type="danger" @click="dangerConfirm">危险操作（红色确认）</el-button>
        <el-button @click="customHtml">自定义内容弹窗</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../PageHeader.vue'

/* Confirm 弹窗 */
const confirmDelete = () => {
  ElMessageBox.confirm('此操作将永久删除该文件，是否继续？', '删除确认', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => ElMessage.success('删除成功'))
    .catch(() => ElMessage.info('已取消删除'))
}

const confirmSubmit = () => {
  ElMessageBox.confirm('确认提交表单数据？提交后不可修改。', '提交确认', {
    confirmButtonText: '提交',
    cancelButtonText: '再看看',
    type: 'warning',
  })
    .then(() => ElMessage.success('提交成功'))
    .catch(() => {})
}

const confirmCancel = () => {
  ElMessageBox.confirm('您确定要执行此操作吗？', '确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info',
  })
    .then(() => ElMessage.success('操作完成'))
    .catch(() => {})
}

/* Alert 弹窗 */
const alertSuccess = () => {
  ElMessageBox.alert('操作已成功完成！数据已保存到服务器。', '成功', {
    confirmButtonText: '知道了',
    type: 'success',
  })
}

const alertWarning = () => {
  ElMessageBox.alert('您的账户余额不足，请及时充值。', '警告', {
    confirmButtonText: '去充值',
    type: 'warning',
  })
}

const alertError = () => {
  ElMessageBox.alert('服务器内部错误，请稍后重试或联系管理员。', '错误', {
    confirmButtonText: '联系管理员',
    type: 'error',
  })
}

const alertInfo = () => {
  ElMessageBox.alert('系统将于今晚 22:00 进行例行维护，请提前保存。', '系统通知', {
    confirmButtonText: '收到',
    type: 'info',
  })
}

/* Prompt 弹窗 */
const promptName = () => {
  ElMessageBox.prompt('请输入用户名', '用户名', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    inputPlaceholder: '2-20 个字符',
  })
    .then(({ value }) => ElMessage.success(`你输入的用户名是：${value}`))
    .catch(() => {})
}

const promptEmail = () => {
  ElMessageBox.prompt('请输入邮箱地址', '邮箱', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    inputPattern: /[\w!#$%&'*+/=?^_`{|}~-]+@[\w](?:[\w-]*[\w])?(?:\.[\w](?:[\w-]*[\w])?)*/,
    inputErrorMessage: '邮箱格式不正确',
  })
    .then(({ value }) => ElMessage.success(`邮箱：${value}`))
    .catch(() => {})
}

const promptRemark = () => {
  ElMessageBox.prompt('请输入备注信息', '备注', {
    confirmButtonText: '保存',
    cancelButtonText: '取消',
    inputType: 'textarea',
    inputPlaceholder: '可选，最多 200 字',
  })
    .then(({ value }) => ElMessage.success(`备注已保存：${value || '（空）'}`))
    .catch(() => {})
}

/* Toast 通知 */
const showToast = (type: 'success' | 'warning' | 'error' | 'info') => {
  const messages: Record<string, string> = {
    success: '操作成功完成！',
    warning: '请注意：该操作有风险。',
    error: '操作失败，请重试。',
    info: '这是一条信息提示。',
  }
  ElMessage({ type, message: messages[type], showClose: true })
}

/* 综合演示 */
const multiStep = () => {
  ElMessageBox.confirm('第一步：确认开始操作流程？', '多步骤演示 (1/3)', {
    confirmButtonText: '下一步',
    cancelButtonText: '取消',
    type: 'info',
  })
    .then(() => {
      ElMessageBox.prompt('第二步：请输入操作备注', '多步骤演示 (2/3)', {
        confirmButtonText: '下一步',
        cancelButtonText: '上一步',
        inputPlaceholder: '输入备注...',
      })
        .then(({ value }) => {
          ElMessageBox.alert(`第三步：操作完成！备注：${value || '（空）'}`, '多步骤演示 (3/3)', {
            confirmButtonText: '完成',
            type: 'success',
          })
        })
        .catch(() => multiStep())
    })
    .catch(() => ElMessage.info('已取消操作流程'))
}

const dangerConfirm = () => {
  ElMessageBox.confirm('该操作不可逆！确定要清空所有日志数据吗？', '危险操作', {
    confirmButtonText: '确认清空',
    cancelButtonText: '取消',
    type: 'error',
    confirmButtonClass: 'el-button--danger',
  })
    .then(() => ElMessage.success('日志已清空'))
    .catch(() => {})
}

const customHtml = () => {
  ElMessageBox.alert(
    '<div style="text-align:center;padding:8px 0">' +
      '<div style="font-size:48px;color:#534686;font-weight:bold;margin-bottom:8px">ApeAdmin</div>' +
      '<p style="color:#5a6273;margin:0">自定义 HTML 内容弹窗示例</p>' +
      '<p style="color:#909399;font-size:13px;margin-top:8px">支持 HTML 标签渲染</p>' +
      '</div>',
    '自定义内容',
    { confirmButtonText: '关闭', dangerouslyUseHTMLString: true }
  )
}
</script>

<style scoped>
.btn-group-vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
