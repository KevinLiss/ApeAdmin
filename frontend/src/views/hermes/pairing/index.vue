<template>
  <div class="hermes-pairing-page">
    <!-- 待批准列表 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="section-header">
          <span>待批准的配对请求（{{ pending.length }}）</span>
          <el-button
            size="small"
            type="danger"
            plain
            :loading="clearing"
            :disabled="!pending.length"
            @click="clearPending"
          >
            清空待批准
          </el-button>
        </div>
      </template>

      <div v-if="!loading && !pending.length" class="empty-tip">
        暂无待批准的配对请求。新设备发起配对后会出现在这里。
      </div>

      <div
        v-for="user in pending"
        :key="userKey(user)"
        class="pairing-row"
      >
        <div class="pairing-info">
          <el-tag size="small" effect="plain">{{ user.platform }}</el-tag>
          <span class="user-name">{{ userLabel(user) }}</span>
          <span class="user-id mono">{{ user.user_id }}</span>
          <span v-if="user.age_minutes != null" class="user-age">
            {{ Math.floor(user.age_minutes) }} 分钟前
          </span>
        </div>
        <el-button
          size="small"
          type="primary"
          :loading="approving === userKey(user)"
          :disabled="!user.request_id"
          @click="approve(user)"
        >
          批准
        </el-button>
      </div>
    </el-card>

    <!-- 已批准列表 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="section-header">
          <span>已授权用户（{{ approved.length }}）</span>
        </div>
      </template>

      <div v-if="!loading && !approved.length" class="empty-tip">
        暂无已授权用户。
      </div>

      <div
        v-for="user in approved"
        :key="userKey(user)"
        class="pairing-row"
      >
        <div class="pairing-info">
          <el-tag size="small" effect="plain">{{ user.platform }}</el-tag>
          <span class="user-name">{{ userLabel(user) }}</span>
          <span class="user-id mono">{{ user.user_id }}</span>
        </div>
        <el-button
          size="small"
          type="danger"
          text
          :loading="revoking === userKey(user)"
          @click="confirmRevoke(user)"
        >
          撤销访问
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { hermes } from '@/api/hermes'

interface PairingUser {
  platform: string
  user_id: string
  user_name?: string
  request_id?: string
  age_minutes?: number
}

const pending = ref<PairingUser[]>([])
const approved = ref<PairingUser[]>([])
const loading = ref(false)
const approving = ref<string | null>(null)
const revoking = ref<string | null>(null)
const clearing = ref(false)

const userKey = (u: PairingUser) => `${u.platform}:${u.user_id}`
const userLabel = (u: PairingUser) => u.user_name || u.user_id

async function loadPairing() {
  loading.value = true
  try {
    const res: any = await hermes.getPairing()
    pending.value = res.pending || []
    approved.value = res.approved || []
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '加载配对数据失败')
  } finally {
    loading.value = false
  }
}

async function approve(user: PairingUser) {
  if (!user.request_id) {
    ElMessage.error('该请求缺少 request_id，无法批准')
    return
  }
  approving.value = userKey(user)
  try {
    await hermes.approvePairing(user.platform, user.request_id)
    ElMessage.success(`已批准 ${userLabel(user)}`)
    await loadPairing()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '批准失败')
  } finally {
    approving.value = null
  }
}

function confirmRevoke(user: PairingUser) {
  ElMessageBox.confirm(
    `确定撤销 ${userLabel(user)}（${user.platform}）的访问权限？`,
    '撤销访问',
    { type: 'warning', confirmButtonText: '撤销', cancelButtonText: '取消' }
  ).then(() => revoke(user)).catch(() => {})
}

async function revoke(user: PairingUser) {
  revoking.value = userKey(user)
  try {
    await hermes.revokePairing(user.platform, user.user_id)
    ElMessage.success('已撤销访问权限')
    await loadPairing()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '撤销失败')
  } finally {
    revoking.value = null
  }
}

async function clearPending() {
  try {
    await ElMessageBox.confirm(
      '确定清空所有待批准的配对请求？',
      '清空待批准',
      { type: 'warning', confirmButtonText: '清空', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  clearing.value = true
  try {
    const res: any = await hermes.clearPendingPairing()
    ElMessage.success(`已清除 ${res.cleared ?? 0} 个待批准请求`)
    await loadPairing()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '清空失败')
  } finally {
    clearing.value = false
  }
}

onMounted(loadPairing)
</script>

<style scoped>
.hermes-pairing-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.pairing-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 4px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.pairing-row:last-child {
  border-bottom: none;
}

.pairing-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
  flex-wrap: wrap;
}

.user-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.user-id {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.mono {
  font-family: ui-monospace, 'SF Mono', Consolas, monospace;
}

.user-age {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.empty-tip {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  padding: 8px 0;
}
</style>
