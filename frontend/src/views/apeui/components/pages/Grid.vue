<template>
  <div>
    <PageHeader title="Grid System" :breadcrumb="['APEUI库', 'Components', 'Grid']" />

    <el-card shadow="hover" header="Basic Grid (24 columns)" style="margin-bottom: 16px">
      <el-row :gutter="12">
        <el-col :span="24"><div class="grid-demo">span 24</div></el-col>
      </el-row>
      <el-row :gutter="12" style="margin-top: 10px">
        <el-col :span="12" v-for="i in 2" :key="i"><div class="grid-demo">span 12</div></el-col>
      </el-row>
      <el-row :gutter="12" style="margin-top: 10px">
        <el-col :span="8" v-for="i in 3" :key="i"><div class="grid-demo">span 8</div></el-col>
      </el-row>
      <el-row :gutter="12" style="margin-top: 10px">
        <el-col :span="6" v-for="i in 4" :key="i"><div class="grid-demo">span 6</div></el-col>
      </el-row>
      <el-row :gutter="12" style="margin-top: 10px">
        <el-col :span="4" v-for="i in 6" :key="i"><div class="grid-demo">4</div></el-col>
      </el-row>
    </el-card>

    <el-card shadow="hover" header="Offset & Alignment" style="margin-bottom: 16px">
      <el-row :gutter="12" style="margin-bottom: 10px">
        <el-col :span="6" :offset="6"><div class="grid-demo">span 6 offset 6</div></el-col>
      </el-row>
      <el-row :gutter="12" justify="center" style="margin-bottom: 10px">
        <el-col :span="8"><div class="grid-demo">center</div></el-col>
      </el-row>
      <el-row :gutter="12" justify="end">
        <el-col :span="8"><div class="grid-demo">right</div></el-col>
      </el-row>
    </el-card>

    <el-card shadow="hover" header="Responsive">
      <el-row :gutter="12">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="i in 4" :key="i">
          <div class="grid-demo">Responsive {{ i }}</div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'
</script>

<style scoped>
.grid-demo {
  background: #e8e7f4;
  border-radius: 6px;
  padding: 12px 0;
  text-align: center;
  font-size: 13px;
  color: #534686;
  font-weight: 600;
}
</style>
