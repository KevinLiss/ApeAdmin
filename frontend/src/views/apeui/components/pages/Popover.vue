<template>
  <div>
    <PageHeader title="Popover" :breadcrumb="['APEUI库', 'Components', 'Popover']" />

    <el-card shadow="hover" header="Basic Usage" style="margin-bottom: 16px">
      <el-popover placement="top" title="Title" :width="200" trigger="click" content="This is a basic popover with click trigger.">
        <template #reference>
          <el-button type="primary">Click Me</el-button>
        </template>
      </el-popover>

      <el-popover placement="bottom" :width="200" trigger="click" content="Popover content without a title.">
        <template #reference>
          <el-button type="primary">No Title</el-button>
        </template>
      </el-popover>
    </el-card>

    <el-card shadow="hover" header="Trigger Types" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-popover placement="top" title="Hover" :width="200" trigger="hover" content="This popover shows on hover.">
          <template #reference>
            <el-button>Hover Me</el-button>
          </template>
        </el-popover>

        <el-popover placement="bottom" title="Click" :width="200" trigger="click" content="This popover shows on click.">
          <template #reference>
            <el-button>Click Me</el-button>
          </template>
        </el-popover>

        <el-popover placement="right" title="Focus" :width="200" trigger="focus" content="This popover shows on focus.">
          <template #reference>
            <el-button>Focus Me</el-button>
          </template>
        </el-popover>
      </div>
    </el-card>

    <el-card shadow="hover" header="Rich Content" style="margin-bottom: 16px">
      <el-popover placement="right" :width="320" trigger="click">
        <template #reference>
          <el-button type="primary">Rich Content</el-button>
        </template>
        <template #default>
          <div class="popover-rich">
            <div class="rich-head">
              <el-avatar :size="40" style="background: #5A67F5; flex-shrink: 0">
                <el-icon :size="20"><UserFilled /></el-icon>
              </el-avatar>
              <div style="margin-left: 12px">
                <div style="font-weight: 600; font-size: 14px">Alex Morgan</div>
                <div style="font-size: 12px; color: #909399">Product Designer</div>
              </div>
            </div>
            <div style="margin-top: 12px; font-size: 13px; color: #5a6273; line-height: 1.7">
              This popover contains rich content including avatar, description text and action buttons —
              anything you can put in a template.
            </div>
            <div style="display: flex; gap: 8px; margin-top: 14px">
              <el-button size="small" type="primary">Follow</el-button>
              <el-button size="small">Message</el-button>
              <el-button size="small" type="danger" plain>Block</el-button>
            </div>
          </div>
        </template>
      </el-popover>
    </el-card>

    <el-card shadow="hover" header="Placements">
      <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: center">
        <el-popover placement="top" title="Top" :width="180" trigger="hover" content="Placed on top.">
          <template #reference>
            <el-button size="small">Top</el-button>
          </template>
        </el-popover>
        <el-popover placement="bottom" title="Bottom" :width="180" trigger="hover" content="Placed on bottom.">
          <template #reference>
            <el-button size="small">Bottom</el-button>
          </template>
        </el-popover>
        <el-popover placement="left" title="Left" :width="180" trigger="hover" content="Placed on left.">
          <template #reference>
            <el-button size="small">Left</el-button>
          </template>
        </el-popover>
        <el-popover placement="right" title="Right" :width="180" trigger="hover" content="Placed on right.">
          <template #reference>
            <el-button size="small">Right</el-button>
          </template>
        </el-popover>
        <el-popover placement="top-start" title="Top Start" :width="180" trigger="hover" content="Placed on top-start.">
          <template #reference>
            <el-button size="small">Top Start</el-button>
          </template>
        </el-popover>
        <el-popover placement="bottom-end" title="Bottom End" :width="180" trigger="hover" content="Placed on bottom-end.">
          <template #reference>
            <el-button size="small">Bottom End</el-button>
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