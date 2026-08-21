<template>
  <div>
    <PageHeader title="状态颜色" :breadcrumb="['APEUI库', '组件示例', '状态颜色']" />

    <el-card shadow="hover">
      <template #header>
        <span class="card-title">默认颜色</span>
      </template>

      <el-row :gutter="30">
        <el-col :lg="6" :sm="12" :xs="12" v-for="item in colorList" :key="item.name" class="color-col">
          <div class="color-swatch" :style="{ background: item.color }">
            <span v-if="item.light" class="swatch-label" :style="{ color: item.light }">{{ item.name }}</span>
            <span v-else class="swatch-label swatch-label--dark">{{ item.name }}</span>
          </div>
          <div class="color-info">
            <h4 class="color-name">{{ item.name }}</h4>
            <p class="color-hex">{{ item.hex }}</p>
            <p class="color-desc">{{ item.desc }}</p>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'

const colorList = [
  { name: 'Primary',   hex: '#5A67F5', desc: '主题主色 · 用于按钮、链接、强调',           light: false },
  { name: 'Secondary', hex: '#FFA47A', desc: '次要色 · 辅助强调与装饰元素',               light: false },
  { name: 'Success',   hex: '#67C100', desc: '成功状态 · 操作成功提示',                  light: false },
  { name: 'Info',      hex: '#3EBCB9', desc: '信息状态 · 一般信息提示',                  light: false },
  { name: 'Warning',   hex: '#E56809', desc: '警告状态 · 需要注意的操作',                light: false },
  { name: 'Danger',    hex: '#DC0808', desc: '危险状态 · 错误或不可逆操作',              light: false },
  { name: 'Light',     hex: '#F4F4F4', desc: '浅色 · 背景与卡片底色',                    light: '#5a6273' },
  { name: 'Dark',      hex: '#2C323F', desc: '深色 · 文字、侧栏、深色区域',              light: false },
]
</script>

<style scoped>
.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #5A67F5;
}

.color-col {
  margin-bottom: 30px;
}

.color-swatch {
  height: 100px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
  cursor: default;
}

.color-swatch:hover {
  transform: translateY(-3px);
}

.swatch-label {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

.swatch-label--dark {
  color: #2C323F;
}

.color-info {
  padding-top: 14px;
  text-align: center;
}

.color-name {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 600;
  color: #2C323F;
}

.color-hex {
  margin: 0 0 4px;
  font-size: 13px;
  font-family: 'Courier New', Consolas, monospace;
  color: #5A67F5;
  font-weight: 600;
}

.color-desc {
  margin: 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}
</style>
