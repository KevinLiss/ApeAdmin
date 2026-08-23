<template>
  <div class="profile-page">
    <!-- 页面标题 -->
    <div class="page-head">
      <h3>个人中心</h3>
      <span class="breadcrumb">个人中心 / 我的资料</span>
    </div>

    <el-row :gutter="20">
      <!-- 左栏：用户信息卡 -->
      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="profile-card">
          <div class="profile-avatar-wrap">
            <el-avatar :size="88" class="profile-avatar">
              {{ avatarText }}
            </el-avatar>
          </div>
          <h2 class="profile-name">{{ profile.nickname || profile.username || 'Admin' }}</h2>
          <p class="profile-username">@{{ profile.username }}</p>
          <div class="profile-roles">
            <el-tag v-for="r in profile.roles || []" :key="r.id" size="small" class="role-tag">
              {{ r.name }}
            </el-tag>
            <span v-if="!profile.roles?.length">—</span>
          </div>
          <el-divider />
          <div class="profile-meta">
            <div class="meta-item">
              <el-icon><OfficeBuilding /></el-icon>
              <span class="meta-label">部门</span>
              <span class="meta-value">{{ profile.dept?.name || '—' }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              <span class="meta-label">创建时间</span>
              <span class="meta-value">{{ formatDate(profile.created_at) }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Clock /></el-icon>
              <span class="meta-label">最近登录</span>
              <span class="meta-value">{{ formatDate(profile.last_login_at) }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Location /></el-icon>
              <span class="meta-label">登录 IP</span>
              <span class="meta-value">{{ profile.last_login_ip || '—' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右栏：资料编辑 + 修改密码 -->
      <el-col :xs="24" :md="16">
        <el-card shadow="never" class="edit-card">
          <template #header>
            <div class="card-title">
              <el-icon><EditPen /></el-icon>
              <span>基本资料</span>
            </div>
          </template>
          <el-form :model="editForm" label-width="90px" class="edit-form">
            <el-form-item label="用户名">
              <el-input :model-value="profile.username" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="editForm.nickname" placeholder="请输入昵称" maxlength="50" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="editForm.email" placeholder="请输入邮箱" maxlength="100" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="editForm.phone" placeholder="请输入手机号" maxlength="20" />
            </el-form-item>
            <el-form-item label="头像地址">
              <el-input v-model="editForm.avatar" placeholder="可选：头像图片 URL" maxlength="500" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="saveProfile">
                <el-icon v-if="!saving"><Check /></el-icon>保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" class="edit-card">
          <template #header>
            <div class="card-title">
              <el-icon><Lock /></el-icon>
              <span>修改密码</span>
            </div>
          </template>
          <el-form :model="pwdForm" label-width="90px" class="edit-form">
            <el-form-item label="原密码">
              <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入原密码" />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="至少 6 位" />
            </el-form-item>
            <el-form-item label="确认新密码">
              <el-input v-model="pwdForm.confirm" type="password" show-password placeholder="再次输入新密码" />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" :loading="savingPwd" @click="savePassword">
                <el-icon v-if="!savingPwd"><Key /></el-icon>修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  OfficeBuilding, Calendar, Clock, Location, EditPen, Lock, Key, Check,
} from '@element-plus/icons-vue'
import { getProfile, updateProfile, changePassword } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const profile = ref<any>({})
const saving = ref(false)
const savingPwd = ref(false)

const editForm = reactive({
  nickname: '',
  email: '',
  phone: '',
  avatar: '',
})

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm: '',
})

const avatarText = computed(() =>
  (profile.value.nickname || profile.value.username || 'A').charAt(0).toUpperCase()
)

function formatDate(v?: string | null): string {
  if (!v) return '—'
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return v
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function fetchProfile() {
  try {
    const data: any = await getProfile()
    profile.value = data
    editForm.nickname = data.nickname || ''
    editForm.email = data.email || ''
    editForm.phone = data.phone || ''
    editForm.avatar = data.avatar || ''
  } catch (e) {
    console.error('[Profile] 获取个人资料失败:', e)
  }
}

async function saveProfile() {
  saving.value = true
  try {
    const data: any = await updateProfile({
      nickname: editForm.nickname,
      email: editForm.email,
      phone: editForm.phone,
      avatar: editForm.avatar,
    })
    ElMessage.success('资料更新成功')
    profile.value = { ...profile.value, ...data }
    // 同步更新 Pinia 中的昵称/头像，让顶部导航即时生效
    userStore.nickname = data.nickname ?? userStore.nickname
    userStore.avatar = data.avatar ?? userStore.avatar
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function savePassword() {
  if (!pwdForm.old_password || !pwdForm.new_password) {
    ElMessage.warning('请填写原密码和新密码')
    return
  }
  if (pwdForm.new_password.length < 6) {
    ElMessage.warning('新密码至少 6 位')
    return
  }
  if (pwdForm.new_password !== pwdForm.confirm) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  savingPwd.value = true
  try {
    await changePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password,
    })
    ElMessage.success('密码修改成功，请重新登录')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm = ''
    await userStore.logout()
    router.push('/login')
  } catch (e: any) {
    ElMessage.error(e?.message || '密码修改失败')
  } finally {
    savingPwd.value = false
  }
}

onMounted(fetchProfile)
</script>

<style scoped>
.profile-page {
  padding: 0;
}
.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e9edf3;
}
.page-head h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #2b2b2b;
}
.breadcrumb {
  font-size: 13px;
  color: #909399;
}

.profile-card {
  border-radius: 16px;
  text-align: center;
  padding: 10px 0;
}
.profile-avatar-wrap {
  margin-bottom: 12px;
}
.profile-avatar {
  background: linear-gradient(135deg, #5A67F5, #47A8FF);
  font-size: 32px;
  font-weight: 600;
}
.profile-name {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 600;
  color: #2b2b2b;
}
.profile-username {
  margin: 0 0 12px;
  font-size: 13px;
  color: #909399;
}
.profile-roles {
  display: flex;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
}
.role-tag {
  background: rgba(90, 103, 245, 0.08);
  border-color: rgba(90, 103, 245, 0.2);
  color: #5A67F5;
}
.profile-meta {
  display: flex;
  flex-direction: column;
  gap: 14px;
  text-align: left;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}
.meta-item .el-icon {
  color: #5A67F5;
  font-size: 16px;
}
.meta-label {
  color: #909399;
  width: 72px;
  flex-shrink: 0;
}
.meta-value {
  color: #2b2b2b;
  font-weight: 500;
  flex: 1;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.edit-card {
  border-radius: 16px;
  margin-bottom: 20px;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
.card-title .el-icon {
  color: #5A67F5;
}
.edit-form {
  max-width: 520px;
}
</style>