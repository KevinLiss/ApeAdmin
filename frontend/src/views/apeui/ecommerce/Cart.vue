<template>
  <div class="cart-page">
    <PageHeader title="Cart" :breadcrumb="['APEUI库', 'Ecommerce', 'Cart']" />

    <template v-if="cartItems.length > 0">
      <el-row :gutter="30">
        <!-- Left: Cart Items -->
        <el-col :xs="24" :lg="16">
          <el-card class="koho-card cart-items-card" shadow="never">
            <h3 class="card-title">
              Shopping Cart
              <span class="item-count">{{ cartItems.length }} items</span>
            </h3>

            <div class="cart-item" v-for="(item, index) in cartItems" :key="item.id">
              <div class="cart-item-img" :style="{ background: item.bgColor }">
                <el-icon :size="28" color="rgba(255,255,255,0.8)"><Goods /></el-icon>
              </div>
              <div class="cart-item-info">
                <h4 class="cart-item-name">{{ item.name }}</h4>
                <span class="cart-item-category">{{ item.category }}</span>
              </div>
              <div class="cart-item-price">
                <span class="price-label">Price</span>
                <span class="price-value">${{ item.price.toFixed(2) }}</span>
              </div>
              <div class="cart-item-qty">
                <span class="price-label">Qty</span>
                <el-input-number v-model="item.qty" :min="1" :max="20" size="small" @change="recalc" />
              </div>
              <div class="cart-item-subtotal">
                <span class="price-label">Subtotal</span>
                <span class="subtotal-value">${{ (item.price * item.qty).toFixed(2) }}</span>
              </div>
              <el-button link type="danger" :icon="Delete" circle @click="removeItem(index)" />
            </div>

            <div class="cart-footer">
              <el-button :icon="ArrowLeft" @click="continueShopping">Continue Shopping</el-button>
              <el-button type="danger" plain @click="clearCart">Clear Cart</el-button>
            </div>
          </el-card>
        </el-col>

        <!-- Right: Summary -->
        <el-col :xs="24" :lg="8">
          <el-card class="koho-card summary-card" shadow="never">
            <h3 class="card-title">Order Summary</h3>

            <!-- Coupon -->
            <div class="coupon-section">
              <span class="summary-label">Coupon Code</span>
              <div class="coupon-input-row">
                <el-input v-model="couponCode" placeholder="Enter code" />
                <el-button type="primary" @click="applyCoupon">Apply</el-button>
              </div>
              <div class="coupon-applied" v-if="couponApplied">
                <el-tag type="success" effect="dark" round>Coupon applied: {{ couponCode.toUpperCase() }} (-10%)</el-tag>
              </div>
            </div>

            <el-divider />

            <!-- Summary -->
            <div class="summary-row">
              <span>Items ({{ totalItems }})</span>
              <span>${{ subtotal.toFixed(2) }}</span>
            </div>
            <div class="summary-row" v-if="discount > 0">
              <span>Discount</span>
              <span class="discount-text">-${{ discount.toFixed(2) }}</span>
            </div>
            <div class="summary-row">
              <span>Shipping</span>
              <span>{{ shipping === 0 ? 'Free' : '$' + shipping.toFixed(2) }}</span>
            </div>
            <div class="summary-row">
              <span>Tax (8%)</span>
              <span>${{ tax.toFixed(2) }}</span>
            </div>

            <el-divider />

            <div class="summary-total">
              <span>Total</span>
              <span class="total-value">${{ total.toFixed(2) }}</span>
            </div>

            <el-button type="primary" size="large" class="checkout-btn" @click="checkout">
              <el-icon class="mr-4"><Wallet /></el-icon>
              Proceed to Checkout
            </el-button>

            <div class="payment-methods">
              <span class="summary-label">We Accept</span>
              <div class="payment-icons">
                <span class="pay-icon visa">VISA</span>
                <span class="pay-icon mc">MC</span>
                <span class="pay-icon pp">PP</span>
                <span class="pay-icon amex">AMEX</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <!-- Empty Cart -->
    <el-card class="koho-card" shadow="never" v-else>
      <el-empty description="Your cart is empty" :image-size="160">
        <el-button type="primary" @click="continueShopping">Start Shopping</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Goods, Delete, ArrowLeft, Wallet } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

interface CartItem {
  id: number
  name: string
  category: string
  price: number
  qty: number
  bgColor: string
}

const couponCode = ref('')
const couponApplied = ref(false)

const cartItems = ref<CartItem[]>([
  { id: 1, name: 'Wireless Bluetooth Headphones', category: 'Electronics', price: 79.99, qty: 1, bgColor: 'linear-gradient(135deg, #5A67F5, #8FA0FF)' },
  { id: 2, name: 'Smart Watch Pro Series 7', category: 'Electronics', price: 199.00, qty: 2, bgColor: 'linear-gradient(135deg, #3EBCB9, #6ee0dd)' },
  { id: 3, name: 'Premium Cotton Casual T-Shirt', category: 'Fashion', price: 29.99, qty: 3, bgColor: 'linear-gradient(135deg, #FFA47A, #ffc4a3)' },
  { id: 4, name: 'Running Sneakers Air Max', category: 'Sports', price: 89.99, qty: 1, bgColor: 'linear-gradient(135deg, #67C100, #85d533)' },
  { id: 5, name: 'Ceramic Coffee Mug Set of 4', category: 'Home & Living', price: 34.99, qty: 2, bgColor: 'linear-gradient(135deg, #E56809, #ff8a3c)' },
  { id: 6, name: 'Premium Yoga Mat Non-Slip', category: 'Sports', price: 49.99, qty: 1, bgColor: 'linear-gradient(135deg, #3EBCB9, #5dd4d1)' },
])

const recalc = () => {}

const subtotal = computed(() => cartItems.value.reduce((sum, item) => sum + item.price * item.qty, 0))
const discount = computed(() => (couponApplied.value ? subtotal.value * 0.1 : 0))
const shipping = computed(() => (subtotal.value > 100 || subtotal.value === 0 ? 0 : 9.99))
const tax = computed(() => (subtotal.value - discount.value) * 0.08)
const total = computed(() => subtotal.value - discount.value + shipping.value + tax.value)
const totalItems = computed(() => cartItems.value.reduce((sum, item) => sum + item.qty, 0))

const applyCoupon = () => {
  if (!couponCode.value) {
    ElMessage.warning('Please enter a coupon code')
    return
  }
  couponApplied.value = true
  ElMessage.success(`Coupon "${couponCode.value.toUpperCase()}" applied!`)
}

const removeItem = (index: number) => {
  cartItems.value.splice(index, 1)
  ElMessage.success('Item removed from cart')
}

const clearCart = () => {
  cartItems.value = []
  ElMessage.info('Cart cleared')
}

const continueShopping = () => {
  ElMessage.info('Continue shopping...')
}

const checkout = () => {
  ElMessage.success('Proceeding to checkout...')
}
</script>

<style scoped>
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #5A67F5;
  margin: 0 0 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid #f0f2f5;
  display: flex;
  align-items: center;
}
.item-count {
  font-size: 13px;
  font-weight: 400;
  color: #909399;
  margin-left: 8px;
}

/* Cart Items */
.cart-items-card {
  border-radius: 12px;
}
.cart-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #f5f5f5;
  flex-wrap: wrap;
}
.cart-item:last-of-type {
  border-bottom: none;
}
.cart-item-img {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.cart-item-info {
  flex: 1;
  min-width: 140px;
}
.cart-item-name {
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
  margin: 0 0 4px;
}
.cart-item-category {
  font-size: 12px;
  color: #909399;
}
.cart-item-price,
.cart-item-qty,
.cart-item-subtotal {
  display: flex;
  flex-direction: column;
  text-align: center;
  min-width: 80px;
}
.price-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}
.price-value {
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
}
.subtotal-value {
  font-size: 16px;
  font-weight: 600;
  color: #5A67F5;
}

.cart-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 20px;
  gap: 12px;
  flex-wrap: wrap;
}

/* Summary */
.summary-card {
  border-radius: 12px;
  position: sticky;
  top: 20px;
}
.coupon-section {
  margin-bottom: 4px;
}
.summary-label {
  font-size: 13px;
  font-weight: 500;
  color: #2B2B2B;
  display: block;
  margin-bottom: 10px;
}
.coupon-input-row {
  display: flex;
  gap: 8px;
}
.coupon-applied {
  margin-top: 10px;
}
.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
  color: #606266;
}
.discount-text {
  color: #67C100;
  font-weight: 500;
}
.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0 16px;
}
.summary-total span:first-child {
  font-size: 16px;
  font-weight: 600;
  color: #2B2B2B;
}
.total-value {
  font-size: 28px;
  font-weight: 700;
  color: #5A67F5;
}
.checkout-btn {
  width: 100%;
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}

/* Payment icons */
.payment-methods {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
}
.payment-icons {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}
.pay-icon {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}
.pay-icon.visa { background: #1A1F71; }
.pay-icon.mc { background: #EB001B; }
.pay-icon.pp { background: #003087; }
.pay-icon.amex { background: #006FCF; }

:deep(.el-button--primary) {
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}
.mr-4 {
  margin-right: 4px;
}
</style>
