<template>
  <div class="pricing-page">
    <PageHeader title="Pricing" :breadcrumb="['APEUI库', 'Ecommerce', 'Pricing']" />

    <div class="pricing-header">
      <h2>Choose Your Plan</h2>
      <p>Select the plan that best fits your business needs</p>
    </div>

    <el-row :gutter="24" class="pricing-cards">
      <el-col :span="8" v-for="plan in plans" :key="plan.name">
        <el-card shadow="hover" :class="['pricing-card', { popular: plan.popular }]">
          <div class="plan-badge" v-if="plan.popular">Most Popular</div>
          <div class="plan-name">{{ plan.name }}</div>
          <div class="plan-price">
            <span class="currency">$</span>
            <span class="amount">{{ plan.price }}</span>
            <span class="period">/month</span>
          </div>
          <p class="plan-desc">{{ plan.description }}</p>
          <ul class="plan-features">
            <li v-for="feature in plan.features" :key="feature">
              <el-icon color="#67C100" size="16"><Check /></el-icon>
              {{ feature }}
            </li>
          </ul>
          <el-button
            :type="plan.popular ? 'primary' : 'default'"
            size="large"
            class="plan-btn"
            round
          >
            Get Started
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import { Check } from '@element-plus/icons-vue'

const plans = [
  {
    name: 'Basic',
    price: 19,
    description: 'Perfect for small businesses getting started',
    popular: false,
    features: [
      '1,000 products',
      'Basic analytics',
      'Email support',
      '2 team members',
      '5 GB storage',
    ],
  },
  {
    name: 'Pro',
    price: 49,
    description: 'Ideal for growing businesses with more needs',
    popular: true,
    features: [
      '10,000 products',
      'Advanced analytics',
      'Priority support',
      '10 team members',
      '50 GB storage',
      'Custom branding',
      'API access',
    ],
  },
  {
    name: 'Enterprise',
    price: 99,
    description: 'For large-scale operations with full control',
    popular: false,
    features: [
      'Unlimited products',
      'Real-time analytics',
      '24/7 phone support',
      'Unlimited team members',
      '500 GB storage',
      'Custom branding',
      'API access',
      'Dedicated manager',
      'SLA guarantee',
    ],
  },
]
</script>

<style scoped>
.pricing-page {
  padding: 0;
}

.pricing-header {
  text-align: center;
  padding: 32px 0 40px;
}

.pricing-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 8px;
}

.pricing-header p {
  font-size: 15px;
  color: #909399;
  margin: 0;
}

.pricing-cards {
  margin-bottom: 24px;
}

.pricing-card {
  text-align: center;
  padding: 8px 8px 24px;
  position: relative;
  min-height: 480px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pricing-card.popular {
  border: 2px solid #534686;
}

.plan-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: #534686;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 16px;
  border-radius: 20px;
  white-space: nowrap;
}

.plan-name {
  font-size: 20px;
  font-weight: 700;
  color: #534686;
  margin-top: 16px;
}

.plan-price {
  margin: 16px 0 12px;
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.plan-price .currency {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.plan-price .amount {
  font-size: 48px;
  font-weight: 800;
  color: #303133;
  line-height: 1;
}

.plan-price .period {
  font-size: 15px;
  color: #909399;
}

.plan-desc {
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
  margin: 0 0 20px;
  max-width: 240px;
}

.plan-features {
  list-style: none;
  padding: 0;
  margin: 0 0 28px;
  text-align: left;
  width: 100%;
  max-width: 240px;
}

.plan-features li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
  padding: 6px 0;
}

.plan-btn {
  width: 100%;
  max-width: 200px;
  margin-top: auto;
}

.pricing-card.popular .plan-btn {
  background: #534686;
  border-color: #534686;
}

.pricing-card.popular .plan-btn:hover {
  background: #463b72;
  border-color: #463b72;
}
</style>
