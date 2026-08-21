<template>
  <div>
    <PageHeader title="按钮组" :breadcrumb="['APEUI库', '组件示例', '按钮组']" />

    <el-card shadow="hover" header="基础按钮组" style="margin-bottom: 16px">
      <div style="display: flex; flex-direction: column; gap: 16px">
        <el-button-group>
          <el-button>左</el-button>
          <el-button>中</el-button>
          <el-button>右</el-button>
        </el-button-group>
        <el-button-group>
          <el-button type="primary"><el-icon><ArrowLeft /></el-icon> 上一页</el-button>
          <el-button type="primary">下一页 <el-icon><ArrowRight /></el-icon></el-button>
        </el-button-group>
      </div>
    </el-card>

    <el-card shadow="hover" header="颜色变体" style="margin-bottom: 16px">
      <el-button-group>
        <el-button type="success">成功</el-button>
        <el-button type="warning">警告</el-button>
        <el-button type="danger">危险</el-button>
        <el-button type="info">信息</el-button>
      </el-button-group>
    </el-card>

    <el-card shadow="hover" header="图标按钮组" style="margin-bottom: 16px">
      <el-button-group>
        <el-button type="primary"><el-icon><EditPen /></el-icon></el-button>
        <el-button type="primary"><el-icon><Share /></el-icon></el-button>
        <el-button type="primary"><el-icon><Delete /></el-icon></el-button>
      </el-button-group>
    </el-card>

    <el-card shadow="hover" header="尺寸">
      <div style="display: flex; flex-direction: column; gap: 16px">
        <el-button-group size="large">
          <el-button type="primary">L</el-button>
          <el-button type="primary">M</el-button>
          <el-button type="primary">R</el-button>
        </el-button-group>
        <el-button-group size="small">
          <el-button type="primary">L</el-button>
          <el-button type="primary">M</el-button>
          <el-button type="primary">R</el-button>
        </el-button-group>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'
</script>
