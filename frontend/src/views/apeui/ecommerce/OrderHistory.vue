<template>
  <div class="order-history-page">
    <PageHeader title="Order History" :breadcrumb="['APEUI库', 'Ecommerce', 'Order History']">
      <template #actions>
        <el-button type="primary" :icon="Download">导出订单</el-button>
      </template>
    </PageHeader>

    <!-- 状态筛选标签 -->
    <el-card shadow="never" class="filter-card">
      <div class="status-tabs">
        <div
          v-for="tab in statusTabs"
          :key="tab.value"
          :class="['status-tab', { active: activeTab === tab.value }]"
          @click="activeTab = tab.value"
        >
          {{ tab.label }}
          <span class="tab-count">{{ tab.count }}</span>
        </div>
      </div>
    </el-card>

    <!-- 订单列表表格 -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">订单列表</span>
          <div class="header-tools">
            <el-input v-model="searchKey" placeholder="搜索订单号/客户" clearable style="width: 220px" :prefix-icon="Search" />
            <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 260px" />
          </div>
        </div>
      </template>
      <el-table :data="filteredOrders" stripe style="width: 100%">
        <el-table-column prop="orderNo" label="订单号" min-width="150" />
        <el-table-column prop="product" label="商品" min-width="160" show-overflow-tooltip />
        <el-table-column prop="customer" label="客户" min-width="120" />
        <el-table-column prop="total" label="总额" min-width="110" align="right">
          <template #default="{ row }">
            <span class="amount-text">${{ row.total.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="light">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="日期" min-width="120" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[5, 10, 20, 50]"
          :total="filteredOrders.length"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>

    <!-- 订单详情弹窗 -->
    <el-dialog v-model="detailVisible" title="订单详情" width="680px" class="order-detail-dialog">
      <div v-if="currentOrder" class="order-detail">
        <!-- 订单概览 -->
        <div class="detail-header">
          <div>
            <span class="detail-order-no">订单号：{{ currentOrder.orderNo }}</span>
            <el-tag :type="statusTagType(currentOrder.status)" effect="light" style="margin-left: 10px">{{ currentOrder.status }}</el-tag>
          </div>
          <span class="detail-date">下单日期：{{ currentOrder.date }}</span>
        </div>

        <el-divider />

        <!-- 商品列表 -->
        <h4 class="section-title">商品列表</h4>
        <el-table :data="currentOrder.items" border style="width: 100%" size="small">
          <el-table-column prop="name" label="商品名称" min-width="160" />
          <el-table-column prop="qty" label="数量" width="80" align="center" />
          <el-table-column prop="price" label="单价" width="100" align="right">
            <template #default="{ row }">${{ row.price.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="小计" width="120" align="right">
            <template #default="{ row }">${{ (row.price * row.qty).toFixed(2) }}</template>
          </el-table-column>
        </el-table>

        <el-divider />

        <!-- 收货地址 + 支付信息 -->
        <el-row :gutter="30">
          <el-col :span="12">
            <h4 class="section-title">收货地址</h4>
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="收货人">{{ currentOrder.address.name }}</el-descriptions-item>
              <el-descriptions-item label="电话">{{ currentOrder.address.phone }}</el-descriptions-item>
              <el-descriptions-item label="地址">{{ currentOrder.address.detail }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="12">
            <h4 class="section-title">支付信息</h4>
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="支付方式">{{ currentOrder.payment.method }}</el-descriptions-item>
              <el-descriptions-item label="交易号">{{ currentOrder.payment.txnNo }}</el-descriptions-item>
              <el-descriptions-item label="支付状态">
                <el-tag :type="statusTagType(currentOrder.status)" effect="light" size="small">{{ currentOrder.status }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>

        <el-divider />

        <!-- 物流跟踪 -->
        <h4 class="section-title">物流跟踪</h4>
        <div class="logistics-tracking">
          <el-steps direction="vertical" :active="currentOrder.tracking.activeStep" process-status="success" finish-status="success">
            <el-step v-for="(step, i) in currentOrder.tracking.steps" :key="i" :title="step.title" :description="step.desc" />
          </el-steps>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="detailVisible = false">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import { Search, Download } from '@element-plus/icons-vue'
import { ref, computed } from 'vue'

const searchKey = ref('')
const dateRange = ref([])
const activeTab = ref('All')
const currentPage = ref(1)
const pageSize = ref(5)
const detailVisible = ref(false)
const currentOrder = ref(null as any)

const statusTabs = computed(() => [
  { label: 'All', value: 'All', count: orders.value.length },
  { label: 'Pending', value: 'Pending', count: orders.value.filter(o => o.status === 'Pending').length },
  { label: 'Processing', value: 'Processing', count: orders.value.filter(o => o.status === 'Processing').length },
  { label: 'Shipped', value: 'Shipped', count: orders.value.filter(o => o.status === 'Shipped').length },
  { label: 'Delivered', value: 'Delivered', count: orders.value.filter(o => o.status === 'Delivered').length },
  { label: 'Cancelled', value: 'Cancelled', count: orders.value.filter(o => o.status === 'Cancelled').length },
])

const orders = ref([
  {
    orderNo: 'ORD-2026-0801',
    product: 'iPhone 15 Pro Max 256GB',
    customer: '张伟',
    total: 1299.00,
    status: 'Delivered',
    date: '2026-08-01',
    items: [{ name: 'iPhone 15 Pro Max 256GB', qty: 1, price: 1199.00 }, { name: '原装硅胶保护壳', qty: 1, price: 100.00 }],
    address: { name: '张伟', phone: '138-0000-0001', detail: '广东省广州市天河区珠江新城华夏路30号' },
    payment: { method: 'Visa', txnNo: 'TXN20260801001' },
    tracking: {
      activeStep: 3,
      steps: [
        { title: '订单已创建', desc: '2026-08-01 10:30' },
        { title: '已付款', desc: '2026-08-01 10:35' },
        { title: '商家已发货', desc: '2026-08-02 14:00' },
        { title: '已签收', desc: '2026-08-04 09:20' },
      ],
    },
  },
  {
    orderNo: 'ORD-2026-0802',
    product: 'MacBook Air M3 13英寸',
    customer: '李娜',
    total: 1099.00,
    status: 'Shipped',
    date: '2026-08-03',
    items: [{ name: 'MacBook Air M3 13英寸', qty: 1, price: 999.00 }, { name: 'USB-C 充电器', qty: 1, price: 100.00 }],
    address: { name: '李娜', phone: '138-0000-0002', detail: '北京市海淀区中关村大街1号' },
    payment: { method: 'PayPal', txnNo: 'TXN20260803002' },
    tracking: {
      activeStep: 2,
      steps: [
        { title: '订单已创建', desc: '2026-08-03 09:15' },
        { title: '已付款', desc: '2026-08-03 09:20' },
        { title: '商家已发货', desc: '2026-08-04 16:00' },
        { title: '运输中', desc: '预计 2026-08-06 送达' },
      ],
    },
  },
  {
    orderNo: 'ORD-2026-0803',
    product: 'iPad Pro 11英寸 M4',
    customer: '王芳',
    total: 899.00,
    status: 'Processing',
    date: '2026-08-05',
    items: [{ name: 'iPad Pro 11英寸 M4', qty: 1, price: 899.00 }],
    address: { name: '王芳', phone: '138-0000-0003', detail: '上海市浦东新区世纪大道100号' },
    payment: { method: '支付宝', txnNo: 'TXN20260805003' },
    tracking: {
      activeStep: 1,
      steps: [
        { title: '订单已创建', desc: '2026-08-05 11:00' },
        { title: '已付款', desc: '2026-08-05 11:05' },
        { title: '备货中', desc: '预计 2026-08-06 发货' },
      ],
    },
  },
  {
    orderNo: 'ORD-2026-0804',
    product: 'AirPods Pro 2 + Apple Care',
    customer: '刘强',
    total: 349.00,
    status: 'Pending',
    date: '2026-08-07',
    items: [{ name: 'AirPods Pro 2', qty: 1, price: 249.00 }, { name: 'Apple Care+', qty: 1, price: 100.00 }],
    address: { name: '刘强', phone: '138-0000-0004', detail: '深圳市南山区科技园南区' },
    payment: { method: '微信支付', txnNo: 'TXN20260807004' },
    tracking: {
      activeStep: 0,
      steps: [{ title: '订单已创建', desc: '2026-08-07 15:30' }, { title: '等待付款', desc: '请在24小时内完成付款' }],
    },
  },
  {
    orderNo: 'ORD-2026-0805',
    product: 'Apple Watch Ultra 2',
    customer: '陈静',
    total: 799.00,
    status: 'Delivered',
    date: '2026-08-09',
    items: [{ name: 'Apple Watch Ultra 2', qty: 1, price: 799.00 }],
    address: { name: '陈静', phone: '138-0000-0005', detail: '杭州市西湖区文三路478号' },
    payment: { method: 'Visa', txnNo: 'TXN20260809005' },
    tracking: {
      activeStep: 3,
      steps: [
        { title: '订单已创建', desc: '2026-08-09 08:00' },
        { title: '已付款', desc: '2026-08-09 08:10' },
        { title: '商家已发货', desc: '2026-08-10 10:00' },
        { title: '已签收', desc: '2026-08-12 14:30' },
      ],
    },
  },
  {
    orderNo: 'ORD-2026-0806',
    product: 'Magic Keyboard + Magic Mouse',
    customer: '赵磊',
    total: 258.00,
    status: 'Cancelled',
    date: '2026-08-11',
    items: [{ name: 'Magic Keyboard', qty: 1, price: 179.00 }, { name: 'Magic Mouse', qty: 1, price: 79.00 }],
    address: { name: '赵磊', phone: '138-0000-0006', detail: '成都市武侯区天府大道北段1号' },
    payment: { method: 'PayPal', txnNo: 'TXN20260811006' },
    tracking: {
      activeStep: 0,
      steps: [{ title: '订单已取消', desc: '2026-08-11 16:00 用户主动取消' }],
    },
  },
  {
    orderNo: 'ORD-2026-0807',
    product: 'iMac 24英寸 M3',
    customer: '孙丽',
    total: 1499.00,
    status: 'Processing',
    date: '2026-08-13',
    items: [{ name: 'iMac 24英寸 M3', qty: 1, price: 1499.00 }],
    address: { name: '孙丽', phone: '138-0000-0007', detail: '武汉市洪山区珞瑜路1037号' },
    payment: { method: 'Mastercard', txnNo: 'TXN20260813007' },
    tracking: {
      activeStep: 1,
      steps: [
        { title: '订单已创建', desc: '2026-08-13 10:00' },
        { title: '已付款', desc: '2026-08-13 10:15' },
        { title: '备货中', desc: '预计 2026-08-15 发货' },
      ],
    },
  },
  {
    orderNo: 'ORD-2026-0808',
    product: 'Mac Studio M2 Ultra',
    customer: '周涛',
    total: 3999.00,
    status: 'Shipped',
    date: '2026-08-15',
    items: [{ name: 'Mac Studio M2 Ultra', qty: 1, price: 3999.00 }],
    address: { name: '周涛', phone: '138-0000-0008', detail: '南京市鼓楼区北京西路2号' },
    payment: { method: 'Visa', txnNo: 'TXN20260815008' },
    tracking: {
      activeStep: 2,
      steps: [
        { title: '订单已创建', desc: '2026-08-15 09:00' },
        { title: '已付款', desc: '2026-08-15 09:10' },
        { title: '商家已发货', desc: '2026-08-16 11:00' },
        { title: '运输中', desc: '预计 2026-08-18 送达' },
      ],
    },
  },
])

const filteredOrders = computed(() => {
  let result = orders.value
  if (activeTab.value !== 'All') {
    result = result.filter(o => o.status === activeTab.value)
  }
  if (searchKey.value) {
    result = result.filter(o => o.orderNo.toLowerCase().includes(searchKey.value.toLowerCase()) || o.customer.includes(searchKey.value))
  }
  return result
})

function statusTagType(status: string) {
  const map: Record<string, string> = {
    Pending: 'warning',
    Processing: 'info',
    Shipped: '',
    Delivered: 'success',
    Cancelled: 'danger',
  }
  return map[status] || ''
}

function showDetail(row: any) {
  currentOrder.value = row
  detailVisible.value = true
}
</script>

<style scoped>
.filter-card {
  margin-bottom: 20px;
}

.filter-card :deep(.el-card__body) {
  padding: 12px 20px;
}

.status-tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.status-tab {
  padding: 8px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  background: #f5f7fa;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-tab:hover {
  background: #ede8f5;
}

.status-tab.active {
  background: #534686;
  color: #fff;
}

.status-tab.active .tab-count {
  background: rgba(255, 255, 255, 0.25);
}

.tab-count {
  background: #e4e7ed;
  border-radius: 10px;
  padding: 1px 8px;
  font-size: 12px;
  font-weight: 600;
}

.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #534686;
}

.header-tools {
  display: flex;
  gap: 10px;
  align-items: center;
}

.amount-text {
  font-weight: 600;
  color: #534686;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.order-detail-dialog .order-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-order-no {
  font-size: 16px;
  font-weight: 700;
  color: #534686;
}

.detail-date {
  font-size: 13px;
  color: #909399;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #534686;
  margin: 0 0 12px;
}

.logistics-tracking {
  padding: 8px 0 0 8px;
}
</style>
