<template>
  <div>
    <PageHeader title="Accordion / Collapse" :breadcrumb="['APEUI库', 'Components', 'Accordion']" />

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Basic Collapse" style="margin-bottom: 16px">
          <el-collapse v-model="activeNames">
            <el-collapse-item title="Consistency" name="1">
              <div>Consistent with real life: in line with the process and logic of real life, and comply with the language and habits that the users are used to.</div>
            </el-collapse-item>
            <el-collapse-item title="Feedback" name="2">
              <div>Operation feedback: enable the users to clearly perceive their operations by style updates and interactive effects.</div>
            </el-collapse-item>
            <el-collapse-item title="Efficiency" name="3">
              <div>Simplify the process: keep the operation simple and intuitive.</div>
            </el-collapse-item>
          </el-collapse>
        </el-card>

        <el-card shadow="hover" header="Custom Title">
          <el-collapse accordion>
            <el-collapse-item name="1">
              <template #title>
                <div class="custom-title">
                  <el-icon color="#534686" :size="18"><InfoFilled /></el-icon>
                  <span style="margin-left: 8px">General Settings</span>
                  <el-tag size="small" type="primary" style="margin-left: 8px">New</el-tag>
                </div>
              </template>
              <div>
                <p>Custom title with icon, text and tag.</p>
                <p style="color: #5a6273">You can put anything in the <code>#title</code> slot.</p>
              </div>
            </el-collapse-item>
            <el-collapse-item name="2">
              <template #title>
                <div class="custom-title">
                  <el-icon color="#3ebcb9" :size="18"><Connection /></el-icon>
                  <span style="margin-left: 8px">Integration</span>
                </div>
              </template>
              <div>Integration content goes here.</div>
            </el-collapse-item>
            <el-collapse-item name="3">
              <template #title>
                <div class="custom-title">
                  <el-icon color="#dc0808" :size="18"><Warning /></el-icon>
                  <span style="margin-left: 8px">Advanced (Danger Zone)</span>
                </div>
              </template>
              <div>Advanced settings content.</div>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Accordion Mode" style="margin-bottom: 16px">
          <el-collapse accordion v-model="accordionActive">
            <el-collapse-item title="Panel One (always open)" name="1">
              <div>With accordion mode only one panel stays open at a time.</div>
            </el-collapse-item>
            <el-collapse-item title="Panel Two" name="2">
              <div>Second panel content.</div>
            </el-collapse-item>
            <el-collapse-item title="Panel Three" name="3">
              <div>Third panel content.</div>
            </el-collapse-item>
          </el-collapse>
        </el-card>

        <el-card shadow="hover" header="Disabled & Mix">
          <el-collapse v-model="activeNames2">
            <el-collapse-item title="Enabled panel" name="a">
              <div>This panel is active.</div>
            </el-collapse-item>
            <el-collapse-item title="Disabled panel" name="b" disabled>
              <div>This panel cannot be toggled.</div>
            </el-collapse-item>
            <el-collapse-item title="Another enabled" name="c">
              <div>Second enabled panel.</div>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { InfoFilled, Connection, Warning } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const activeNames = ref(['1'])
const accordionActive = ref('1')
const activeNames2 = ref(['a'])
</script>

<style scoped>
.custom-title {
  display: flex;
  align-items: center;
  font-weight: 600;
}
</style>