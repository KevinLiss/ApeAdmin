<template>
  <div>
    <PageHeader title="Range Slider" :breadcrumb="['APEUI库', 'Components', 'Range Slider']" />

    <el-row :gutter="30">
      <!-- Default Slider -->
      <el-col :span="12" style="margin-bottom: 30px">
        <el-card>
          <template #header><span class="card-title">Default Slider</span></template>
          <div class="slider-demo">
            <el-slider v-model="defaultVal" />
            <div class="slider-value">Value: {{ defaultVal }}</div>
          </div>
        </el-card>
      </el-col>

      <!-- Min-Max Range -->
      <el-col :span="12" style="margin-bottom: 30px">
        <el-card>
          <template #header><span class="card-title">Min-Max Range</span></template>
          <div class="slider-demo">
            <el-slider v-model="rangeVal" range :min="0" :max="100" />
            <div class="slider-value">Range: {{ rangeVal[0] }} - {{ rangeVal[1] }}</div>
          </div>
        </el-card>
      </el-col>

      <!-- With Prefix -->
      <el-col :span="12" style="margin-bottom: 30px">
        <el-card>
          <template #header><span class="card-title">With Prefix ($)</span></template>
          <div class="slider-demo">
            <el-slider v-model="prefixVal" :min="0" :max="1000" :step="50" />
            <div class="slider-value">Price: ${{ prefixVal }}</div>
          </div>
        </el-card>
      </el-col>

      <!-- Negative Range -->
      <el-col :span="12" style="margin-bottom: 30px">
        <el-card>
          <template #header><span class="card-title">Negative Range</span></template>
          <div class="slider-demo">
            <el-slider v-model="negativeVal" :min="-50" :max="50" />
            <div class="slider-value">Value: {{ negativeVal }}</div>
          </div>
        </el-card>
      </el-col>

      <!-- Steps -->
      <el-col :span="12" style="margin-bottom: 30px">
        <el-card>
          <template #header><span class="card-title">Step Slider (step=10)</span></template>
          <div class="slider-demo">
            <el-slider v-model="stepVal" :min="0" :max="100" :step="10" show-stops />
            <div class="slider-value">Value: {{ stepVal }}</div>
          </div>
        </el-card>
      </el-col>

      <!-- With Input -->
      <el-col :span="12" style="margin-bottom: 30px">
        <el-card>
          <template #header><span class="card-title">With Input Box</span></template>
          <div class="slider-demo">
            <el-slider v-model="inputVal" :min="0" :max="100" show-input />
            <div class="slider-value">Value: {{ inputVal }}</div>
          </div>
        </el-card>
      </el-col>

      <!-- Vertical -->
      <el-col :span="12" style="margin-bottom: 30px">
        <el-card>
          <template #header><span class="card-title">Vertical Slider</span></template>
          <div class="slider-demo vertical-demo">
            <el-slider v-model="verticalVal" vertical height="200px" />
            <div class="slider-value">Value: {{ verticalVal }}</div>
          </div>
        </el-card>
      </el-col>

      <!-- Disabled -->
      <el-col :span="12" style="margin-bottom: 30px">
        <el-card>
          <template #header><span class="card-title">Disabled Slider</span></template>
          <div class="slider-demo">
            <el-slider v-model="disabledVal" disabled />
            <div class="slider-value">Value: {{ disabledVal }} (disabled)</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '../PageHeader.vue'

const defaultVal = ref(50)
const rangeVal = ref([30, 70])
const prefixVal = ref(500)
const negativeVal = ref(0)
const stepVal = ref(40)
const inputVal = ref(60)
const verticalVal = ref(50)
const disabledVal = ref(70)
</script>

<style scoped>
.slider-demo {
  padding: 10px 20px;
}
.slider-value {
  margin-top: 16px;
  font-size: 14px;
  color: #5A67F5;
  font-weight: 500;
}
.vertical-demo {
  display: flex;
  align-items: center;
  gap: 30px;
  height: 240px;
}
.card-title {
  font-size: 20px;
  font-weight: 500;
  color: #5A67F5;
}
</style>
