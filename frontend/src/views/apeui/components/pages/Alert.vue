<template>
  <div>
    <PageHeader title="Alert" :breadcrumb="['APEUI库', 'Components', 'Alert']" />

    <el-card shadow="hover" header="Alert Types" style="margin-bottom: 16px">
      <div style="display: flex; flex-direction: column; gap: 14px">
        <el-alert title="Success alert text" type="success" />
        <el-alert title="Info alert text" type="info" />
        <el-alert title="Warning alert text" type="warning" />
        <el-alert title="Error alert text" type="error" />
      </div>
    </el-card>

    <el-card shadow="hover" header="With / Without Icons" style="margin-bottom: 16px">
      <div style="display: flex; flex-direction: column; gap: 14px">
        <el-alert title="With icon" type="info" show-icon />
        <el-alert title="Success with icon" type="success" show-icon />
        <el-alert title="Warning with icon" type="warning" show-icon />
        <el-alert title="Error with icon" type="error" show-icon />
        <el-alert title="Info without icon (show-icon not set)" type="info" />
        <el-alert title="Custom icon" type="warning" :icon="Star" show-icon />
      </div>
    </el-card>

    <el-card shadow="hover" header="Closable" style="margin-bottom: 16px">
      <div style="display: flex; flex-direction: column; gap: 14px">
        <el-alert title="Closable success alert" type="success" closable />
        <el-alert title="Closable info alert" type="info" closable />
        <el-alert title="Closable warning alert with custom close text" type="warning" closable close-text="Got it" />
        <el-alert title="Closable error alert with icon" type="error" show-icon closable />
      </div>
    </el-card>

    <el-card shadow="hover" header="Center Alignment" style="margin-bottom: 16px">
      <div style="display: flex; flex-direction: column; gap: 14px">
        <el-alert title="Center aligned success" type="success" center show-icon />
        <el-alert title="Center aligned info" type="info" center show-icon />
        <el-alert title="Center aligned warning" type="warning" center show-icon />
      </div>
    </el-card>

    <el-card shadow="hover" header="With Description">
      <div style="display: flex; flex-direction: column; gap: 14px">
        <el-alert title="Success with description" type="success" description="A brief description about this success alert." show-icon />
        <el-alert title="Warning with description" type="warning" description="A brief description about this warning alert." show-icon />
        <el-alert title="Error with description" type="error" description="A brief description about this error alert." show-icon />
        <el-alert title="Rich content" type="warning" show-icon>
          <template #default>
            <div>
              <p>This alert supports custom rich content inside:</p>
              <ul style="padding-left: 18px; margin: 8px 0">
                <li>Bullet point one</li>
                <li>Bullet point two</li>
                <li>Bullet point three</li>
              </ul>
              <el-button size="small" type="primary" plain>Action Button</el-button>
            </div>
          </template>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Star } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'
</script>