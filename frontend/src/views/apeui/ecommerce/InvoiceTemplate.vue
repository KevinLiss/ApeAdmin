<template>
  <div class="invoice-template-page">
    <PageHeader title="Invoice" :breadcrumb="['APEUI库', 'Ecommerce', 'Invoice']" />

    <el-row :gutter="30">
      <!-- 左侧：发票卡片 -->
      <el-col :span="18">
        <div class="invoice-paper">
          <!-- 顶部：公司信息 + 发票编号 -->
          <div class="invoice-top">
            <div class="company-info">
              <div class="company-logo">
                <el-icon :size="36" color="#534686"><Shop /></el-icon>
              </div>
              <div>
                <h2 class="company-name">ApeAdmin Store</h2>
                <p class="company-meta">广州市天河区珠江新城华夏路30号</p>
                <p class="company-meta">contact@apeadmin.com · +86 020-8888-0000</p>
              </div>
            </div>
            <div class="invoice-meta">
              <h1 class="invoice-title">INVOICE</h1>
              <div class="meta-row"><span class="meta-label">发票编号：</span><span class="meta-value">INV-2026-0821-001</span></div>
              <div class="meta-row"><span class="meta-label">开具日期：</span><span class="meta-value">2026-08-21</span></div>
              <div class="meta-row"><span class="meta-label">到期日期：</span><span class="meta-value">2026-09-05</span></div>
            </div>
          </div>

          <div class="invoice-divider"></div>

          <!-- 客户信息 -->
          <div class="customer-section">
            <div class="customer-block">
              <div class="block-label">账单接收 (Bill To)</div>
              <div class="customer-name">张伟</div>
              <div class="customer-detail">广东省广州市天河区珠江新城华夏路30号</div>
              <div class="customer-detail">zhangwei@example.com</div>
              <div class="customer-detail">+86 138-0000-0001</div>
            </div>
            <div class="customer-block">
              <div class="block-label">发货信息 (Ship To)</div>
              <div class="customer-name">张伟</div>
              <div class="customer-detail">广东省广州市天河区珠江新城华夏路30号</div>
              <div class="customer-detail">顺丰快递 · SF10260821001</div>
              <div class="customer-detail">预计送达：2026-08-23</div>
            </div>
          </div>

          <!-- 商品表格 -->
          <table class="invoice-table">
            <thead>
              <tr>
                <th class="col-desc">商品描述</th>
                <th class="col-qty">数量</th>
                <th class="col-price">单价</th>
                <th class="col-amount">金额</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, i) in items" :key="i">
                <td class="col-desc">
                  <div class="item-name">{{ item.name }}</div>
                  <div class="item-sku">SKU: {{ item.sku }}</div>
                </td>
                <td class="col-qty">{{ item.qty }}</td>
                <td class="col-price">${{ item.price.toFixed(2) }}</td>
                <td class="col-amount">${{ (item.price * item.qty).toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>

          <!-- 费用汇总 -->
          <div class="invoice-summary">
            <div class="summary-content">
              <div class="summary-line">
                <span>小计 (Subtotal)</span>
                <span>${{ subtotal.toFixed(2) }}</span>
              </div>
              <div class="summary-line">
                <span>税费 (Tax 8%)</span>
                <span>${{ tax.toFixed(2) }}</span>
              </div>
              <div class="summary-line">
                <span>运费 (Shipping)</span>
                <span>${{ shipping.toFixed(2) }}</span>
              </div>
              <div class="summary-total">
                <span>总计 (Total)</span>
                <span class="total-amount">${{ grandTotal.toFixed(2) }}</span>
              </div>
            </div>
          </div>

          <div class="invoice-divider"></div>

          <!-- 底部：付款方式 + 备注 + 签名 -->
          <el-row :gutter="30" class="invoice-footer">
            <el-col :span="8">
              <div class="footer-block">
                <div class="block-label">付款方式</div>
                <div class="footer-value">银行转账</div>
                <div class="footer-detail">账户名：ApeAdmin Store</div>
                <div class="footer-detail">账号：6228 4800 1234 5678 901</div>
                <div class="footer-detail">开户行：中国银行天河支行</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="footer-block">
                <div class="block-label">备注</div>
                <div class="footer-detail">请在到期日前完成付款。如逾期未付，将产生 2% 的滞纳金。如有疑问请联系客服：400-888-0000。</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="footer-block signature-block">
                <div class="block-label">授权签名</div>
                <div class="signature-area"></div>
                <div class="footer-detail">授权人：李经理</div>
                <div class="footer-detail">日期：2026-08-21</div>
              </div>
            </el-col>
          </el-row>

          <div class="invoice-thanks">
            <el-icon color="#534686"><Star /></el-icon>
            感谢您的惠顾，期待再次合作！
          </div>
        </div>
      </el-col>

      <!-- 右侧：操作按钮 -->
      <el-col :span="6">
        <el-card shadow="never" class="action-card">
          <template #header>
            <span class="card-title">发票操作</span>
          </template>
          <div class="action-list">
            <el-button type="primary" size="large" :icon="Download" @click="downloadInvoice" class="action-btn">下载 PDF</el-button>
            <el-button size="large" :icon="Printer" @click="printInvoice" class="action-btn">打印发票</el-button>
            <el-button size="large" :icon="Message" @click="sendEmail" class="action-btn">发送邮件</el-button>
            <el-button size="large" :icon="Share" @click="shareLink" class="action-btn">分享链接</el-button>
          </div>
          <el-divider />
          <div class="invoice-status">
            <div class="status-label">发票状态</div>
            <el-tag type="warning" effect="light" size="large">待付款</el-tag>
            <div class="status-note">等待客户付款确认</div>
          </div>
          <el-divider />
          <div class="invoice-info-mini">
            <div class="mini-row"><span>发票金额</span><span class="mini-val">${{ grandTotal.toFixed(2) }}</span></div>
            <div class="mini-row"><span>商品数量</span><span class="mini-val">{{ totalQty }} 件</span></div>
            <div class="mini-row"><span>创建时间</span><span class="mini-val">2026-08-21</span></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import { Download, Printer, Message, Share, Shop, Star } from '@element-plus/icons-vue'
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

const items = [
  { name: 'iPhone 15 Pro Max 256GB', sku: 'IP15PM-256', qty: 1, price: 1199.00 },
  { name: 'AirPods Pro 2 (USB-C)', sku: 'APP-PRO2-USBC', qty: 2, price: 249.00 },
  { name: 'Apple Watch Ultra 2', sku: 'AW-ULT2', qty: 1, price: 799.00 },
  { name: 'Magic Keyboard for iPad', sku: 'MK-IPAD-11', qty: 1, price: 279.00 },
  { name: 'AppleCare+ Protection Plan', sku: 'ACP-PRO', qty: 2, price: 199.00 },
]

const subtotal = computed(() => items.reduce((sum, i) => sum + i.price * i.qty, 0))
const tax = computed(() => subtotal.value * 0.08)
const shipping = 25.00
const grandTotal = computed(() => subtotal.value + tax.value + shipping)
const totalQty = computed(() => items.reduce((sum, i) => sum + i.qty, 0))

function downloadInvoice() {
  ElMessage.success('发票 PDF 正在生成，请稍候...')
}

function printInvoice() {
  ElMessage.success('正在打开打印对话框...')
}

function sendEmail() {
  ElMessage.success('发票已发送至客户邮箱：zhangwei@example.com')
}

function shareLink() {
  ElMessage.success('分享链接已复制到剪贴板')
}
</script>

<style scoped>
.invoice-paper {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 40px 48px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  aspect-ratio: 210 / 297;
  max-width: 800px;
  margin: 0 auto;
}

/* 顶部 */
.invoice-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.company-info {
  display: flex;
  gap: 14px;
  align-items: center;
}

.company-logo {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: #f0ecf6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.company-name {
  font-size: 20px;
  font-weight: 700;
  color: #534686;
  margin: 0 0 4px;
}

.company-meta {
  font-size: 12px;
  color: #909399;
  margin: 2px 0;
}

.invoice-meta {
  text-align: right;
}

.invoice-title {
  font-size: 36px;
  font-weight: 800;
  color: #534686;
  letter-spacing: 4px;
  margin: 0 0 12px;
}

.meta-row {
  font-size: 13px;
  margin: 3px 0;
}

.meta-label {
  color: #909399;
}

.meta-value {
  font-weight: 600;
  color: #303133;
}

.invoice-divider {
  height: 2px;
  background: linear-gradient(90deg, #534686, #f0ecf6);
  margin: 24px 0;
  border-radius: 1px;
}

/* 客户信息 */
.customer-section {
  display: flex;
  gap: 40px;
  margin-bottom: 24px;
}

.customer-block {
  flex: 1;
}

.block-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: #534686;
  letter-spacing: 1px;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid #f0ecf6;
}

.customer-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.customer-detail {
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
}

/* 商品表格 */
.invoice-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.invoice-table thead th {
  background: #534686;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  padding: 10px 14px;
  text-align: left;
}

.invoice-table thead .col-qty,
.invoice-table thead .col-price,
.invoice-table thead .col-amount {
  text-align: center;
}

.invoice-table tbody td {
  padding: 12px 14px;
  border-bottom: 1px solid #f0ecf6;
  font-size: 13px;
  color: #606266;
}

.invoice-table tbody .col-qty,
.invoice-table tbody .col-price,
.invoice-table tbody .col-amount {
  text-align: center;
}

.invoice-table tbody tr:nth-child(even) {
  background: #fafbfc;
}

.item-name {
  font-weight: 600;
  color: #303133;
}

.item-sku {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 2px;
}

.col-amount {
  font-weight: 600;
  color: #534686;
}

/* 费用汇总 */
.invoice-summary {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 24px;
}

.summary-content {
  width: 280px;
}

.summary-line {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #606266;
  padding: 6px 0;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 2px solid #534686;
  padding-top: 12px;
  margin-top: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.total-amount {
  font-size: 22px;
  color: #534686;
}

/* 底部 */
.invoice-footer {
  margin-bottom: 20px;
}

.footer-block {
  font-size: 13px;
}

.footer-value {
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.footer-detail {
  font-size: 12px;
  color: #909399;
  line-height: 1.7;
}

.signature-block .signature-area {
  height: 48px;
  border-bottom: 1px dashed #c0c4cc;
  margin-bottom: 8px;
}

.invoice-thanks {
  text-align: center;
  font-size: 13px;
  color: #534686;
  padding-top: 16px;
  border-top: 1px solid #f0ecf6;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* 右侧操作卡片 */
.action-card {
  position: sticky;
  top: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #534686;
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  width: 100%;
}

.invoice-status {
  text-align: center;
}

.status-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.status-note {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 8px;
}

.invoice-info-mini {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mini-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #606266;
}

.mini-val {
  font-weight: 600;
  color: #303133;
}
</style>
