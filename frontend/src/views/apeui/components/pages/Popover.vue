<template>
  <div>
    <PageHeader title="气泡卡片" :breadcrumb="['APEUI库', '组件示例', '气泡卡片']" />

    <el-card shadow="hover" header="基础用法" style="margin-bottom: 16px">
      <el-popover placement="top" title="Title" :width="200" trigger="click" content="This is a basic popover with click trigger.">
        <template #reference>
          <el-button type="primary">点击我</el-button>
        </template>
      </el-popover>

      <el-popover placement="bottom" :width="200" trigger="click" content="Popover content without a title.">
        <template #reference>
          <el-button type="primary">无标题</el-button>
        </template>
      </el-popover>
    </el-card>

    <el-card shadow="hover" header="触发方式" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-popover placement="top" title="Hover" :width="200" trigger="hover" content="This popover shows on hover.">
          <template #reference>
            <el-button>悬停我</el-button>
          </template>
        </el-popover>

        <el-popover placement="bottom" title="Click" :width="200" trigger="click" content="This popover shows on click.">
          <template #reference>
            <el-button>点击我</el-button>
          </template>
        </el-popover>

        <el-popover placement="right" title="Focus" :width="200" trigger="focus" content="This popover shows on focus.">
          <template #reference>
            <el-button>聚焦我</el-button>
          </template>
        </el-popover>
      </div>
    </el-card>

    <el-card shadow="hover" header="富文本内容" style="margin-bottom: 16px">
      <el-popover placement="right" :width="320" trigger="click">
        <template #reference>
          <el-button type="primary">富内容</el-button>
        </template>
        <template #default>
          <div class="popover-rich">
            <div class="rich-head">
              <el-avatar :size="40" style="background: #5A67F5; flex-shrink: 0">
                <el-icon :size="20"><UserFilled /></el-icon>
              </el-avatar>
              <div style="margin-left: 12px">
                <div style="font-weight: 600; font-size: 14px">Alex Morgan</div>
                <div style="font-size: 12px; color: #909399">产品设计师</div>
              </div>
            </div>
            <div style="margin-top: 12px; font-size: 13px; color: #5a6273; line-height: 1.7">
              This popover contains rich content including avatar, description text and action buttons —
              anything you can put in a template.
            </div>
            <div style="display: flex; gap: 8px; margin-top: 14px">
              <el-button size="small" type="primary">关注</el-button>
              <el-button size="small">消息</el-button>
              <el-button size="small" type="danger" plain>拉黑</el-button>
            </div>
          </div>
        </template>
      </el-popover>
    </el-card>

    <el-card shadow="hover" header="弹出位置">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-popover placement="top" title="Top" :width="180" trigger="hover" content="Placed on top.">
          <template #reference>
            <el-button size="small">顶部</el-button>
          </template>
        </el-popover>
        <el-popover placement="bottom" title="Bottom" :width="180" trigger="hover" content="Placed on bottom.">
          <template #reference>
            <el-button size="small">底部</el-button>
          </template>
        </el-popover>
        <el-popover placement="left" title="Left" :width="180" trigger="hover" content="Placed on left.">
          <template #reference>
            <el-button size="small">左</el-button>
          </template>
        </el-popover>
        <el-popover placement="right" title="Right" :width="180" trigger="hover" content="Placed on right.">
          <template #reference>
            <el-button size="small">右</el-button>
          </template>
        </el-popover>
        <el-popover placement="top-start" title="顶部起始" :width="180" trigger="hover" content="Placed on top-start.">
          <template #reference>
            <el-button size="small">顶部起始</el-button>
          </template>
        </el-popover>
        <el-popover placement="bottom-end" title="底部末尾" :width="180" trigger="hover" content="Placed on bottom-end.">
          <template #reference>
            <el-button size="small">底部末尾</el-button>
          </template>
        </el-popover>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { UserFilled } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'
</script>

<style scoped>
.popover-rich .rich-head {
  display: flex;
  align-items: center;
}
</style>