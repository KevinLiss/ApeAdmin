<template>
  <div>
    <PageHeader title="Creative Card" :breadcrumb="['APEUI库', 'Components', 'Creative Card']" />

    <el-row :gutter="30">
      <!-- 1. Border Left Primary -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="border-left-primary">
          <template #header>
            <div class="card-header">
              <span class="card-title">Border Left Primary</span>
            </div>
          </template>
          <div class="card-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>

      <!-- 2. Border Right Secondary -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="border-right-secondary">
          <template #header>
            <div class="card-header">
              <span class="card-title">Border Right Secondary</span>
            </div>
          </template>
          <div class="card-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>

      <!-- 3. Border Top Success -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="border-top-success">
          <template #header>
            <div class="card-header">
              <span class="card-title">Border Top Success</span>
            </div>
          </template>
          <div class="card-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>

      <!-- 4. Border Bottom Info -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="border-bottom-info">
          <template #header>
            <div class="card-header">
              <span class="card-title">Border Bottom Info</span>
            </div>
          </template>
          <div class="card-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>

      <!-- 5. Border Left Warning -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="border-left-warning">
          <template #header>
            <div class="card-header">
              <span class="card-title">Border Left Warning</span>
            </div>
          </template>
          <div class="card-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>

      <!-- 6. Border Left Danger -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="border-left-danger">
          <template #header>
            <div class="card-header">
              <span class="card-title">Border Left Danger</span>
            </div>
          </template>
          <div class="card-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>

      <!-- 7. Border Left Secondary -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="border-left-secondary">
          <template #header>
            <div class="card-header">
              <span class="card-title">Border Left Secondary</span>
            </div>
          </template>
          <div class="card-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>

      <!-- 8. Border Left Primary -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="border-left-primary">
          <template #header>
            <div class="card-header">
              <span class="card-title">Border Left Primary</span>
            </div>
          </template>
          <div class="card-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>

      <!-- 9. Border Left 2px -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="border-left-2px">
          <template #header>
            <div class="card-header">
              <span class="card-title">Border Left 2px</span>
            </div>
          </template>
          <div class="card-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>

      <!-- 10. Border Left 3px -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="border-left-3px">
          <template #header>
            <div class="card-header">
              <span class="card-title">Border Left 3px</span>
            </div>
          </template>
          <div class="card-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>

      <!-- 11. Absolute Header Primary -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="absolute-header-card" :body-style="{ padding: '0' }">
          <div class="absolute-header absolute-header-primary">
            <span class="absolute-header-title">Absolute Header Primary</span>
          </div>
          <div class="card-body absolute-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>

      <!-- 12. Absolute Header Secondary -->
      <el-col :span="12" class="card-col">
        <el-card shadow="hover" class="absolute-header-card" :body-style="{ padding: '0' }">
          <div class="absolute-header absolute-header-secondary">
            <span class="absolute-header-title">Absolute Header Secondary</span>
          </div>
          <div class="card-body absolute-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'
</script>

<style scoped>
.card-col {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-title {
  font-weight: 600;
  font-size: 15px;
  color: #534686;
}

.card-body {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
}

.card-body p {
  margin: 0 0 10px 0;
}

.card-body p:last-child {
  margin-bottom: 0;
}

/* Border装饰变体 */
.border-left-primary {
  border-left: 4px solid #534686;
}

.border-right-secondary {
  border-right: 4px solid #FFA47A;
}

.border-top-success {
  border-top: 4px solid #67C100;
}

.border-bottom-info {
  border-bottom: 4px solid #3EBCB9;
}

.border-left-warning {
  border-left: 4px solid #E56809;
}

.border-left-danger {
  border-left: 4px solid #DC0808;
}

.border-left-secondary {
  border-left: 4px solid #FFA47A;
}

.border-left-2px {
  border-left: 2px solid #534686;
}

.border-left-3px {
  border-left: 3px solid #534686;
}

/* Absolute Header 变体 */
.absolute-header-card {
  overflow: hidden;
}

.absolute-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
}

.absolute-header-primary {
  background: #534686;
}

.absolute-header-secondary {
  background: #FFA47A;
}

.absolute-header-title {
  font-weight: 600;
  font-size: 15px;
  color: #fff;
}

.absolute-body {
  padding: 20px;
}
</style>
