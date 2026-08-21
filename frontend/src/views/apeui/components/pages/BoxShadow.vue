<template>
  <div class="box-shadow-page">
    <PageHeader title="阴影效果" :breadcrumb="['APEUI库', '组件示例', '阴影效果']" />

    <el-card class="shadow-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">示例</span>
          <span class="card-subtitle">支持 shadow-none 及三种默认尺寸。</span>
        </div>
      </template>

      <!-- Larger shadow -->
      <h6 class="group-title">Larger shadow</h6>
      <el-row :gutter="30" class="shadow-group">
        <el-col :span="8" v-for="n in 3" :key="'lg-' + n">
          <div class="shadow-block" style="box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)">
            Larger shadow
          </div>
        </el-col>
      </el-row>

      <!-- Regular shadow -->
      <h6 class="group-title">Regular shadow</h6>
      <el-row :gutter="30" class="shadow-group">
        <el-col :span="8" v-for="n in 3" :key="'reg-' + n">
          <div class="shadow-block" style="box-shadow: 0 .125rem .25rem rgba(0,0,0,.075)">
            Regular shadow
          </div>
        </el-col>
      </el-row>

      <!-- Small shadow -->
      <h6 class="group-title">Small shadow</h6>
      <el-row :gutter="30" class="shadow-group">
        <el-col :span="8" v-for="n in 3" :key="'sm-' + n">
          <div class="shadow-block" style="box-shadow: 0 .0625rem .125rem rgba(0,0,0,.05)">
            Small shadow
          </div>
        </el-col>
      </el-row>

      <!-- No shadow -->
      <h6 class="group-title">No shadow</h6>
      <el-row :gutter="30" class="shadow-group">
        <el-col :span="8" v-for="n in 3" :key="'none-' + n">
          <div class="shadow-block" style="box-shadow: none">
            No shadow
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'
</script>

<style scoped>
.box-shadow-page {
  width: 100%;
}

.shadow-card {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #5A67F5;
}

.card-subtitle {
  font-size: 13px;
  color: #909399;
  font-weight: 400;
}

.group-title {
  font-size: 14px;
  font-weight: 600;
  color: #5A67F5;
  margin: 0 0 15px 0;
  padding-left: 2px;
}

.shadow-group {
  margin-bottom: 30px;
}

.shadow-group:last-child {
  margin-bottom: 0;
}

.shadow-block {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  border: 1px solid #ebeef5;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
