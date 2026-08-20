<template>
  <div>
    <PageHeader title="State Color" :breadcrumb="['APEUI库', 'Components', 'State Color']" />
    <el-row :gutter="16">
      <el-col :span="8" v-for="item in colorList" :key="item.name" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <div :style="{ background: item.color, height: '100px', borderRadius: '8px', marginBottom: '12px' }"></div>
          <h4 style="margin: 0 0 4px; font-weight: 600">{{ item.name }}</h4>
          <p style="margin: 0; color: #909399; font-size: 13px">{{ item.desc }}</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'

const colorList = [
  { name: 'Primary', color: '#534686', desc: '#534686 — 主题主色' },
  { name: 'Success', color: '#67C100', desc: '#67C100 — 成功状态' },
  { name: 'Info', color: '#3EBCB9', desc: '#3EBCB9 — 信息状态' },
  { name: 'Warning', color: '#E56809', desc: '#E56809 — 警告状态' },
  { name: 'Danger', color: '#DC0808', desc: '#DC0808 — 危险状态' },
  { name: 'Secondary', color: '#FFA47A', desc: '#FFA47A — 次要色' },
]
</script>
