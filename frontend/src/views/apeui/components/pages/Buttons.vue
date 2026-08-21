<template>
  <div>
    <PageHeader title="按钮" :breadcrumb="['APEUI库', '组件示例', '按钮']" />

    <el-card shadow="hover" header="默认按钮" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center">
        <el-button>默认</el-button>
        <el-button type="primary">主要</el-button>
        <el-button type="success">成功</el-button>
        <el-button type="info">信息</el-button>
        <el-button type="warning">警告</el-button>
        <el-button type="danger">危险</el-button>
        <el-button type="primary" plain>朴素</el-button>
        <el-button type="primary" round>圆角</el-button>
        <el-button type="primary" circle><el-icon><Search /></el-icon></el-button>
        <el-button type="primary" disabled>禁用</el-button>
      </div>
    </el-card>

    <el-card shadow="hover" header="尺寸" style="margin-bottom: 16px">
      <div style="display: flex; gap: 12px; align-items: center">
        <el-button size="large">大</el-button>
        <el-button>默认</el-button>
        <el-button size="small">小</el-button>
        <el-button size="large" type="primary"><el-icon><Plus /></el-icon> <span>添加</span></el-button>
      </div>
    </el-card>

    <el-card shadow="hover" header="带图标" style="margin-bottom: 16px">
      <div style="display: flex; gap: 12px; align-items: center">
        <el-button type="primary"><el-icon><Plus /></el-icon> <span>新建</span></el-button>
        <el-button type="success"><el-icon><Check /></el-icon> <span>保存</span></el-button>
        <el-button type="warning"><el-icon><Star /></el-icon> <span>收藏</span></el-button>
        <el-button type="danger"><el-icon><Delete /></el-icon> <span>删除</span></el-button>
        <el-button type="info"><el-icon><Download /></el-icon> <span>下载</span></el-button>
        <el-button><el-icon><Refresh /></el-icon> <span>刷新</span></el-button>
      </div>
    </el-card>

    <el-card shadow="hover" header="文字与链接按钮" style="margin-bottom: 16px">
      <div style="display: flex; gap: 12px; align-items: center">
        <el-button text>文字按钮</el-button>
        <el-button text type="primary">文字主要</el-button>
        <el-button link>链接按钮</el-button>
        <el-button link type="primary">链接主要</el-button>
        <el-button link type="success">链接成功</el-button>
      </div>
    </el-card>

    <el-card shadow="hover" header="加载状态">
      <div style="display: flex; gap: 12px; align-items: center">
        <el-button type="primary" :loading="true">加载中...</el-button>
        <el-button type="primary" loading-icon="Loading">自定义加载</el-button>
        <el-button type="success" :loading-icon="Loading">
          <template #loading><el-icon class="is-loading"><Loading /></el-icon></template>
          Custom Icon
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'
</script>
