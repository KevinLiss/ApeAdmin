<template>
  <el-card shadow="never">
    <template #header><div class="card-header"><span>插件管理</span><span class="header-note">提交、审核、上架、购买与安装数据</span></div></template>
    <div class="toolbar">
      <el-input v-model="query.keyword" clearable placeholder="搜索插件名称、标识或描述" class="search" @keyup.enter="search" />
      <el-select v-model="query.status" clearable placeholder="全部状态" class="status" @change="search"><el-option label="待审核" value="pending" /><el-option label="已上架" value="approved" /><el-option label="已驳回" value="rejected" /><el-option label="已下架" value="offline" /></el-select>
      <el-button type="primary" @click="search">查询</el-button>
    </div>
    <el-table :data="pluginList" v-loading="loading" stripe>
      <el-table-column prop="display_name" label="插件" min-width="170"><template #default="{ row }"><div>{{ row.display_name }}</div><small>{{ row.name }} · {{ row.version }}</small></template></el-table-column>
      <el-table-column prop="developer.username" label="开发者" width="120" />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag></template></el-table-column>
      <el-table-column label="购买" width="92"><template #default="{ row }">{{ row.metrics?.buyer_count || 0 }} 人<br /><small>{{ row.metrics?.paid_order_count || 0 }} 单</small></template></el-table-column>
      <el-table-column label="安装" width="92"><template #default="{ row }">{{ row.metrics?.install_users || row.install_count || 0 }} 人<br /><small>{{ row.metrics?.download_total || row.download_count || 0 }} 次</small></template></el-table-column>
      <el-table-column label="操作" width="220" fixed="right"><template #default="{ row }">
        <el-button text type="primary" @click="openDetail(row)">详情</el-button>
        <el-button v-if="row.status === 'approved'" text type="warning" @click="offline(row)">下架</el-button>
        <el-button v-if="['offline', 'rejected'].includes(row.status)" text type="success" @click="online(row)">上架</el-button>
        <el-button text type="danger" @click="remove(row)">删除</el-button>
      </template></el-table-column>
      <template #empty><el-empty description="暂无插件提交" /></template>
    </el-table>
    <div class="pager" v-if="total > query.page_size"><el-pagination v-model:current-page="query.page" :page-size="query.page_size" :total="total" layout="prev, pager, next" @current-change="loadList" /></div>
  </el-card>

  <el-drawer v-model="detailVisible" title="插件详情与审核资料" size="620px" destroy-on-close>
    <template v-if="detail"><el-descriptions :column="2" border>
      <el-descriptions-item label="名称">{{ detail.display_name }}</el-descriptions-item><el-descriptions-item label="版本">{{ detail.version }}</el-descriptions-item>
      <el-descriptions-item label="状态"><el-tag :type="statusType(detail.status)">{{ statusLabel(detail.status) }}</el-tag></el-descriptions-item><el-descriptions-item label="开发者">{{ detail.developer?.username || '-' }}</el-descriptions-item>
      <el-descriptions-item label="购买人数">{{ detail.metrics?.buyer_count || 0 }}</el-descriptions-item><el-descriptions-item label="成功订单">{{ detail.metrics?.paid_order_count || 0 }}</el-descriptions-item>
      <el-descriptions-item label="安装人数">{{ detail.metrics?.install_users || detail.install_count || 0 }}</el-descriptions-item><el-descriptions-item label="下载次数">{{ detail.metrics?.download_total || detail.download_count || 0 }}</el-descriptions-item>
      <el-descriptions-item label="成交金额">{{ detail.metrics?.paid_amount || 0 }} USDT</el-descriptions-item><el-descriptions-item label="价格">{{ Number(detail.price) > 0 ? `${detail.price} USDT` : '免费' }}</el-descriptions-item>
      <el-descriptions-item label="平台服务费">{{ detail.service_fee_rate }}%</el-descriptions-item><el-descriptions-item label="当前上架版本">{{ detail.version }}</el-descriptions-item>
      <el-descriptions-item label="驳回原因" :span="2">{{ detail.reject_reason || '-' }}</el-descriptions-item><el-descriptions-item label="描述" :span="2">{{ detail.description || '-' }}</el-descriptions-item>
    </el-descriptions>
    <h4>版本审核与发布</h4>
    <el-table :data="detail.versions || []" size="small" row-key="id">
      <el-table-column prop="version" label="版本" width="100" />
      <el-table-column label="状态" width="110"><template #default="{ row }"><el-tag :type="versionStatusType(row.status)">{{ versionStatusLabel(row.status) }}</el-tag></template></el-table-column>
      <el-table-column label="风险" width="90"><template #default="{ row }">{{ row.analysis_report?.risk_level || '-' }}</template></el-table-column>
      <el-table-column label="文件" min-width="130"><template #default="{ row }"><span v-for="file in row.files" :key="file.id" class="file-link" @click="downloadFile(file)">{{ file.filename }}</span><span v-if="!row.files?.length">-</span></template></el-table-column>
      <el-table-column label="操作" width="245"><template #default="{ row }">
        <el-button text type="primary" @click="openSource(row)">源码</el-button>
        <el-button v-if="row.status === 'submitted'" text type="success" @click="openApprove(row)">通过</el-button>
        <el-button v-if="row.status === 'submitted'" text type="danger" @click="openReject(row)">驳回</el-button>
        <el-button v-if="row.status === 'approved'" text type="primary" @click="publishVersion(row)">发布上架</el-button>
      </template></el-table-column>
      <template #empty><el-empty description="暂无版本" :image-size="60" /></template>
    </el-table>
    <div class="drawer-actions"><el-button v-if="detail.status === 'approved'" type="warning" @click="offline(detail)">下架</el-button><el-button v-if="detail.status === 'offline'" type="success" @click="online(detail)">重新上架</el-button></div>
    </template>
  </el-drawer>

  <el-dialog v-model="approveVisible" title="审核通过" width="480px"><el-form label-position="top"><el-form-item label="平台服务费百分比"><el-input-number v-model="feeRate" :min="0" :max="100" :precision="2" /><div class="form-note">从该插件每笔成交金额中扣除，余额进入开发者待结算收益。</div></el-form-item></el-form><template #footer><el-button @click="approveVisible = false">取消</el-button><el-button type="success" :loading="actionLoading" @click="confirmApprove">确认通过</el-button></template></el-dialog>
  <el-dialog v-model="rejectVisible" title="驳回插件版本" width="480px"><el-input v-model="rejectReason" type="textarea" :rows="4" placeholder="请填写开发者可理解的驳回原因" /><template #footer><el-button @click="rejectVisible = false">取消</el-button><el-button type="danger" :loading="actionLoading" @click="confirmReject">确认驳回</el-button></template></el-dialog>
  <el-dialog v-model="sourceVisible" title="插件源码查看" width="860px"><div class="source-layout"><div class="source-list"><button v-for="file in sourceFiles" :key="file.path" @click="loadSource(file.path)">{{ file.path }}</button></div><pre class="source-code">{{ sourceContent || '选择左侧文件查看内容' }}</pre></div></el-dialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteAdminPlugin, getAdminPluginDetail, getAdminPluginFileDownloadUrl, getAdminPlugins, getAdminVersionSource, getAdminVersionSourceTree, offlinePlugin, onlinePlugin, publishPluginVersion, reviewPluginVersion } from '@/api/apehub_web'

const pluginList = ref<any[]>([]); const loading = ref(false); const total = ref(0); const actionLoading = ref(false)
const query = ref({ status: '', keyword: '', page: 1, page_size: 20 }); const detailVisible = ref(false); const detail = ref<any>(null)
const rejectVisible = ref(false); const rejectReason = ref(''); const rejectTarget = ref<any>(null)
const approveVisible = ref(false); const approveTarget = ref<any>(null); const feeRate = ref(30)
const sourceVisible = ref(false); const sourceTarget = ref<any>(null); const sourceFiles = ref<any[]>([]); const sourceContent = ref('')
const statusLabel = (status: string) => ({ pending: '待审核', approved: '已上架', rejected: '已驳回', offline: '已下架' }[status] || status)
const statusType = (status: string) => ({ pending: 'warning', approved: 'success', rejected: 'danger', offline: 'info' } as any)[status] || 'info'
const versionStatusLabel = (status: string) => ({ draft: '草稿', analyzing: 'AI 分析中', analysis_failed: '分析失败', submitted: '待审核', reviewing: '审核中', approved: '已通过', published: '已发布', rejected: '已驳回', deprecated: '历史版本' } as any)[status] || status
const versionStatusType = (status: string) => ({ submitted: 'warning', approved: 'success', published: 'success', rejected: 'danger', analysis_failed: 'danger', deprecated: 'info' } as any)[status] || 'info'
const formatSize = (size: number) => size >= 1024 * 1024 ? `${(size / 1024 / 1024).toFixed(2)} MB` : `${Math.ceil((size || 0) / 1024)} KB`
const loadList = async () => { loading.value = true; try { const data = await getAdminPlugins(query.value); pluginList.value = data.items || []; total.value = data.total || 0 } finally { loading.value = false } }
const search = () => { query.value.page = 1; loadList() }
const openDetail = async (row: any) => { detailVisible.value = true; detail.value = null; try { detail.value = await getAdminPluginDetail(row.id) } catch { detailVisible.value = false } }
const refresh = async (pluginId?: number) => { await loadList(); if (pluginId && detailVisible.value) detail.value = await getAdminPluginDetail(pluginId) }
const openReject = (row: any) => { rejectTarget.value = row; rejectReason.value = ''; rejectVisible.value = true }
const confirmReject = async () => { if (!rejectReason.value.trim() || !detail.value) return ElMessage.warning('请填写驳回原因'); actionLoading.value = true; try { await reviewPluginVersion(detail.value.id, rejectTarget.value.id, { action: 'reject', reason: rejectReason.value.trim() }); ElMessage.success('版本已驳回'); rejectVisible.value = false; await refresh(detail.value.id) } finally { actionLoading.value = false } }
const openApprove = (version: any) => { approveTarget.value = version; feeRate.value = Number(detail.value?.service_fee_rate || 30); approveVisible.value = true }
const confirmApprove = async () => { if (!detail.value || !approveTarget.value) return; actionLoading.value = true; try { await reviewPluginVersion(detail.value.id, approveTarget.value.id, { action: 'approve', service_fee_rate: feeRate.value }); ElMessage.success('版本已通过，请确认后发布上架'); approveVisible.value = false; await refresh(detail.value.id) } finally { actionLoading.value = false } }
const publishVersion = async (version: any) => { if (!detail.value) return; await ElMessageBox.confirm(`确认发布 ${version.version} 至插件市场？`, '发布版本', { type: 'warning' }); await publishPluginVersion(detail.value.id, version.id); ElMessage.success('版本已发布'); await refresh(detail.value.id) }
const openSource = async (version: any) => { if (!detail.value) return; sourceTarget.value = version; sourceContent.value = ''; const data = await getAdminVersionSourceTree(detail.value.id, version.id); sourceFiles.value = data.files || []; sourceVisible.value = true }
const loadSource = async (path: string) => { if (!detail.value || !sourceTarget.value) return; const data = await getAdminVersionSource(detail.value.id, sourceTarget.value.id, path); sourceContent.value = data.content || '' }
const offline = async (row: any) => { await ElMessageBox.confirm(`确认下架「${row.display_name}」？已购买用户仍可下载。`, '下架插件', { type: 'warning' }); await offlinePlugin(row.id); ElMessage.success('插件已下架'); await refresh(row.id) }
const online = async (row: any) => { await onlinePlugin(row.id); ElMessage.success('插件已上架'); await refresh(row.id) }
const remove = async (row: any) => { await ElMessageBox.confirm(`确认删除「${row.display_name}」？有购买记录的插件会被系统保护，无法删除。`, '删除插件', { type: 'warning' }); await deleteAdminPlugin(row.id); ElMessage.success('插件已删除'); detailVisible.value = false; await loadList() }
const downloadFile = async (file: any) => { if (!detail.value) return; const response = await fetch(getAdminPluginFileDownloadUrl(detail.value.id, file.id), { headers: { Authorization: `Bearer ${localStorage.getItem('apeadmin_token') || ''}` } }); if (!response.ok) return ElMessage.error('文件下载失败'); const blob = await response.blob(); const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = file.filename; link.click(); URL.revokeObjectURL(url) }
onMounted(loadList)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }.header-note, small { color: var(--el-text-color-secondary); font-size: 12px; }.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }.search { width: 280px; }.status { width: 130px; }.pager { margin-top: 16px; display: flex; justify-content: center; }.drawer-actions { display: flex; gap: 10px; margin-top: 22px; }
.file-link { display:block; color:var(--el-color-primary); cursor:pointer; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }.form-note { margin-top:8px; color:var(--el-text-color-secondary); font-size:12px; }.source-layout { display:grid; grid-template-columns:260px minmax(0,1fr); height:560px; border:1px solid var(--el-border-color); }.source-list { overflow:auto; border-right:1px solid var(--el-border-color); }.source-list button { display:block; width:100%; padding:8px 10px; border:0; background:transparent; text-align:left; cursor:pointer; color:var(--el-text-color-regular); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }.source-list button:hover { background:var(--el-fill-color-light); }.source-code { margin:0; padding:14px; overflow:auto; white-space:pre; font-size:12px; line-height:1.6; background:var(--el-fill-color-lighter); }
</style>
