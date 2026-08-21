<template>
  <div class="checkout-page">
    <PageHeader title="Checkout" :breadcrumb="['APEUI库', 'Ecommerce', 'Checkout']" />

    <el-row :gutter="30">
      <!-- 左侧：步骤导航 -->
      <el-col :span="5">
        <el-card shadow="never" class="steps-nav-card">
          <el-steps direction="vertical" :active="activeStep" finish-status="success" align-center>
            <el-step title="收货地址" description="选择或新增地址" @click="goToStep(0)" class="clickable-step" />
            <el-step title="支付方式" description="选择付款方式" @click="goToStep(1)" class="clickable-step" />
            <el-step title="确认订单" description="核对并下单" @click="goToStep(2)" class="clickable-step" />
          </el-steps>
        </el-card>
      </el-col>

      <!-- 右侧：当前步骤内容 -->
      <el-col :span="19">
        <!-- Step 1: 收货地址 -->
        <el-card v-show="activeStep === 0" shadow="never" class="step-card">
          <template #header>
            <span class="card-title">收货地址</span>
          </template>
          <el-row :gutter="30">
            <el-col :span="8" v-for="addr in addresses" :key="addr.id">
              <div :class="['address-card', { selected: selectedAddressId === addr.id }]" @click="selectAddress(addr.id)">
                <el-radio :model-value="selectedAddressId" :label="addr.id" class="address-radio">
                  <span class="addr-name">{{ addr.name }} <el-tag size="small" effect="plain" v-if="addr.isDefault" type="success">默认</el-tag></span>
                </el-radio>
                <div class="addr-detail">
                  <p class="addr-line">{{ addr.phone }}</p>
                  <p class="addr-line">{{ addr.detail }}</p>
                  <p class="addr-label">{{ addr.label }}</p>
                </div>
                <div class="addr-actions">
                  <el-button link type="primary" size="small" @click.stop="editAddress(addr)">编辑</el-button>
                  <el-button link type="danger" size="small" @click.stop="deleteAddress(addr)" v-if="!addr.isDefault">删除</el-button>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="address-card add-address" @click="showAddAddress = true">
                <el-icon :size="32" color="#c0c4cc"><Plus /></el-icon>
                <span class="add-text">新增收货地址</span>
              </div>
            </el-col>
          </el-row>
          <div class="step-footer">
            <el-button type="primary" size="large" :disabled="!selectedAddressId" @click="nextStep">下一步：支付方式</el-button>
          </div>
        </el-card>

        <!-- Step 2: 支付方式 -->
        <el-card v-show="activeStep === 1" shadow="never" class="step-card">
          <template #header>
            <span class="card-title">支付方式</span>
          </template>
          <div class="payment-methods">
            <!-- 信用卡 -->
            <div :class="['payment-option', { active: paymentMethod === 'credit' }]" @click="paymentMethod = 'credit'">
              <el-radio :model-value="paymentMethod" label="credit">
                <el-icon><CreditCard /></el-icon> 信用卡
              </el-radio>
            </div>
            <el-card v-if="paymentMethod === 'credit'" shadow="never" class="credit-form">
              <el-form :model="creditForm" label-width="90px" class="checkout-form">
                <el-form-item label="卡号">
                  <el-input v-model="creditForm.cardNo" placeholder="1234 5678 9012 3456" maxlength="19" />
                </el-form-item>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="有效期">
                      <el-input v-model="creditForm.expiry" placeholder="MM / YY" maxlength="7" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="CVV">
                      <el-input v-model="creditForm.cvv" placeholder="3-4位安全码" maxlength="4" type="password" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="持卡人">
                  <el-input v-model="creditForm.holder" placeholder="持卡人姓名" />
                </el-form-item>
              </el-form>
            </el-card>

            <!-- PayPal -->
            <div :class="['payment-option', { active: paymentMethod === 'paypal' }]" @click="paymentMethod = 'paypal'">
              <el-radio :model-value="paymentMethod" label="paypal">
                <el-icon><Wallet /></el-icon> PayPal
              </el-radio>
            </div>
            <el-card v-if="paymentMethod === 'paypal'" shadow="never" class="method-info">
              <el-icon color="#3EBCB9" :size="20"><Wallet /></el-icon>
              <span>将跳转至 PayPal 完成支付，安全便捷。</span>
            </el-card>

            <!-- 支付宝 -->
            <div :class="['payment-option', { active: paymentMethod === 'alipay' }]" @click="paymentMethod = 'alipay'">
              <el-radio :model-value="paymentMethod" label="alipay">
                <el-icon color="#1677FF"><Box /></el-icon> 支付宝
              </el-radio>
            </div>
            <el-card v-if="paymentMethod === 'alipay'" shadow="never" class="method-info">
              <el-icon color="#1677FF" :size="20"><Box /></el-icon>
              <span>使用支付宝扫码支付，支持花呗分期。</span>
            </el-card>

            <!-- 微信支付 -->
            <div :class="['payment-option', { active: paymentMethod === 'wechat' }]" @click="paymentMethod = 'wechat'">
              <el-radio :model-value="paymentMethod" label="wechat">
                <el-icon color="#67C100"><ChatDotRound /></el-icon> 微信支付
              </el-radio>
            </div>
            <el-card v-if="paymentMethod === 'wechat'" shadow="never" class="method-info">
              <el-icon color="#67C100" :size="20"><ChatDotRound /></el-icon>
              <span>使用微信扫码支付，实时到账。</span>
            </el-card>
          </div>
          <div class="step-footer">
            <el-button size="large" @click="prevStep">上一步</el-button>
            <el-button type="primary" size="large" @click="nextStep">下一步：确认订单</el-button>
          </div>
        </el-card>

        <!-- Step 3: 确认订单 -->
        <el-card v-show="activeStep === 2" shadow="never" class="step-card">
          <template #header>
            <span class="card-title">确认订单</span>
          </template>

          <!-- 商品列表汇总 -->
          <h4 class="section-title">商品列表</h4>
          <el-table :data="cartItems" border size="small" style="margin-bottom: 20px">
            <el-table-column prop="name" label="商品名称" min-width="200" />
            <el-table-column prop="qty" label="数量" width="80" align="center" />
            <el-table-column label="单价" width="100" align="right">
              <template #default="{ row }">${{ row.price.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="小计" width="120" align="right">
              <template #default="{ row }">
                <span class="subtotal-text">${{ (row.price * row.qty).toFixed(2) }}</span>
              </template>
            </el-table-column>
          </el-table>

          <!-- 收货地址确认 -->
          <h4 class="section-title">收货地址</h4>
          <div class="confirm-address" v-if="selectedAddress">
            <el-icon color="#5A67F5"><Location /></el-icon>
            <div>
              <span class="confirm-addr-name">{{ selectedAddress.name }} · {{ selectedAddress.phone }}</span>
              <p class="confirm-addr-detail">{{ selectedAddress.detail }}</p>
            </div>
          </div>

          <!-- 支付方式确认 -->
          <h4 class="section-title">支付方式</h4>
          <div class="confirm-payment">
            <el-tag effect="plain">{{ paymentMethodLabel }}</el-tag>
          </div>

          <!-- 费用明细 -->
          <h4 class="section-title">费用明细</h4>
          <div class="cost-summary">
            <div class="cost-row">
              <span>商品总价</span>
              <span>${{ itemsTotal.toFixed(2) }}</span>
            </div>
            <div class="cost-row">
              <span>运费</span>
              <span>${{ shipping.toFixed(2) }}</span>
            </div>
            <div class="cost-row">
              <span>税费 (8%)</span>
              <span>${{ tax.toFixed(2) }}</span>
            </div>
            <div class="cost-total">
              <span>应付总计</span>
              <span class="total-amount">${{ grandTotal.toFixed(2) }}</span>
            </div>
          </div>

          <div class="step-footer">
            <el-button size="large" @click="prevStep">上一步</el-button>
            <el-button type="primary" size="large" :icon="Check" @click="placeOrder">提交订单</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增地址弹窗 -->
    <el-dialog v-model="showAddAddress" title="新增收货地址" width="520px">
      <el-form :model="newAddress" label-width="80px">
        <el-form-item label="收货人">
          <el-input v-model="newAddress.name" placeholder="收货人姓名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="newAddress.phone" placeholder="手机号码" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="newAddress.detail" type="textarea" :rows="2" placeholder="详细地址" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="newAddress.label" placeholder="如：家、公司、学校" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddAddress = false">取消</el-button>
        <el-button type="primary" @click="confirmAddAddress">保存</el-button>
      </template>
    </el-dialog>

    <!-- 下单成功弹窗 -->
    <el-dialog v-model="orderSuccessVisible" title="下单成功" width="460px" :close-on-click-modal="false">
      <div class="success-dialog">
        <el-icon :size="56" color="#67C100"><CircleCheck /></el-icon>
        <h3 class="success-title">订单提交成功！</h3>
        <p class="success-desc">订单号：{{ orderNo }}</p>
        <p class="success-desc">支付金额：${{ grandTotal.toFixed(2) }}</p>
        <p class="success-hint">我们将在 1-3 个工作日内为您发货</p>
      </div>
      <template #footer>
        <el-button @click="orderSuccessVisible = false">关闭</el-button>
        <el-button type="primary" @click="orderSuccessVisible = false">查看订单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import { Plus, CreditCard, Wallet, Box, ChatDotRound, Location, Check, CircleCheck } from '@element-plus/icons-vue'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const activeStep = ref(0)

/* ===== Step 1: 收货地址 ===== */
const addresses = ref([
  { id: 1, name: '张伟', phone: '138-0000-0001', detail: '广东省广州市天河区珠江新城华夏路30号', label: '家', isDefault: true },
  { id: 2, name: '张伟', phone: '138-0000-0001', detail: '北京市海淀区中关村大街1号科技大厦18层', label: '公司', isDefault: false },
  { id: 3, name: '张伟', phone: '138-0000-0001', detail: '上海市浦东新区世纪大道100号环球金融中心', label: '上海办事处', isDefault: false },
])
const selectedAddressId = ref(1)
const showAddAddress = ref(false)
const newAddress = ref({ name: '', phone: '', detail: '', label: '' })

const selectedAddress = computed(() => addresses.value.find(a => a.id === selectedAddressId.value))

function selectAddress(id: number) {
  selectedAddressId.value = id
}

function editAddress(addr: any) {
  ElMessage.info(`编辑地址：${addr.label}`)
}

function deleteAddress(addr: any) {
  addresses.value = addresses.value.filter(a => a.id !== addr.id)
  ElMessage.success('地址已删除')
}

function confirmAddAddress() {
  if (!newAddress.value.name || !newAddress.value.phone || !newAddress.value.detail) {
    ElMessage.warning('请填写完整的地址信息')
    return
  }
  addresses.value.push({ id: Date.now(), ...newAddress.value, isDefault: false })
  newAddress.value = { name: '', phone: '', detail: '', label: '' }
  showAddAddress.value = false
  ElMessage.success('地址添加成功')
}

/* ===== Step 2: 支付方式 ===== */
const paymentMethod = ref('credit')
const creditForm = ref({ cardNo: '', expiry: '', cvv: '', holder: '' })

const paymentMethodLabel = computed(() => {
  const map: Record<string, string> = { credit: '信用卡', paypal: 'PayPal', alipay: '支付宝', wechat: '微信支付' }
  return map[paymentMethod.value] || ''
})

/* ===== Step 3: 确认订单 ===== */
const cartItems = ref([
  { name: 'iPhone 15 Pro Max 256GB', qty: 1, price: 1199.00 },
  { name: 'AirPods Pro 2 (USB-C)', qty: 1, price: 249.00 },
  { name: 'Apple Watch Ultra 2', qty: 1, price: 799.00 },
  { name: 'Magic Keyboard for iPad', qty: 2, price: 279.00 },
])

const itemsTotal = computed(() => cartItems.value.reduce((sum, i) => sum + i.price * i.qty, 0))
const shipping = ref(25.00)
const tax = computed(() => itemsTotal.value * 0.08)
const grandTotal = computed(() => itemsTotal.value + shipping.value + tax.value)

const orderSuccessVisible = ref(false)
const orderNo = ref('')

/* ===== 步骤导航 ===== */
function goToStep(step: number) {
  if (step <= activeStep.value) {
    activeStep.value = step
  }
}

function nextStep() {
  if (activeStep.value === 0 && !selectedAddressId.value) {
    ElMessage.warning('请选择收货地址')
    return
  }
  if (activeStep.value === 1 && paymentMethod.value === 'credit') {
    if (!creditForm.value.cardNo || !creditForm.value.expiry || !creditForm.value.cvv) {
      ElMessage.warning('请填写完整的信用卡信息')
      return
    }
  }
  activeStep.value = Math.min(activeStep.value + 1, 2)
}

function prevStep() {
  activeStep.value = Math.max(activeStep.value - 1, 0)
}

function placeOrder() {
  orderNo.value = `ORD-2026-${Date.now().toString().slice(-6)}`
  orderSuccessVisible.value = true
}
</script>

<style scoped>
.steps-nav-card {
  position: sticky;
  top: 20px;
}

.clickable-step {
  cursor: pointer;
}

.clickable-step :deep(.el-step__head),
.clickable-step :deep(.el-step__title) {
  cursor: pointer;
}

.step-card {
  min-height: 400px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #5A67F5;
}

/* 地址卡片 */
.address-card {
  border: 2px solid #e4e7ed;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  height: 100%;
}

.address-card:hover {
  border-color: #c0b4d9;
}

.address-card.selected {
  border-color: #5A67F5;
  background: #faf9fc;
  box-shadow: 0 0 0 3px rgba(90, 103, 245, 0.08);
}

.address-radio {
  margin-bottom: 10px;
}

.addr-name {
  font-weight: 600;
  color: #303133;
  font-size: 15px;
}

.addr-detail {
  padding-left: 24px;
}

.addr-line {
  font-size: 13px;
  color: #606266;
  margin: 4px 0;
  line-height: 1.5;
}

.addr-label {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

.addr-actions {
  padding-left: 24px;
  margin-top: 8px;
}

.add-address {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-style: dashed;
  min-height: 160px;
  gap: 8px;
}

.add-text {
  font-size: 14px;
  color: #909399;
}

/* 支付方式 */
.payment-methods {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-option {
  border: 2px solid #e4e7ed;
  border-radius: 10px;
  padding: 14px 18px;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-option:hover {
  border-color: #c0b4d9;
}

.payment-option.active {
  border-color: #5A67F5;
  background: #faf9fc;
}

.credit-form {
  border: 1px solid #EDF2FF !important;
  margin-top: -4px;
}

.checkout-form {
  margin-top: 8px;
}

.method-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
  border: 1px solid #EDF2FF !important;
  margin-top: -4px;
}

/* 步骤底部按钮 */
.step-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #EDF2FF;
}

/* 确认订单 */
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #5A67F5;
  margin: 0 0 12px;
}

.subtotal-text {
  font-weight: 600;
  color: #5A67F5;
}

.confirm-address {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  background: #faf9fc;
  padding: 14px 16px;
  border-radius: 8px;
  border: 1px solid #EDF2FF;
  margin-bottom: 20px;
}

.confirm-addr-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
  display: block;
}

.confirm-addr-detail {
  font-size: 13px;
  color: #909399;
  margin: 4px 0 0;
}

.confirm-payment {
  margin-bottom: 20px;
}

.cost-summary {
  background: #faf9fc;
  border: 1px solid #EDF2FF;
  border-radius: 8px;
  padding: 16px 20px;
  max-width: 320px;
  margin-left: auto;
}

.cost-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #606266;
  padding: 6px 0;
}

.cost-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 2px solid #5A67F5;
  padding-top: 12px;
  margin-top: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.total-amount {
  font-size: 22px;
  color: #5A67F5;
}

/* 成功弹窗 */
.success-dialog {
  text-align: center;
  padding: 20px 0;
}

.success-title {
  font-size: 20px;
  font-weight: 700;
  color: #5A67F5;
  margin: 16px 0 8px;
}

.success-desc {
  font-size: 14px;
  color: #606266;
  margin: 4px 0;
}

.success-hint {
  font-size: 13px;
  color: #c0c4cc;
  margin-top: 12px;
}
</style>
