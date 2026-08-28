<template>
  <div class="plugins-admin">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card pending">
        <div class="stat-icon"><el-icon><Document /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待审核</div>
        </div>
      </div>
      <div class="stat-card approved">
        <div class="stat-icon"><el-icon><CircleCheck /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.approved }}</div>
          <div class="stat-label">已上架</div>
        </div>
      </div>
      <div class="stat-card rejected">
        <div class="stat-icon"><el-icon><CircleClose /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.rejected }}</div>
          <div class="stat-label">已驳回</div>
        </div>
      </div>
      <div class="stat-card offline">
        <div class="stat-icon"><el-icon><Remove /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.offline }}</div>
          <div class="stat-label">已下架</div>
        </div>
      </div>
      <div class="stat-card revenue">
        <div class="stat-icon"><el-icon><Money /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.totalRevenue }} <small>USDT</small></div>
          <div class="stat-label">总成交额</div>
        </div>
      </div>
    </div>

    <!-- 主卡片 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>插件审核管理</span>
          <span class="header-note">提交 · AI 分析 · 审核 · 发布 · 分成</span>
        </div>
      </template>

      <div class="toolbar">
        <el-input v-model="query.keyword" clearable placeholder="搜索插件名称、标识或描述" class="search" @keyup.enter="search">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="query.status" clearable placeholder="全部状态" class="status" @change="search">
          <el-option label="待审核" value="pending" />
          <el-option label="已上架" value="approved" />
          <el-option label="已驳回" value="rejected" />
          <el-option label="已下架" value="offline" />
        </el-select>
        <el-button type="primary" @click="search">查询</el-button>
      </div>

      <el-table :data="pluginList" v-loading="loading" stripe @row-click="openDetail" row-class-name="clickable-row">
        <el-table-column prop="display_name" label="插件" min-width="180">
          <template #default="{ row }">
            <div class="plugin-name-cell">
              <span class="plugin-icon">{{ row.icon ? '📦' : '🔌' }}</span>
              <div>
                <div class="plugin-title">{{ row.display_name }}</div>
                <small>{{ row.name }} · v{{ row.version }}</small>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="developer.username" label="开发者" width="120" />
        <el-table-column prop="category" label="分类" width="90" />
        <el-table-column label="价格" width="100">
          <template #default="{ row }">
            <span v-if="Number(row.price) > 0" class="price-tag">{{ row.price }} USDT</span>
            <span v-else class="free-tag">免费</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light" round>{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="审核队列" width="90" align="center">
          <template #default="{ row }">
            <el-badge :value="row.review_queue_count" :hidden="!row.review_queue_count" type="warning">
              <span class="queue-text">{{ row.review_queue_count || 0 }}</span>
            </el-badge>
          </template>
        </el-table-column>
        <el-table-column label="购买/安装" width="110">
          <template #default="{ row }">
            <div class="metric-cell">
              <span>{{ row.metrics?.buyer_count || 0 }} 购买</span>
              <small>{{ row.metrics?.install_users || 0 }} 安装</small>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click.stop="openDetail(row)">审核</el-button>
            <el-button v-if="row.status === 'approved'" text type="warning" @click.stop="offline(row)">下架</el-button>
            <el-button v-if="['offline', 'rejected'].includes(row.status)" text type="success" @click.stop="online(row)">上架</el-button>
            <el-button text type="danger" @click.stop="remove(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="暂无插件提交" /></template>
      </el-table>

      <div class="pager" v-if="total > query.page_size">
        <el-pagination v-model:current-page="query.page" :page-size="query.page_size" :total="total" layout="prev, pager, next" @current-change="loadList" />
      </div>
    </el-card>

    <!-- 审核详情抽屉 -->
    <el-drawer v-model="detailVisible" title="插件审核工作台" size="780px" destroy-on-close>
      <template v-if="detail">
        <!-- 插件基本信息 -->
        <div class="plugin-header">
          <div class="plugin-header-main">
            <h3>{{ detail.display_name }}</h3>
            <p>{{ detail.description || '暂无描述' }}</p>
            <div class="plugin-meta">
              <span><el-icon><User /></el-icon> {{ detail.developer?.username || '-' }}</span>
              <span><el-icon><PriceTag /></el-icon> {{ Number(detail.price) > 0 ? `${detail.price} USDT` : '免费' }}</span>
              <span><el-icon><Folder /></el-icon> {{ detail.category }}</span>
              <span>📊 服务费 {{ detail.service_fee_rate }}%</span>
            </div>
          </div>
          <el-tag :type="statusType(detail.status)" effect="dark" size="large" round>{{ statusLabel(detail.status) }}</el-tag>
        </div>

        <!-- 指标条 -->
        <div class="metrics-bar">
          <div class="metric-item"><span class="metric-val">{{ detail.metrics?.buyer_count || 0 }}</span><span class="metric-lbl">购买人数</span></div>
          <div class="metric-item"><span class="metric-val">{{ detail.metrics?.paid_order_count || 0 }}</span><span class="metric-lbl">成交订单</span></div>
          <div class="metric-item"><span class="metric-val">{{ detail.metrics?.paid_amount || 0 }}</span><span class="metric-lbl">成交额 USDT</span></div>
          <div class="metric-item"><span class="metric-val">{{ detail.metrics?.install_users || 0 }}</span><span class="metric-lbl">安装人数</span></div>
        </div>

        <!-- Tab 区 -->
        <el-tabs v-model="activeTab" class="review-tabs">
          <!-- 版本审核 -->
          <el-tab-pane label="版本审核" name="versions">
            <div class="version-flow-hint">
              <span class="flow-step" :class="{ active: true }">1. 提交</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">2. AI 分析</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">3. 审核通过</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">4. 发布上架</span>
            </div>
            <el-table :data="detail.versions || []" size="small" row-key="id" border>
              <el-table-column prop="version" label="版本号" width="90">
                <template #default="{ row }"><strong>v{{ row.version }}</strong></template>
              </el-table-column>
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="versionStatusType(row.status)" size="small" effect="light">{{ versionStatusLabel(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="AI 风险" width="80" align="center">
                <template #default="{ row }">
                  <el-tooltip v-if="row.analysis_report?.risk_level" :content="`风险等级: ${row.analysis_report.risk_level}`" placement="top">
                    <span :class="['risk-badge', `risk-${row.analysis_report.risk_level}`]">{{ row.analysis_report.risk_level }}</span>
                  </el-tooltip>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="文件" min-width="120">
                <template #default="{ row }">
                  <span v-for="file in row.files" :key="file.id" class="file-link" @click="downloadFile(file)">
                    <el-icon><Document /></el-icon> {{ file.filename }}
                  </span>
                  <span v-if="!row.files?.length">-</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="280">
                <template #default="{ row }">
                  <el-button text type="primary" @click="openSource(row)">源码</el-button>
                  <el-button text type="info" @click="openAIReport(row)">AI 报告</el-button>
                  <el-button v-if="row.status === 'submitted'" text type="success" @click="openApprove(row)">通过</el-button>
                  <el-button v-if="row.status === 'submitted'" text type="danger" @click="openReject(row)">驳回</el-button>
                  <el-button v-if="row.status === 'approved'" text type="primary" @click="publishVersion(row)">
                    <el-icon><Promotion /></el-icon> 发布上架
                  </el-button>
                  <el-tag v-if="row.status === 'published'" type="success" size="small" effect="dark">已发布</el-tag>
                </template>
              </el-table-column>
              <template #empty><el-empty description="暂无版本" :image-size="60" /></template>
            </el-table>
            <div v-if="detail.reject_reason" class="reject-reason-box">
              <el-icon><WarningFilled /></el-icon>
              <span>驳回原因：{{ detail.reject_reason }}</span>
            </div>
          </el-tab-pane>

          <!-- AI 分析报告 -->
          <el-tab-pane label="AI 分析报告" name="ai">
            <div v-if="currentAIReport" class="ai-report">
              <div class="ai-report-header">
                <span :class="['risk-badge', `risk-${currentAIReport.risk_level || 'unknown'}`]">
                  风险等级: {{ currentAIReport.risk_level || '未知' }}
                </span>
                <span class="ai-model">分析模型: {{ currentAIReport.model || 'DeepSeek' }}</span>
              </div>
              <div v-if="currentAIReport.summary" class="ai-section">
                <h4>概述</h4>
                <p>{{ currentAIReport.summary }}</p>
              </div>
              <div v-if="currentAIReport.features?.length" class="ai-section">
                <h4>功能特性</h4>
                <ul>
                  <li v-for="(feat, i) in currentAIReport.features" :key="i">{{ feat }}</li>
                </ul>
              </div>
              <div v-if="currentAIReport.architecture" class="ai-section">
                <h4>架构说明</h4>
                <p>{{ currentAIReport.architecture }}</p>
              </div>
              <div v-if="currentAIReport.warnings?.length" class="ai-section">
                <h4>安全警告</h4>
                <div v-for="(warn, i) in currentAIReport.warnings" :key="i" :class="['warn-item', `warn-${warn.severity || 'info'}`]">
                  <el-icon><Warning /></el-icon>
                  <span>{{ warn.message || warn }}</span>
                </div>
              </div>
              <div v-if="currentAIReport.file_count" class="ai-section">
                <h4>文件统计</h4>
                <p>共 {{ currentAIReport.file_count }} 个文件，总大小 {{ formatSize(currentAIReport.total_size || 0) }}</p>
              </div>
            </div>
            <el-empty v-else description="请从版本列表点击「AI 报告」查看分析结果" :image-size="80" />
          </el-tab-pane>

          <!-- 源码审查 -->
          <el-tab-pane label="源码审查" name="source">
            <div v-if="sourceFiles.length" class="source-layout">
              <div class="source-list">
                <div class="source-list-header">文件列表 ({{ sourceFiles.length }})</div>
                <button v-for="file in sourceFiles" :key="file.path"
                  :class="['source-file-btn', { active: currentSourcePath === file.path }]"
                  @click="loadSource(file.path)">
                  <el-icon><Document /></el-icon>
                  <span>{{ file.path }}</span>
                </button>
              </div>
              <div class="source-viewer">
                <div v-if="sourceContent" class="source-code">{{ sourceContent }}</div>
                <el-empty v-else description="选择左侧文件查看源码" :image-size="60" />
              </div>
            </div>
            <el-empty v-else description="请从版本列表点击「源码」查看文件树" :image-size="80" />
          </el-tab-pane>

          <!-- 审核历史 -->
          <el-tab-pane label="审核历史" name="history">
            <el-timeline v-if="detail.reviews?.length">
              <el-timeline-item v-for="review in detail.reviews" :key="review.id"
                :type="reviewActionType(review.action)"
                :timestamp="formatDate(review.created_at)"
                placement="top">
                <div class="review-item">
                  <span :class="['review-action', `review-${review.action}`]">{{ reviewActionLabel(review.action) }}</span>
                  <span v-if="review.service_fee_rate" class="review-fee">服务费 {{ review.service_fee_rate }}%</span>
                  <p v-if="review.comment" class="review-comment">{{ review.comment }}</p>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无审核记录" :image-size="80" />
          </el-tab-pane>
        </el-tabs>

        <!-- 底部操作 -->
        <div class="drawer-actions">
          <el-button v-if="detail.status === 'approved'" type="warning" plain @click="offline(detail)">
            <el-icon><Remove /></el-icon> 下架插件
          </el-button>
          <el-button v-if="detail.status === 'offline'" type="success" plain @click="online(detail)">
            <el-icon><Promotion /></el-icon> 重新上架
          </el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 审核通过弹窗 -->
    <el-dialog v-model="approveVisible" title="审核通过" width="480px" destroy-on-close>
      <div class="dialog-body">
        <div class="dialog-hint">
          <el-icon><InfoFilled /></el-icon>
          <span>通过后版本状态变为"已通过"，还需手动点击"发布上架"才能在市场展示。</span>
        </div>
        <el-form label-position="top">
          <el-form-item label="平台服务费百分比">
            <el-input-number v-model="feeRate" :min="0" :max="100" :precision="2" :step="5" />
            <span class="form-note">从每笔成交金额中扣除，余额进入开发者待结算收益</span>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="approveVisible = false">取消</el-button>
        <el-button type="success" :loading="actionLoading" @click="confirmApprove">确认通过</el-button>
      </template>
    </el-dialog>

    <!-- 驳回弹窗 -->
    <el-dialog v-model="rejectVisible" title="驳回插件版本" width="480px" destroy-on-close>
      <div class="dialog-body">
        <div class="dialog-hint warn">
          <el-icon><WarningFilled /></el-icon>
          <span>驳回后开发者可在修改后重新提交审核。请填写清晰的驳回原因。</span>
        </div>
        <el-input v-model="rejectReason" type="textarea" :rows="4" placeholder="请填写开发者可理解的驳回原因（必填）" />
      </div>
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" :loading="actionLoading" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, CircleCheck, CircleClose, Remove, Money, Search, User, PriceTag, Folder, Warning, WarningFilled, InfoFilled, Promotion } from '@element-plus/icons-vue'
import {
  deleteAdminPlugin, getAdminPluginDetail, getAdminPluginFileDownloadUrl,
  getAdminPlugins, getAdminVersionSource, getAdminVersionSourceTree,
  offlinePlugin, onlinePlugin, publishPluginVersion, reviewPluginVersion,
} from '@/api/apehub_web'

const pluginList = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const actionLoading = ref(false)
const query = ref({ status: '', keyword: '', page: 1, page_size: 20 })
const detailVisible = ref(false)
const detail = ref<any>(null)
const activeTab = ref('versions')

// 弹窗
const rejectVisible = ref(false)
const rejectReason = ref('')
const rejectTarget = ref<any>(null)
const approveVisible = ref(false)
const approveTarget = ref<any>(null)
const feeRate = ref(30)

// 源码
const sourceFiles = ref<any[]>([])
const sourceContent = ref('')
const currentSourcePath = ref('')
const sourceVersionId = ref<number>(0)

// AI 报告
const currentAIReport = ref<any>(null)

// 统计
const stats = ref({ pending: 0, approved: 0, rejected: 0, offline: 0, totalRevenue: 0 })

const statusLabel = (status: string) =>
  ({ pending: '待审核', approved: '已上架', rejected: '已驳回', offline: '已下架' }[status] || status)
const statusType = (status: string) =>
  ({ pending: 'warning', approved: 'success', rejected: 'danger', offline: 'info' } as any)[status] || 'info'

const versionStatusLabel = (status: string) =>
  ({ draft: '草稿', analyzing: 'AI 分析中', analysis_failed: '分析失败', submitted: '待审核',
     reviewing: '审核中', approved: '已通过', published: '已发布', rejected: '已驳回', deprecated: '历史版本'
  } as any)[status] || status
const versionStatusType = (status: string) =>
  ({ submitted: 'warning', approved: 'success', published: 'success', rejected: 'danger',
     analysis_failed: 'danger', analyzing: 'info', draft: 'info', deprecated: 'info', reviewing: 'warning'
  } as any)[status] || 'info'

const reviewActionLabel = (action: string) =>
  ({ approve: '审核通过', reject: '驳回', publish: '发布上架', submit: '提交审核' }[action] || action)
const reviewActionType = (action: string) =>
  ({ approve: 'success', reject: 'danger', publish: 'primary', submit: 'warning' } as any)[action] || 'info'

const formatSize = (size: number) =>
  size >= 1024 * 1024 ? `${(size / 1024 / 1024).toFixed(2)} MB` : `${Math.ceil((size || 0) / 1024)} KB`

const formatDate = (d: string) => d ? d.replace('T', ' ').slice(0, 16) : '-'

// 加载列表
const loadList = async () => {
  loading.value = true
  try {
    const data = await getAdminPlugins(query.value)
    pluginList.value = data.items || []
    total.value = data.total || 0
    // 计算统计
    const s = { pending: 0, approved: 0, rejected: 0, offline: 0, totalRevenue: 0 }
    for (const p of pluginList.value) {
      const st = p.status || 'pending'
      if (st in s) (s as any)[st]++
      s.totalRevenue += Number(p.metrics?.paid_amount || 0)
    }
    stats.value = s
  } finally { loading.value = false }
}
const search = () => { query.value.page = 1; loadList() }

// 打开详情
const openDetail = async (row: any) => {
  detailVisible.value = true
  detail.value = null
  activeTab.value = 'versions'
  currentAIReport.value = null
  sourceFiles.value = []
  sourceContent.value = ''
  currentSourcePath.value = ''
  try {
    detail.value = await getAdminPluginDetail(row.id)
  } catch {
    detailVisible.value = false
  }
}

const refresh = async (pluginId?: number) => {
  await loadList()
  if (pluginId && detailVisible.value) detail.value = await getAdminPluginDetail(pluginId)
}

// 审核操作
const openReject = (row: any) => { rejectTarget.value = row; rejectReason.value = ''; rejectVisible.value = true }
const confirmReject = async () => {
  if (!rejectReason.value.trim() || !detail.value) return ElMessage.warning('请填写驳回原因')
  actionLoading.value = true
  try {
    await reviewPluginVersion(detail.value.id, rejectTarget.value.id, { action: 'reject', reason: rejectReason.value.trim() })
    ElMessage.success('版本已驳回')
    rejectVisible.value = false
    await refresh(detail.value.id)
  } finally { actionLoading.value = false }
}

const openApprove = (version: any) => {
  approveTarget.value = version
  feeRate.value = Number(detail.value?.service_fee_rate || 30)
  approveVisible.value = true
}
const confirmApprove = async () => {
  if (!detail.value || !approveTarget.value) return
  actionLoading.value = true
  try {
    await reviewPluginVersion(detail.value.id, approveTarget.value.id, { action: 'approve', service_fee_rate: feeRate.value })
    ElMessage.success('版本已通过，请点击"发布上架"使其在市场展示')
    approveVisible.value = false
    await refresh(detail.value.id)
  } finally { actionLoading.value = false }
}

const publishVersion = async (version: any) => {
  if (!detail.value) return
  await ElMessageBox.confirm(`确认发布 v${version.version} 至插件市场？发布后用户可购买和安装。`, '发布版本', { type: 'warning' })
  await publishPluginVersion(detail.value.id, version.id)
  ElMessage.success('版本已发布上架')
  await refresh(detail.value.id)
}

// 源码查看
const openSource = async (version: any) => {
  if (!detail.value) return
  sourceVersionId.value = version.id
  sourceContent.value = ''
  currentSourcePath.value = ''
  activeTab.value = 'source'
  const data = await getAdminVersionSourceTree(detail.value.id, version.id)
  sourceFiles.value = data.files || []
  detailVisible.value = detailVisible.value || true
}
const loadSource = async (path: string) => {
  if (!detail.value || !sourceVersionId.value) return
  currentSourcePath.value = path
  const data = await getAdminVersionSource(detail.value.id, sourceVersionId.value, path)
  sourceContent.value = data.content || ''
}

// AI 报告
const openAIReport = (version: any) => {
  currentAIReport.value = version.analysis_report || null
  activeTab.value = 'ai'
}

// 下架/上架/删除
const offline = async (row: any) => {
  await ElMessageBox.confirm(`确认下架「${row.display_name}」？已购买用户仍可下载。`, '下架插件', { type: 'warning' })
  await offlinePlugin(row.id)
  ElMessage.success('插件已下架')
  await refresh(row.id)
}
const online = async (row: any) => {
  await onlinePlugin(row.id)
  ElMessage.success('插件已上架')
  await refresh(row.id)
}
const remove = async (row: any) => {
  await ElMessageBox.confirm(`确认删除「${row.display_name}」？有购买记录的插件会被系统保护，无法删除。`, '删除插件', { type: 'warning' })
  await deleteAdminPlugin(row.id)
  ElMessage.success('插件已删除')
  detailVisible.value = false
  await loadList()
}

const downloadFile = async (file: any) => {
  if (!detail.value) return
  const response = await fetch(getAdminPluginFileDownloadUrl(detail.value.id, file.id), {
    headers: { Authorization: `Bearer ${localStorage.getItem('apeadmin_token') || ''}` },
  })
  if (!response.ok) return ElMessage.error('文件下载失败')
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = file.filename
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(loadList)
</script>

<style scoped>
/* 统计卡片 */
.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 24px;
  border-radius: 12px;
  background: var(--el-fill-color-lighter);
  border: 1px solid var(--el-border-color-lighter);
  min-width: 140px;
  flex: 1;
  transition: all 0.2s;
}
.stat-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.stat-icon {
  width: 42px; height: 42px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
}
.stat-card.pending .stat-icon { background: #fef3e2; color: #e6a23c; }
.stat-card.approved .stat-icon { background: #e8f5e9; color: #67c23a; }
.stat-card.rejected .stat-icon { background: #fde2e2; color: #f56c6c; }
.stat-card.offline .stat-icon { background: #f0f0f0; color: #909399; }
.stat-card.revenue .stat-icon { background: #e6e6fa; color: #6366f1; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--el-text-color-primary); }
.stat-value small { font-size: 12px; font-weight: 400; color: var(--el-text-color-secondary); }
.stat-label { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 2px; }

/* 主卡片 */
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-note { color: var(--el-text-color-secondary); font-size: 12px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.search { width: 300px; }
.status { width: 130px; }
.pager { margin-top: 16px; display: flex; justify-content: center; }

/* 表格行 */
.plugin-name-cell { display: flex; align-items: center; gap: 10px; }
.plugin-icon { font-size: 20px; }
.plugin-title { font-weight: 600; }
.metric-cell { display: flex; flex-direction: column; }
.metric-cell small { color: var(--el-text-color-secondary); font-size: 11px; }
.queue-text { font-size: 14px; }
.price-tag { color: #e6a23c; font-weight: 600; }
.free-tag { color: #67c23a; }
.clickable-row { cursor: pointer; }

/* 抽屉 */
.plugin-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 20px;
}
.plugin-header-main h3 { margin: 0 0 6px; font-size: 18px; }
.plugin-header-main p { margin: 0 0 10px; color: var(--el-text-color-secondary); font-size: 13px; }
.plugin-meta { display: flex; gap: 16px; flex-wrap: wrap; }
.plugin-meta span { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--el-text-color-secondary); }

.metrics-bar {
  display: flex; gap: 0;
  margin-bottom: 20px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter);
}
.metric-item {
  flex: 1; text-align: center; padding: 14px 8px;
  background: var(--el-fill-color-lighter);
  border-right: 1px solid var(--el-border-color-lighter);
}
.metric-item:last-child { border-right: 0; }
.metric-val { display: block; font-size: 20px; font-weight: 700; color: var(--el-text-color-primary); }
.metric-lbl { font-size: 11px; color: var(--el-text-color-secondary); }

/* 版本流程提示 */
.version-flow-hint {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 16px; padding: 12px 16px;
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
}
.flow-step { font-size: 12px; color: var(--el-text-color-secondary); }
.flow-step.active { color: var(--el-color-primary); font-weight: 600; }
.flow-arrow { color: var(--el-text-color-placeholder); }

/* 文件链接 */
.file-link {
  display: inline-flex; align-items: center; gap: 4px;
  color: var(--el-color-primary); cursor: pointer;
  margin-right: 8px; font-size: 12px;
}
.file-link:hover { text-decoration: underline; }

/* 风险标签 */
.risk-badge {
  display: inline-block; padding: 2px 10px; border-radius: 12px;
  font-size: 11px; font-weight: 600;
}
.risk-low { background: #e8f5e9; color: #2e7d32; }
.risk-medium { background: #fff3e0; color: #e65100; }
.risk-high { background: #fde2e2; color: #c62828; }
.risk-unknown { background: #f0f0f0; color: #909399; }

/* 驳回原因 */
.reject-reason-box {
  display: flex; align-items: center; gap: 8px;
  margin-top: 14px; padding: 10px 14px;
  background: #fde2e2; border-radius: 8px;
  color: #c62828; font-size: 13px;
}

/* AI 报告 */
.ai-report { padding: 4px 0; }
.ai-report-header {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 16px;
}
.ai-model { font-size: 12px; color: var(--el-text-color-secondary); }
.ai-section { margin-bottom: 18px; }
.ai-section h4 { margin: 0 0 8px; font-size: 14px; color: var(--el-text-color-primary); }
.ai-section p { margin: 0; font-size: 13px; color: var(--el-text-color-regular); line-height: 1.7; }
.ai-section ul { margin: 0; padding-left: 18px; }
.ai-section li { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.8; }
.warn-item {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 12px; border-radius: 6px; margin-bottom: 6px;
  font-size: 12px;
}
.warn-high { background: #fde2e2; color: #c62828; }
.warn-medium { background: #fff3e0; color: #e65100; }
.warn-low, .warn-info { background: #e8f5e9; color: #2e7d32; }

/* 源码查看 */
.source-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  height: 560px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  overflow: hidden;
}
.source-list {
  overflow: auto;
  border-right: 1px solid var(--el-border-color);
  background: var(--el-fill-color-lighter);
}
.source-list-header {
  padding: 10px 14px; font-size: 12px; font-weight: 600;
  color: var(--el-text-color-secondary);
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.source-file-btn {
  display: flex; align-items: center; gap: 6px;
  width: 100%; padding: 8px 12px;
  border: 0; background: transparent;
  text-align: left; cursor: pointer;
  font-size: 12px; color: var(--el-text-color-regular);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.source-file-btn:hover { background: var(--el-fill-color-light); }
.source-file-btn.active { background: var(--el-color-primary-light-9); color: var(--el-color-primary); }
.source-viewer { overflow: auto; }
.source-code {
  margin: 0; padding: 16px;
  white-space: pre; font-size: 12px; line-height: 1.6;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

/* 审核历史 */
.review-item { display: flex; flex-direction: column; gap: 4px; }
.review-action {
  display: inline-block; padding: 2px 10px;
  border-radius: 10px; font-size: 12px; font-weight: 600;
  width: fit-content;
}
.review-approve { background: #e8f5e9; color: #2e7d32; }
.review-reject { background: #fde2e2; color: #c62828; }
.review-publish { background: #e6e6fa; color: #6366f1; }
.review-submit { background: #fef3e2; color: #e6a23c; }
.review-fee { font-size: 12px; color: var(--el-text-color-secondary); }
.review-comment { margin: 4px 0 0; font-size: 13px; color: var(--el-text-color-regular); }

/* 底部操作 */
.drawer-actions {
  display: flex; gap: 10px;
  margin-top: 24px; padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

/* 弹窗 */
.dialog-body { padding: 4px 0; }
.dialog-hint {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 12px 14px; margin-bottom: 16px;
  background: #e6f4ec; border-radius: 8px;
  font-size: 13px; color: #2e7d32;
}
.dialog-hint.warn { background: #fef3e2; color: #e65100; }
.dialog-hint .el-icon { margin-top: 1px; }
.form-note { display: block; margin-top: 6px; color: var(--el-text-color-secondary); font-size: 12px; }

/* Tabs */
.review-tabs :deep(.el-tabs__nav) { padding-left: 4px; }
.review-tabs :deep(.el-tabs__header) { margin-bottom: 16px; }

/* 响应式 */
@media (max-width: 768px) {
  .stats-row { gap: 8px; }
  .stat-card { min-width: 100px; padding: 12px; }
  .stat-value { font-size: 18px; }
  .toolbar { flex-wrap: wrap; }
  .search { width: 100%; }
  .source-layout { grid-template-columns: 1fr; height: auto; }
  .source-list { max-height: 200px; }
}
</style>
