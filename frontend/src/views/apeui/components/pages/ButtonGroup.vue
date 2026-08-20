<template>
  <div>
    <PageHeader title="Button Group" :breadcrumb="['APEUI库', 'Components', 'Button Group']" />

    <el-card shadow="hover" header="Basic Groups" style="margin-bottom: 16px">
      <div style="display: flex; flex-direction: column; gap: 16px">
        <el-button-group>
          <el-button>Left</el-button>
          <el-button>Center</el-button>
          <el-button>Right</el-button>
        </el-button-group>
        <el-button-group>
          <el-button type="primary"><el-icon><ArrowLeft /></el-icon> Prev</el-button>
          <el-button type="primary">Next <el-icon><ArrowRight /></el-icon></el-button>
        </el-button-group>
      </div>
    </el-card>

    <el-card shadow="hover" header="Color Variants" style="margin-bottom: 16px">
      <el-button-group>
        <el-button type="success">Success</el-button>
        <el-button type="warning">Warning</el-button>
        <el-button type="danger">Danger</el-button>
        <el-button type="info">Info</el-button>
      </el-button-group>
    </el-card>

    <el-card shadow="hover" header="Icon Groups" style="margin-bottom: 16px">
      <el-button-group>
        <el-button type="primary"><el-icon><EditPen /></el-icon></el-button>
        <el-button type="primary"><el-icon><Share /></el-icon></el-button>
        <el-button type="primary"><el-icon><Delete /></el-icon></el-button>
      </el-button-group>
    </el-card>

    <el-card shadow="hover" header="Sizes">
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
