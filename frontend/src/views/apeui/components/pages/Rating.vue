<template>
  <div>
    <PageHeader title="Rating" :breadcrumb="['APEUI库', 'Components', 'Rating']" />

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="基础评分">
          <div class="rating-row" v-for="item in basicRatings" :key="item.label">
            <span class="rating-label">{{ item.label }}</span>
            <el-rate v-model="item.value" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="半星评分 (allow-half)">
          <div class="rating-row" v-for="item in halfRatings" :key="item.label">
            <span class="rating-label">{{ item.label }}</span>
            <el-rate v-model="item.value" allow-half />
            <span class="rating-value">{{ item.value }} 分</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="只读评分">
          <div class="rating-row" v-for="item in readonlyRatings" :key="item.label">
            <span class="rating-label">{{ item.label }}</span>
            <el-rate :model-value="item.value" disabled />
            <span class="rating-value">{{ item.value }} / 5</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="不同最大值 (max)">
          <div class="rating-row" v-for="item in maxRatings" :key="item.label">
            <span class="rating-label">{{ item.label }}</span>
            <el-rate v-model="item.value" :max="item.max" />
            <span class="rating-value">{{ item.value }} / {{ item.max }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" header="带文字评分" style="margin-bottom: 16px">
      <div class="rating-with-text">
        <div class="rating-text-block">
          <el-rate v-model="textValue" :texts="rateTexts" @change="onRateChange" />
          <span class="rating-text-display">{{ currentText }}</span>
        </div>
        <el-divider />
        <div class="rating-row">
          <span class="rating-label">服务评价</span>
          <el-rate v-model="serviceValue" :texts="['极差', '失望', '一般', '满意', '超赞']" show-text />
        </div>
        <div class="rating-row" style="margin-top: 16px">
          <span class="rating-label">物流评价</span>
          <el-rate v-model="logisticsValue" :colors="['#DC0808', '#E56809', '#67C100']" show-text />
        </div>
      </div>
    </el-card>

    <el-card shadow="hover" header="自定义图标 & 颜色">
      <div class="rating-row" v-for="item in customRatings" :key="item.label">
        <span class="rating-label">{{ item.label }}</span>
        <el-rate
          v-model="item.value"
          :icons="item.icons"
          :void-icon="item.voidIcon"
          :colors="item.colors"
        />
        <span class="rating-value">{{ item.value }} 分</span>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { StarFilled, ChatRound, ChatLineRound, Star } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const basicRatings = ref([
  { label: '产品质量', value: 0 },
  { label: '服务态度', value: 0 },
  { label: '性价比', value: 0 },
])

const halfRatings = ref([
  { label: '整体满意', value: 3.5 },
  { label: '功能完整', value: 4.5 },
  { label: '界面美观', value: 4 },
])

const readonlyRatings = ref([
  { label: '综合评分', value: 5 },
  { label: '用户口碑', value: 4 },
  { label: '市场评价', value: 3 },
])

const maxRatings = ref([
  { label: 'max=10', value: 7, max: 10 },
  { label: 'max=7', value: 5, max: 7 },
  { label: 'max=3', value: 2, max: 3 },
])

const textValue = ref(3)
const rateTexts = ['很差', '较差', '还行', '推荐', '强烈推荐']
const currentText = computed(() => rateTexts[textValue.value - 1] || '还行')
const onRateChange = () => {}

const serviceValue = ref(4)
const logisticsValue = ref(5)

const customRatings = ref([
  {
    label: '心形评分',
    value: 3,
    icons: [StarFilled, StarFilled, StarFilled],
    voidIcon: Star,
    colors: ['#DC0808', '#E56809', '#DC0808'],
  },
  {
    label: '评论评分',
    value: 4,
    icons: [ChatLineRound, ChatLineRound, ChatLineRound],
    voidIcon: ChatRound,
    colors: ['#5A67F5', '#7F8AF8', '#5A67F5'],
  },
])
</script>

<style scoped>
.rating-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f5;
}
.rating-row:last-child {
  border-bottom: none;
}
.rating-label {
  width: 100px;
  color: #5a6273;
  font-size: 14px;
  white-space: nowrap;
}
.rating-value {
  color: #5A67F5;
  font-size: 14px;
  font-weight: 600;
}
.rating-text-block {
  display: flex;
  align-items: center;
  gap: 16px;
}
.rating-text-display {
  color: #5A67F5;
  font-weight: 600;
  font-size: 15px;
}
.rating-with-text {
  padding: 4px 0;
}
</style>
