<template>
  <div class="plugins-admin">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card pending" style="cursor:pointer" @click="filterByStatus('pending')">
        <div class="stat-icon"><el-icon><Document /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待审核</div>
        </div>
      </div>
      <div class="stat-card approved" style="cursor:pointer" @click="filterByStatus('approved')">
        <div class="stat-icon"><el-icon><CircleCheck /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.approved }}</div>
          <div class="stat-label">已上架</div>
        </div>
      </div>
      <div class="stat-card rejected" style="cursor:pointer" @click="filterByStatus('rejected')">
        <div class="stat-icon"><el-icon><CircleClose /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.rejected }}</div>
          <div class="stat-label">已驳回</div>
        </div>
      </div>
      <div class="stat-card offline" style="cursor:pointer" @click="filterByStatus('offline')">
        <div class="stat-icon"><el-icon><Remove /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.offline }}</div>
          <div class="stat-label">已下架</div>
        </div>
      </div>
      <div class="stat-card revenue">
        <div class="stat-icon"><el-icon><Money /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ fmtMoney(stats.totalRevenue) }} <small>USDT</small></div>
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
            <span v-if="Number(row.price) > 0" class="price-tag">{{ fmtMoney(row.price) }} USDT</span>
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
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click.stop="openEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'pending'" text type="primary" @click.stop="openDetail(row)">审核</el-button>
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
              <span><el-icon><PriceTag /></el-icon> {{ Number(detail.price) > 0 ? `${fmtMoney(detail.price)} USDT` : '免费' }}</span>
              <span><el-icon><Folder /></el-icon> {{ detail.category }}</span>
              <span>📊 服务费 {{ fmtMoney(detail.service_fee_rate) }}%</span>
            </div>
          </div>
          <el-tag :type="statusType(detail.status)" effect="dark" size="large" round>{{ statusLabel(detail.status) }}</el-tag>
        </div>

        <!-- 指标条 -->
        <div class="metrics-bar">
          <div class="metric-item"><span class="metric-val">{{ detail.metrics?.buyer_count || 0 }}</span><span class="metric-lbl">购买人数</span></div>
          <div class="metric-item"><span class="metric-val">{{ detail.metrics?.paid_order_count || 0 }}</span><span class="metric-lbl">成交订单</span></div>
          <div class="metric-item"><span class="metric-val">{{ fmtMoney(detail.metrics?.paid_amount) }}</span><span class="metric-lbl">成交额 USDT</span></div>
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
                  <el-button v-if="row.status === 'published'" text type="warning" @click="unpublishVersion(row)">下架</el-button>
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
                <p>共 {{ currentAIReport.file_count }} 个文件，总大小 {{ formatSize(currentAIReport.uncompressed_size || currentAIReport.total_size || 0) }}</p>
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
                  <span v-if="review.service_fee_rate" class="review-fee">服务费 {{ fmtMoney(review.service_fee_rate) }}%</span>
                  <p v-if="review.comment" class="review-comment">{{ review.comment }}</p>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无审核记录" :image-size="80" />
          </el-tab-pane>
        </el-tabs>

        <!-- 底部操作 -->
        <div class="drawer-actions">
          <el-button type="primary" @click="openEdit(detail)">
            <el-icon><Edit /></el-icon> 编辑插件
          </el-button>
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

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editVisible" title="编辑插件" width="860px" destroy-on-close class="edit-dialog">
      <el-tabs v-model="editTab" class="edit-tabs">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="editForm" label-width="120px" class="edit-form">
            <el-form-item label="显示名称">
              <el-input v-model="editForm.display_name" />
            </el-form-item>
            <el-form-item label="插件标识">
              <el-input v-model="editForm.name" />
            </el-form-item>
            <el-form-item label="Slug">
              <el-input v-model="editForm.slug" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="editForm.description" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item label="分类">
              <el-select v-model="editForm.category" placeholder="选择分类">
                <el-option label="工具" value="工具" />
                <el-option label="AI" value="AI" />
                <el-option label="电商" value="电商" />
                <el-option label="仪表盘" value="仪表盘" />
                <el-option label="系统增强" value="系统增强" />
              </el-select>
            </el-form-item>
            <el-form-item label="版本号">
              <el-input v-model="editForm.version" />
            </el-form-item>
            <el-form-item label="标签">
              <el-input v-model="editForm.tags" placeholder="逗号分隔" />
            </el-form-item>
            <el-form-item label="图标">
              <div class="icon-edit-row">
                <el-upload
                  :show-file-list="false"
                  :before-upload="(file: any) => uploadIcon(file)"
                  accept="image/*">
                  <el-button text type="primary"><el-icon><Upload /></el-icon> 上传图标</el-button>
                </el-upload>
                <div v-if="editForm.icon" class="icon-preview">
                  <img :src="editForm.icon" alt="icon" class="icon-img" />
                  <el-button text type="danger" @click="editForm.icon = ''">清除</el-button>
                </div>
                <span class="form-hint">或填写 URL</span>
                <el-input v-model="editForm.icon" placeholder="图标 URL 或文字" style="flex:1;min-width:200px" />
              </div>
            </el-form-item>
            <el-form-item label="价格 (USDT)">
              <el-input-number v-model="editForm.price" :min="0" :precision="2" :step="1" />
            </el-form-item>
            <el-form-item label="服务费率 %">
              <el-input-number v-model="editForm.service_fee_rate" :min="0" :max="100" :precision="2" :step="5" />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="editForm.status">
                <el-option label="待审核" value="pending" />
                <el-option label="已上架" value="approved" />
                <el-option label="已驳回" value="rejected" />
                <el-option label="已下架" value="offline" />
              </el-select>
            </el-form-item>
            <el-form-item label="开发者">
              <el-select v-model="editForm.developer_id" filterable placeholder="选择开发者" style="width:100%">
                <el-option v-for="u in developerList" :key="u.id" :label="`${u.username}（${u.nickname || u.email || 'ID:' + u.id}）`" :value="u.id" />
              </el-select>
            </el-form-item>
            <el-divider content-position="left">系统统计（只读）</el-divider>
            <div class="readonly-stats">
              <div class="stat-item"><span class="stat-lbl">下载次数</span><span class="stat-val">{{ editForm.download_count ?? 0 }}</span></div>
              <div class="stat-item"><span class="stat-lbl">安装次数</span><span class="stat-val">{{ editForm.install_count ?? 0 }}</span></div>
              <div class="stat-item"><span class="stat-lbl">评分</span><span class="stat-val">{{ editForm.rating_avg ?? 0 }}</span></div>
              <div class="stat-item"><span class="stat-lbl">评分人数</span><span class="stat-val">{{ editForm.rating_count ?? 0 }}</span></div>
            </div>
          </el-form>
        </el-tab-pane>

        <!-- Demo 管理 -->
        <el-tab-pane label="Demo 管理" name="demos">
          <div class="demo-edit-list">
            <div v-if="!editForm.demos?.length" class="demo-empty-hint">
              <el-icon><InfoFilled /></el-icon>
              <span>暂无 Demo。点击下方按钮添加 H5、小程序、后台等演示入口。</span>
            </div>
            <div v-for="(demo, idx) in editForm.demos" :key="idx" class="demo-edit-card">
              <div class="demo-card-header">
                <el-select v-model="demo.demo_type" placeholder="类型" style="width:140px" @change="onDemoTypeChange(demo)">
                  <el-option label="H5 网页" value="h5" />
                  <el-option label="小程序" value="miniprogram" />
                  <el-option label="管理后台" value="admin" />
                  <el-option label="PC 客户端" value="pc" />
                  <el-option label="API 文档" value="api" />
                  <el-option label="MCP 工具" value="mcp" />
                </el-select>
                <el-input v-model="demo.title" placeholder="Demo 标题（如：在线体验）" style="flex:1;margin-left:12px" />
                <el-button text type="danger" @click="editForm.demos.splice(idx, 1)"><el-icon><Delete /></el-icon> 删除</el-button>
              </div>
              <div class="demo-card-body">
                <!-- 二维码类型：H5 / 小程序 → 上传二维码图片 -->
                <template v-if="['h5', 'miniprogram'].includes(demo.demo_type)">
                  <div class="qr-upload-row">
                    <div class="qr-preview" v-if="demo.qr_image">
                      <img :src="demo.qr_image" alt="二维码" class="qr-img" />
                      <el-button text type="danger" @click="demo.qr_image = ''">移除</el-button>
                    </div>
                    <el-upload
                      :show-file-list="false"
                      :before-upload="(file: any) => uploadDemoQr(file, demo)"
                      accept="image/*">
                      <el-button type="primary" plain><el-icon><Upload /></el-icon> 上传{{ demo.demo_type === 'h5' ? ' H5 ' : ' 小程序 ' }}二维码</el-button>
                    </el-upload>
                    <span class="form-hint">用户扫码即可访问 Demo</span>
                  </div>
                  <el-input v-model="demo.url" placeholder="扫码后跳转的 URL（选填）" style="margin-top:10px">
                    <template #prepend>URL</template>
                  </el-input>
                </template>
                <!-- 链接类型：管理后台 / PC / API / MCP → 填写链接 -->
                <template v-else>
                  <el-input v-model="demo.url" placeholder="请输入 Demo 访问链接（如 https://...）">
                    <template #prepend>链接</template>
                  </el-input>
                </template>
              </div>
            </div>
            <el-button type="primary" plain @click="editForm.demos.push({ demo_type: 'h5', title: '', url: '', qr_image: '' })">
              <el-icon><Plus /></el-icon> 添加 Demo
            </el-button>
          </div>
        </el-tab-pane>

        <!-- 截图/Logo -->
        <el-tab-pane label="截图/Logo" name="media">
          <div class="media-edit-section">
            <div class="media-upload-bar">
              <el-upload
                :show-file-list="false"
                :before-upload="(file: any) => uploadMedia(file, 'carousel')"
                accept="image/*">
                <el-button type="primary" plain><el-icon><Upload /></el-icon> 上传截图</el-button>
              </el-upload>
              <el-upload
                :show-file-list="false"
                :before-upload="(file: any) => uploadMedia(file, 'logo')"
                accept="image/*">
                <el-button type="success" plain><el-icon><Upload /></el-icon> 上传 Logo</el-button>
              </el-upload>
            </div>
            <div class="media-grid">
              <div v-for="m in editMediaList" :key="m.id" class="media-card">
                <img :src="m.url" :alt="m.alt_text" />
                <div class="media-card-info">
                  <el-tag size="small" :type="m.media_type === 'logo' ? 'success' : 'info'">{{ m.media_type }}</el-tag>
                  <el-button text type="danger" @click="deleteMedia(m)">删除</el-button>
                </div>
              </div>
              <el-empty v-if="!editMediaList.length" description="暂无截图" :image-size="60" />
            </div>
          </div>
        </el-tab-pane>

        <!-- 文件管理 -->
        <el-tab-pane label="文件管理" name="files">
          <div class="files-edit-section">
            <div class="files-upload-hint">
              <el-icon><InfoFilled /></el-icon>
              <span>插件包(ZIP) 会关联到最新版本，文档可关联指定版本。</span>
            </div>
            <div class="files-upload-bar">
              <el-upload
                :show-file-list="false"
                :before-upload="(file: any) => uploadFile(file, 'package')"
                accept=".zip">
                <el-button type="primary" plain><el-icon><Upload /></el-icon> 上传插件包 (ZIP)</el-button>
              </el-upload>
              <el-upload
                :show-file-list="false"
                :before-upload="(file: any) => uploadFile(file, 'doc')">
                <el-button type="info" plain><el-icon><Upload /></el-icon> 上传文档</el-button>
              </el-upload>
            </div>
            <el-table :data="editFileList" size="small" style="margin-top:12px">
              <el-table-column prop="filename" label="文件名" min-width="180" />
              <el-table-column prop="file_type" label="类型" width="90">
                <template #default="{ row }">
                  <el-tag size="small" :type="row.file_type === 'package' ? 'primary' : 'info'">{{ row.file_type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="关联版本" width="130">
                <template #default="{ row }">
                  <span v-if="row.version_id && versionName(row.version_id)" class="version-link">v{{ versionName(row.version_id) }}</span>
                  <span v-else class="muted-text">-</span>
                </template>
              </el-table-column>
              <el-table-column label="大小" width="100">
                <template #default="{ row }">{{ formatSize(row.size) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="90">
                <template #default="{ row }">
                  <el-button text type="danger" @click="deleteFile(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

          <!-- 版本文档 -->
          <el-tab-pane label="版本文档" name="version">
            <div class="version-edit-section">
              <el-select v-model="editVersionId" placeholder="选择版本" style="margin-bottom:16px;width:240px" @change="onVersionSelect" popper-class="version-select-popper">
                <el-option v-for="v in editVersionList" :key="v.id" :label="`v${v.version}（${versionStatusLabel(v.status)}）`" :value="v.id">
                  <span style="float:left">v{{ v.version }}</span>
                  <span style="float:right;color:var(--el-text-color-secondary);font-size:12px">{{ versionStatusLabel(v.status) }}</span>
                </el-option>
              </el-select>
              <template v-if="editVersionId">
                <!-- 关联文件展示 -->
                <div v-if="currentVersionFiles.length" class="version-files-box">
                  <div class="version-files-title">
                    <el-icon><Folder /></el-icon> 关联文件
                    <el-button text size="small" type="primary" style="margin-left:auto" @click="triggerVersionUpload">更换文件</el-button>
                  </div>
                  <div v-for="f in currentVersionFiles" :key="f.id" class="version-file-row">
                    <el-tag size="small" :type="f.file_type === 'package' ? 'primary' : 'info'">{{ f.file_type }}</el-tag>
                    <span class="file-name">{{ f.filename }}</span>
                    <span class="file-size">{{ formatSize(f.size) }}</span>
                    <el-button text size="small" type="danger" :icon="Delete" @click="removeVersionFile(f)">删除</el-button>
                  </div>
                  <input v-show="false" ref="versionUploadInput" type="file" accept=".zip,.gz" @change="handleVersionUpload($event)" />
                </div>
                <div v-else class="version-files-box empty">
                  <el-icon><Warning /></el-icon>
                  <span>该版本暂无关联文件，请在「文件管理」Tab 上传 ZIP 或文档。</span>
                  <el-button text size="small" type="primary" @click="triggerVersionUpload">上传文件</el-button>
                  <input v-show="false" ref="versionUploadInput" type="file" accept=".zip,.gz" @change="handleVersionUpload($event)" />
                </div>
                <el-form label-width="100px" style="margin-top:16px">
                  <el-form-item label="版本号">
                    <el-input v-model="editVersionForm.version" />
                  </el-form-item>
                  <el-form-item label="兼容性">
                    <el-input v-model="editVersionForm.compatibility" placeholder="如：ApeAdmin v1.4+" />
                  </el-form-item>
                  <el-form-item label="更新日志">
                    <el-input v-model="editVersionForm.changelog" type="textarea" :rows="4" placeholder="本次更新内容" />
                  </el-form-item>
                  <el-form-item label="技术文档">
                    <el-input v-model="editVersionForm.documentation" type="textarea" :rows="10" placeholder="Markdown 格式" />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" :loading="versionSaving" @click="saveVersion">保存版本文档</el-button>
                  </el-form-item>
                </el-form>
              </template>
              <el-empty v-else description="请选择版本编辑文档" :image-size="60" />
            </div>
          </el-tab-pane>

          <!-- MCP 工具 -->
          <el-tab-pane label="MCP 工具" name="mcp">
            <div class="mcp-edit-section">
              <div class="mcp-edit-hint">
                <el-icon><InfoFilled /></el-icon>
                <span>配置该插件对外暴露的 MCP 工具元数据（JSON 格式）。AI 助手可通过这些工具调用插件能力。运行时注册由插件代码自动完成，此字段用于记录和展示。</span>
              </div>
              <el-input
                v-model="mcpToolsJson"
                type="textarea"
                :rows="16"
                placeholder='例如：[{"name":"market_search","description":"搜索市场插件","category":"apehub_web","permissions":[]}]'
                style="font-family: monospace; font-size: 12px;" />
              <div class="mcp-edit-actions">
                <el-button type="primary" :loading="editSaving" @click="saveMcpTools">保存 MCP 配置</el-button>
                <el-button @click="formatMcpJson">格式化 JSON</el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      <template #footer>
        <el-button @click="editVisible = false">关闭</el-button>
        <el-button v-if="editTab === 'basic' || editTab === 'demos'" type="primary" :loading="editSaving" @click="saveEdit">保存基本信息</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, CircleCheck, CircleClose, Remove, Money, Search, User, PriceTag, Folder, Warning, WarningFilled, InfoFilled, Promotion, Edit, Plus, Upload, Delete } from '@element-plus/icons-vue'
import {
  deleteAdminPlugin, getAdminPluginDetail, getAdminPluginFileDownloadUrl,
  getAdminPlugins, getAdminVersionSource, getAdminVersionSourceTree,
  offlinePlugin, onlinePlugin, publishPluginVersion, unpublishPluginVersion, reviewPluginVersion,
  updateAdminPlugin, adminUploadMedia, adminDeleteMedia, adminUploadFile, adminDeleteFile,
  updateAdminVersion, adminUploadDemoQr, getAdminUsers,
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

// 金额统一格式化：最多 2 位小数，去除多余的 0（如 10.00000000 → 10，10.50000000 → 10.5）
const fmtMoney = (v: any) => {
  const n = Number(v || 0)
  if (!isFinite(n)) return '0'
  return n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

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
const filterByStatus = (status: string) => {
  query.value.status = query.value.status === status ? '' : status
  search()
}

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
const unpublishVersion = async (version: any) => {
  if (!detail.value) return
  await ElMessageBox.confirm(`确认下架 v${version.version}？下架后用户将无法购买此版本，已购买用户不受影响。若无其他已发布版本，插件将整体下架。`, '下架版本', { type: 'warning' })
  await unpublishPluginVersion(detail.value.id, version.id)
  ElMessage.success('版本已下架')
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

// ---- 编辑弹窗 ----
const editVisible = ref(false)
const editTab = ref('basic')
const editSaving = ref(false)
const editForm = ref<any>({})
const editMediaList = ref<any[]>([])
const editFileList = ref<any[]>([])
const editVersionList = ref<any[]>([])
const editVersionId = ref<number>(0)
const editVersionForm = ref<any>({})
const versionSaving = ref(false)
const developerList = ref<any[]>([])
const mcpToolsJson = ref('')

// 加载开发者列表（管理员可筛选绑定）
const loadDevelopers = async () => {
  try {
    const data = await getAdminUsers({ page: 1, page_size: 100 })
    developerList.value = data.items || data || []
  } catch {
    developerList.value = []
  }
}

// 上传图标 — 复用 adminUploadMedia 接口，media_type=logo 时后端自动更新 plugin.icon
const uploadIcon = async (file: any) => {
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await adminUploadMedia(editForm.value.id, formData, { media_type: 'logo' })
    // 后端已将 plugin.icon 更新为 url，前端同步展示
    editForm.value.icon = res.url
    ElMessage.success('图标上传成功')
  } catch (e: any) {
    ElMessage.error(e.message || '图标上传失败')
  }
  return false
}

// 上传 Demo 二维码 — 调用 adminUploadDemoQr，拿到 url 后赋值给 demo.qr_image
const uploadDemoQr = async (file: any, demo: any) => {
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await adminUploadDemoQr(editForm.value.id, formData)
    demo.qr_image = res.url
    ElMessage.success('二维码上传成功')
  } catch (e: any) {
    ElMessage.error(e.message || '二维码上传失败')
  }
  return false
}

// 切换 Demo 类型时清空不适用字段
const onDemoTypeChange = (demo: any) => {
  if (['h5', 'miniprogram'].includes(demo.demo_type)) {
    // 二维码类型，保留 qr_image，清空 url 是可选的
  } else {
    // 链接类型，清空二维码
    demo.qr_image = ''
  }
}

// 根据版本 ID 查找版本号
const versionName = (versionId: number) => {
  const v = editVersionList.value.find((x: any) => x.id === versionId)
  return v ? v.version : ''
}

// 当前选中版本关联的文件列表
const currentVersionFiles = computed(() => {
  const v = editVersionList.value.find((x: any) => x.id === editVersionId.value)
  return v?.files || []
})

const openEdit = async (row: any) => {
  editVisible.value = true
  editTab.value = 'basic'
  editVersionId.value = 0
  editVersionForm.value = {}
  try {
    const d = await getAdminPluginDetail(row.id)
    editForm.value = {
      id: d.id,
      display_name: d.display_name,
      name: d.name,
      slug: d.slug,
      description: d.description,
      category: d.category,
      version: d.version,
      tags: d.tags,
      icon: d.icon,
      price: Number(d.price),
      service_fee_rate: Number(d.service_fee_rate),
      status: d.status,
      developer_id: d.developer_id,
      download_count: d.download_count,
      install_count: d.install_count || 0,
      rating_avg: d.rating_avg,
      rating_count: d.rating_count,
      demos: (d.demos || []).map((x: any) => ({ demo_type: x.demo_type, title: x.title, url: x.url, qr_image: x.qr_image })),
    }
    editMediaList.value = d.media || []
    editFileList.value = d.files || []
    editVersionList.value = d.versions || []
    mcpToolsJson.value = d.mcp_tools ? JSON.stringify(d.mcp_tools, null, 2) : '[]'
    // 延迟加载开发者列表（仅在首次打开时）
    if (!developerList.value.length) await loadDevelopers()
  } catch {
    ElMessage.error('加载插件详情失败')
  }
}

const saveEdit = async () => {
  editSaving.value = true
  try {
    await updateAdminPlugin(editForm.value.id, editForm.value)
    ElMessage.success('插件信息已保存')
    await refresh(editForm.value.id)
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败')
  } finally { editSaving.value = false }
}

const uploadMedia = async (file: any, mediaType: string) => {
  const formData = new FormData()
  formData.append('file', file)
  try {
    await adminUploadMedia(editForm.value.id, formData, { media_type: mediaType })
    ElMessage.success('图片上传成功')
    // 刷新 media 列表
    const d = await getAdminPluginDetail(editForm.value.id)
    editMediaList.value = d.media || []
  } catch (e: any) {
    ElMessage.error(e.message || '上传失败')
  }
  return false // 阻止 el-upload 默认上传
}

const deleteMedia = async (m: any) => {
  await ElMessageBox.confirm(`确认删除图片「${m.alt_text || m.url}」？`, '删除图片', { type: 'warning' })
  await adminDeleteMedia(editForm.value.id, m.id)
  ElMessage.success('图片已删除')
  editMediaList.value = editMediaList.value.filter((x: any) => x.id !== m.id)
}

const uploadFile = async (file: any, fileType: string) => {
  const formData = new FormData()
  formData.append('file', file)
  try {
    await adminUploadFile(editForm.value.id, formData, { file_type: fileType })
    ElMessage.success('文件上传成功')
    const d = await getAdminPluginDetail(editForm.value.id)
    editFileList.value = d.files || []
    editVersionList.value = d.versions || []
  } catch (e: any) {
    ElMessage.error(e.message || '上传失败')
  }
  return false
}

const deleteFile = async (f: any) => {
  await ElMessageBox.confirm(`确认删除文件「${f.filename}」？`, '删除文件', { type: 'warning' })
  await adminDeleteFile(editForm.value.id, f.id)
  ElMessage.success('文件已删除')
  editFileList.value = editFileList.value.filter((x: any) => x.id !== f.id)
}

const onVersionSelect = () => {
  const v = editVersionList.value.find((x: any) => x.id === editVersionId.value)
  if (v) {
    editVersionForm.value = {
      version: v.version,
      compatibility: v.compatibility || '',
      changelog: v.changelog || '',
      documentation: v.documentation || '',
    }
  }
}

// 版本文档 Tab：关联文件的上传/删除
const versionUploadInput = ref<HTMLInputElement | null>(null)
const triggerVersionUpload = () => versionUploadInput.value?.click()
const handleVersionUpload = async (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !editForm.value.id || !editVersionId.value) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    await adminUploadFile(editForm.value.id, formData, { file_type: 'package', version_id: editVersionId.value })
    ElMessage.success('文件上传成功')
    const d = await getAdminPluginDetail(editForm.value.id)
    editVersionList.value = d.versions || []
  } catch (err: any) {
    ElMessage.error(err.message || '上传失败')
  }
  input.value = ''
}
const removeVersionFile = async (f: any) => {
  await ElMessageBox.confirm(`确认删除文件「${f.filename}」？`, '删除文件', { type: 'warning' })
  await adminDeleteFile(editForm.value.id, f.id)
  ElMessage.success('文件已删除')
  const d = await getAdminPluginDetail(editForm.value.id)
  editVersionList.value = d.versions || []
}

const saveVersion = async () => {
  versionSaving.value = true
  try {
    await updateAdminVersion(editForm.value.id, editVersionId.value, editVersionForm.value)
    ElMessage.success('版本文档已保存')
    await refresh(editForm.value.id)
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败')
  } finally { versionSaving.value = false }
}

// MCP 工具配置
const saveMcpTools = async () => {
  let parsed: any
  try {
    parsed = JSON.parse(mcpToolsJson.value || '[]')
  } catch {
    return ElMessage.error('JSON 格式错误，请检查')
  }
  editSaving.value = true
  try {
    await updateAdminPlugin(editForm.value.id, { mcp_tools: parsed })
    ElMessage.success('MCP 工具配置已保存')
    await refresh(editForm.value.id)
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败')
  } finally { editSaving.value = false }
}

const formatMcpJson = () => {
  try {
    const parsed = JSON.parse(mcpToolsJson.value || '[]')
    mcpToolsJson.value = JSON.stringify(parsed, null, 2)
    ElMessage.success('JSON 格式化完成')
  } catch {
    ElMessage.error('JSON 格式错误，无法格式化')
  }
}

onMounted(() => {
  loadList()
  loadDevelopers()
})
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

/* 编辑弹窗 */
.edit-dialog :deep(.el-dialog__body) { padding: 0 20px; }
.edit-tabs :deep(.el-tabs__header) { margin-bottom: 16px; }
.edit-form { max-width: 640px; }
.edit-form :deep(.el-form-item) { margin-bottom: 16px; }

.demo-edit-list { display: flex; flex-direction: column; gap: 10px; }
.demo-edit-item {
  display: flex; gap: 8px; align-items: center;
  padding: 10px; border: 1px solid var(--el-border-color-lighter); border-radius: 8px;
}

.media-edit-section { }
.media-upload-bar { display: flex; gap: 12px; margin-bottom: 16px; }
.media-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}
.media-card {
  border: 1px solid var(--el-border-color-lighter); border-radius: 8px; overflow: hidden;
}
.media-card img { width: 100%; height: 140px; object-fit: cover; display: block; }
.media-card-info {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 12px;
}

.files-edit-section { }
.files-edit-section .el-upload { display: inline-block; margin-right: 12px; }

.version-edit-section { }

/* MCP 工具编辑 */
.mcp-edit-section { }
.mcp-edit-hint {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 10px 14px; margin-bottom: 12px;
  background: var(--el-fill-color-lighter); border-radius: 8px;
  font-size: 12px; color: var(--el-text-color-secondary); line-height: 1.6;
}
.mcp-edit-actions { display: flex; gap: 10px; margin-top: 12px; }

/* 版本选择下拉在 dialog 之上显示 */
:global(.version-select-popper) {
  z-index: 3000 !important;
}

/* ---- 编辑弹窗新增样式 ---- */

/* 图标编辑行 */
.icon-edit-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.icon-edit-row .icon-preview { display: flex; align-items: center; gap: 6px; }
.icon-edit-row .icon-img { width: 40px; height: 40px; border-radius: 8px; object-fit: cover; border: 1px solid var(--el-border-color-lighter); }
.form-hint { font-size: 12px; color: var(--el-text-color-secondary); }

/* 只读统计区 */
.readonly-stats {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
  margin-bottom: 12px;
}
.readonly-stats .stat-item {
  display: flex; flex-direction: column; align-items: center;
  padding: 10px 8px; border-radius: 8px;
  background: var(--el-fill-color-lighter);
  border: 1px solid var(--el-border-color-lighter);
}
.readonly-stats .stat-lbl { font-size: 11px; color: var(--el-text-color-secondary); }
.readonly-stats .stat-val { font-size: 18px; font-weight: 700; color: var(--el-text-color-primary); }

/* Demo 编辑卡片 */
.demo-edit-list { display: flex; flex-direction: column; gap: 12px; }
.demo-empty-hint {
  display: flex; align-items: center; gap: 8px;
  padding: 20px; border: 1px dashed var(--el-border-color); border-radius: 8px;
  color: var(--el-text-color-secondary); font-size: 13px;
}
.demo-edit-card {
  border: 1px solid var(--el-border-color-lighter); border-radius: 10px;
  padding: 14px; background: var(--el-fill-color-lighter);
}
.demo-card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.demo-card-body { display: flex; flex-direction: column; gap: 10px; }

/* 二维码上传 */
.qr-upload-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.qr-preview { display: flex; align-items: center; gap: 6px; }
.qr-img { width: 80px; height: 80px; border-radius: 6px; border: 1px solid var(--el-border-color-lighter); object-fit: cover; }

/* 文件管理上传提示 */
.files-upload-hint {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; margin-bottom: 12px;
  background: var(--el-fill-color-lighter); border-radius: 8px;
  font-size: 12px; color: var(--el-text-color-secondary);
}
.files-upload-bar { display: flex; gap: 12px; margin-bottom: 8px; }
.version-link { color: var(--el-color-primary); font-weight: 600; font-size: 12px; }
.muted-text { color: var(--el-text-color-placeholder); font-size: 12px; }

/* 版本文档关联文件 */
.version-files-box {
  border: 1px solid var(--el-border-color-lighter); border-radius: 8px;
  padding: 12px 14px; margin-bottom: 12px;
}
.version-files-box.empty {
  display: flex; align-items: center; gap: 8px;
  background: var(--el-fill-color-lighter);
  color: var(--el-text-color-secondary); font-size: 12px;
}
.version-files-title {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 600; color: var(--el-text-color-primary);
  margin-bottom: 8px; white-space: nowrap;
}
.version-file-row {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 0; font-size: 12px;
}
.version-file-row .file-name { flex: 1; color: var(--el-text-color-regular); }
.version-file-row .file-size { color: var(--el-text-color-secondary); }

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
