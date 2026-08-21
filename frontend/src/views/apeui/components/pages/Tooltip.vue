<template>
  <div>
    <PageHeader title="文字提示" :breadcrumb="['APEUI库', '组件示例', '文字提示']" />

    <el-card shadow="hover" header="基础用法" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-tooltip content="Simple tooltip" placement="top">
          <el-button type="primary">悬停我</el-button>
        </el-tooltip>

        <el-tooltip content="Tooltip with effect dark" effect="dark" placement="top">
          <el-button>深色效果</el-button>
        </el-tooltip>

        <el-tooltip content="Tooltip with effect light" effect="light" placement="top">
          <el-button>浅色效果</el-button>
        </el-tooltip>
      </div>
    </el-card>

    <el-card shadow="hover" header="弹出位置" style="margin-bottom: 16px">
      <div class="placement-row" style="display: flex; gap: 16px; align-items: center; justify-content: center">
        <el-tooltip content="顶部起始" placement="top-start">
          <el-button size="small">顶部起始</el-button>
        </el-tooltip>
        <el-tooltip content="Top" placement="top">
          <el-button size="small">顶部</el-button>
        </el-tooltip>
        <el-tooltip content="顶部末尾" placement="top-end">
          <el-button size="small">顶部末尾</el-button>
        </el-tooltip>
        <el-tooltip content="Left" placement="left">
          <el-button size="small">左</el-button>
        </el-tooltip>
        <el-tooltip content="Bottom" placement="bottom">
          <el-button size="small">底部</el-button>
        </el-tooltip>
        <el-tooltip content="Right" placement="right">
          <el-button size="small">右</el-button>
        </el-tooltip>
      </div>
    </el-card>

    <el-card shadow="hover" header="自定义内容" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-tooltip placement="top">
          <template #content>
            <div style="display: flex; align-items: center; gap: 8px">
              <el-icon :size="16"><StarFilled style="color: #f2b274" /></el-icon>
              <span style="font-weight: 600">自定义富提示</span>
            </div>
            <div style="font-size: 12px; opacity: 0.85">该提示使用带图标和文字的的自定义插槽。</div>
          </template>
          <el-button type="primary">自定义插槽</el-button>
        </el-tooltip>

        <el-tooltip placement="bottom">
          <template #content>
            <div style="text-align: center; padding: 4px 8px">
              <div style="font-size: 18px; font-weight: 700; color: #f2b274">98.5%</div>
              <div style="font-size: 12px">本月在线时长</div>
            </div>
          </template>
          <el-button>自定义样式内容</el-button>
        </el-tooltip>
      </div>
    </el-card>

    <el-card shadow="hover" header="自定义提示（主题/宽度/箭头）">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-tooltip content="自定义背景颜色" placement="top" :show-arrow="false" effect="light" popper-class="apeui-tooltip-primary">
          <el-button type="primary">无箭头 / 自定义样式</el-button>
        </el-tooltip>

        <el-tooltip :content="longText" placement="right" :width="260" effect="light">
          <span style="color: #5a6273; font-size: 13px">悬停查看长文本</span>
        </el-tooltip>
        <span style="color: #909399; font-size: 13px">（下方为宽提示）</span>
        <el-tooltip content="这是一个宽提示" placement="right" :width="260" effect="light">
          <el-button>宽提示</el-button>
        </el-tooltip>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { StarFilled } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const longText = '这是一段较长的提示文本，在宽度受限时会自动换行显示。'
</script>

<style scoped>
.placement-row {
  flex-wrap: wrap;
}
</style>