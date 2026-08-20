<template>
  <div>
    <PageHeader title="Box Shadow" :breadcrumb="['APEUI库', 'Components', 'Box Shadow']" />

    <el-row :gutter="16">
      <el-col :span="6" v-for="item in shadows" :key="item.name" style="margin-bottom: 20px">
        <el-card shadow="hover" :body-style="{ padding: '30px', textAlign: 'center' }">
          <div :style="{ boxShadow: item.shadow, height: '80px', borderRadius: '8px', background: '#fff', marginBottom: '16px' }"></div>
          <h4 style="margin: 0 0 4px; font-weight: 600">{{ item.name }}</h4>
          <code style="font-size: 11px; color: #909399">{{ item.shadow }}</code>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'

const shadows = [
  { name: 'Shadow Sm', shadow: '0 1px 3px rgba(0,0,0,0.08)' },
  { name: 'Shadow Md', shadow: '0 4px 12px rgba(0,0,0,0.1)' },
  { name: 'Shadow Lg', shadow: '0 8px 24px rgba(0,0,0,0.12)' },
  { name: 'Shadow Xl', shadow: '0 16px 40px rgba(0,0,0,0.16)' },
  { name: 'Purple Glow', shadow: '0 8px 24px rgba(83,70,134,0.25)' },
  { name: 'Green Glow', shadow: '0 8px 24px rgba(103,193,0,0.25)' },
  { name: 'Orange Glow', shadow: '0 8px 24px rgba(229,104,9,0.25)' },
  { name: 'Red Glow', shadow: '0 8px 24px rgba(220,8,8,0.25)' },
]
</script>
