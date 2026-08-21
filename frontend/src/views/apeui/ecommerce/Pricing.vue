<template>
  <div class="pricing-page">
    <PageHeader title="定价方案" :breadcrumb="['APEUI库', '电商模块', '定价方案']" />

    <div class="pricing-header">
      <h2>选择您的套餐</h2>
      <p>选择最适合您业务需求的套餐方案</p>
    </div>

    <el-row :gutter="24" class="pricing-cards">
      <el-col :span="8" v-for="plan in plans" :key="plan.name">
        <el-card shadow="hover" :class="['pricing-card', { popular: plan.popular }]">
          <div class="plan-badge" v-if="plan.popular">最受欢迎</div>
          <div class="plan-name">{{ plan.name }}</div>
          <div class="plan-price">
            <span class="currency">$</span>
            <span class="amount">{{ plan.price }}</span>
            <span class="period">/月</span>
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
            开始使用
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
    description: '适合刚起步的小型企业',
    popular: false,
    features: [
      '1,000 products',
      '基础分析',
      '邮件支持',
      '2 team members',
      '5 GB storage',
    ],
  },
  {
    name: 'Pro',
    price: 49,
    description: '适合有更多需求的成长型企业',
    popular: true,
    features: [
      '10,000 products',
      '高级分析',
      '优先支持',
      '10 team members',
      '50 GB storage',
      '自定义品牌',
      'API 访问',
    ],
  },
  {
    name: 'Enterprise',
    price: 99,
    description: '适合需要完全控制的大规模业务',
    popular: false,
    features: [
      '无限商品',
      '实时分析',
      '24/7 phone support',
      '无限团队成员',
      '500 GB storage',
      '自定义品牌',
      'API 访问',
      '专属经理',
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
  border: 2px solid #5A67F5;
}

.plan-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: #5A67F5;
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
  color: #5A67F5;
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
  background: #5A67F5;
  border-color: #5A67F5;
}

.pricing-card.popular .plan-btn:hover {
  background: #463b72;
  border-color: #463b72;
}
</style>
