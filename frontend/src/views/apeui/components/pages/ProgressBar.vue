<template>
  <div>
    <PageHeader title="Progress" :breadcrumb="['APEUI库', 'Components', 'Progress']" />

    <el-row :gutter="16">
      <el-col :span="14" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Linear Progress" style="margin-bottom: 16px">
          <div style="display: flex; flex-direction: column; gap: 18px">
            <el-progress :percentage="20" />
            <el-progress :percentage="40" status="success" />
            <el-progress :percentage="60" status="warning" />
            <el-progress :percentage="80" status="exception" />
            <el-progress :percentage="50" :show-text="false" />
          </div>
        </el-card>

        <el-card shadow="hover" header="Colors & Striped">
          <div style="display: flex; flex-direction: column; gap: 14px">
            <el-progress :percentage="35" color="#534686" />
            <el-progress :percentage="55" color="#3ebcb9" />
            <el-progress :percentage="75" color="#67c100" />
            <el-progress :percentage="90" color="#e56809" />
            <el-progress :percentage="100" striped striped-flow />
          </div>
        </el-card>
      </el-col>

      <el-col :span="10" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Circle Progress" style="margin-bottom: 16px">
          <div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: center">
            <el-progress type="circle" :percentage="0" />
            <el-progress type="circle" :percentage="25" />
            <el-progress type="circle" :percentage="50" status="success" />
            <el-progress type="circle" :percentage="75" status="warning" />
            <el-progress type="circle" :percentage="100" status="exception" />
            <el-progress type="circle" :percentage="65" color="#534686" :width="100" />
          </div>
        </el-card>

        <el-card shadow="hover" header="Dashboard Progress">
          <div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: center">
            <el-progress type="dashboard" :percentage="60" />
            <el-progress type="dashboard" :percentage="80" status="success" />
            <el-progress type="dashboard" :percentage="45" status="warning" />
            <el-progress type="dashboard" :percentage="30" color="#534686" :width="120" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" header="Animated Progress">
      <div style="display: flex; align-items: center; gap: 24px; margin-bottom: 16px">
        <el-progress :percentage="dynamicPercentage" color="#534686" style="flex: 1" />
        <el-progress type="circle" :percentage="dynamicPercentage" color="#534686" />
        <el-button type="primary" :disabled="dynamicPercentage >= 100" @click="increase">Increase</el-button>
        <el-button type="warning" :disabled="dynamicPercentage <= 0" @click="decrease">Decrease</el-button>
      </div>
      <div style="margin-bottom: 16px">
        <el-progress :percentage="dynamicPercentage" striped striped-flow :duration="5" />
      </div>
      <div style="display: flex; align-items: center; gap: 16px">
        <span style="min-width: 80px; color: #5a6273">Custom:</span>
        <el-slider v-model="dynamicPercentage" :max="100" style="flex: 1" />
        <span style="min-width: 40px; text-align: right">{{ dynamicPercentage }}%</span>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '../PageHeader.vue'

const dynamicPercentage = ref(0)

const increase = () => {
  dynamicPercentage.value = Math.min(100, dynamicPercentage.value + 10)
}

const decrease = () => {
  dynamicPercentage.value = Math.max(0, dynamicPercentage.value - 10)
}
</script>