<template>
  <div>
    <PageHeader title="Buttons" :breadcrumb="['APEUI库', 'Components', 'Buttons']" />

    <el-card shadow="hover" header="Default Buttons" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center">
        <el-button>Default</el-button>
        <el-button type="primary">Primary</el-button>
        <el-button type="success">Success</el-button>
        <el-button type="info">Info</el-button>
        <el-button type="warning">Warning</el-button>
        <el-button type="danger">Danger</el-button>
        <el-button type="primary" plain>Plain</el-button>
        <el-button type="primary" round>Round</el-button>
        <el-button type="primary" circle><el-icon><Search /></el-icon></el-button>
        <el-button type="primary" disabled>Disabled</el-button>
      </div>
    </el-card>

    <el-card shadow="hover" header="Sizes" style="margin-bottom: 16px">
      <div style="display: flex; gap: 12px; align-items: center">
        <el-button size="large">Large</el-button>
        <el-button>Default</el-button>
        <el-button size="small">Small</el-button>
        <el-button size="large" type="primary"><el-icon><Plus /></el-icon> <span>Add</span></el-button>
      </div>
    </el-card>

    <el-card shadow="hover" header="With Icons" style="margin-bottom: 16px">
      <div style="display: flex; gap: 12px; align-items: center">
        <el-button type="primary"><el-icon><Plus /></el-icon> <span>New</span></el-button>
        <el-button type="success"><el-icon><Check /></el-icon> <span>Save</span></el-button>
        <el-button type="warning"><el-icon><Star /></el-icon> <span>Star</span></el-button>
        <el-button type="danger"><el-icon><Delete /></el-icon> <span>Delete</span></el-button>
        <el-button type="info"><el-icon><Download /></el-icon> <span>Download</span></el-button>
        <el-button><el-icon><Refresh /></el-icon> <span>Refresh</span></el-button>
      </div>
    </el-card>

    <el-card shadow="hover" header="Text & Link Buttons" style="margin-bottom: 16px">
      <div style="display: flex; gap: 12px; align-items: center">
        <el-button text>Text Button</el-button>
        <el-button text type="primary">Text Primary</el-button>
        <el-button link>Link Button</el-button>
        <el-button link type="primary">Link Primary</el-button>
        <el-button link type="success">Link Success</el-button>
      </div>
    </el-card>

    <el-card shadow="hover" header="Loading">
      <div style="display: flex; gap: 12px; align-items: center">
        <el-button type="primary" :loading="true">Loading...</el-button>
        <el-button type="primary" loading-icon="Loading">Custom Loading</el-button>
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
