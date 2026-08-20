<template>
  <div>
    <PageHeader title="Tooltip" :breadcrumb="['APEUI库', 'Components', 'Tooltip']" />

    <el-card shadow="hover" header="Basic Usage" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-tooltip content="Simple tooltip" placement="top">
          <el-button type="primary">Hover Me</el-button>
        </el-tooltip>

        <el-tooltip content="Tooltip with effect dark" effect="dark" placement="top">
          <el-button>Dark Effect</el-button>
        </el-tooltip>

        <el-tooltip content="Tooltip with effect light" effect="light" placement="top">
          <el-button>Light Effect</el-button>
        </el-tooltip>
      </div>
    </el-card>

    <el-card shadow="hover" header="Placements" style="margin-bottom: 16px">
      <div class="placement-row" style="display: flex; gap: 16px; align-items: center; justify-content: center">
        <el-tooltip content="Top Start" placement="top-start">
          <el-button size="small">Top Start</el-button>
        </el-tooltip>
        <el-tooltip content="Top" placement="top">
          <el-button size="small">Top</el-button>
        </el-tooltip>
        <el-tooltip content="Top End" placement="top-end">
          <el-button size="small">Top End</el-button>
        </el-tooltip>
        <el-tooltip content="Left" placement="left">
          <el-button size="small">Left</el-button>
        </el-tooltip>
        <el-tooltip content="Bottom" placement="bottom">
          <el-button size="small">Bottom</el-button>
        </el-tooltip>
        <el-tooltip content="Right" placement="right">
          <el-button size="small">Right</el-button>
        </el-tooltip>
      </div>
    </el-card>

    <el-card shadow="hover" header="Custom Content" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-tooltip placement="top">
          <template #content>
            <div style="display: flex; align-items: center; gap: 8px">
              <el-icon :size="16"><StarFilled style="color: #f2b274" /></el-icon>
              <span style="font-weight: 600">Custom Rich Tooltip</span>
            </div>
            <div style="font-size: 12px; opacity: 0.85">This tooltip uses a custom slot with icons and text.</div>
          </template>
          <el-button type="primary">Custom Slot</el-button>
        </el-tooltip>

        <el-tooltip placement="bottom">
          <template #content>
            <div style="text-align: center; padding: 4px 8px">
              <div style="font-size: 18px; font-weight: 700; color: #f2b274">98.5%</div>
              <div style="font-size: 12px">Uptime this month</div>
            </div>
          </template>
          <el-button>Styled Content</el-button>
        </el-tooltip>
      </div>
    </el-card>

    <el-card shadow="hover" header="Customize Tooltip (Theme/Width/Arrow)">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-tooltip content="Custom background color" placement="top" :show-arrow="false" effect="light" popper-class="apeui-tooltip-primary">
          <el-button type="primary">No Arrow / Custom Class</el-button>
        </el-tooltip>

        <el-tooltip :content="longText" placement="right" :width="260" effect="light">
          <span style="color: #5a6273; font-size: 13px">Hover for long text</span>
        </el-tooltip>
        <span style="color: #909399; font-size: 13px">(Wide tooltip rendered below)</span>
        <el-tooltip content="This is a wide tooltip" placement="right" :width="260" effect="light">
          <el-button>Wide Tooltip</el-button>
        </el-tooltip>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { StarFilled } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const longText = 'This is a long tooltip that can span multiple lines when the width is constrained.'
</script>

<style scoped>
.placement-row {
  flex-wrap: wrap;
}
</style>