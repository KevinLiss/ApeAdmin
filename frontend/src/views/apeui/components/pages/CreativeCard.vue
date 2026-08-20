<template>
  <div>
    <PageHeader title="Creative Card" :breadcrumb="['APEUI库', 'Components', 'Creative Card']" />

    <el-row :gutter="16">
      <el-col :span="8" style="margin-bottom: 16px">
        <div class="gradient-card">
          <el-icon :size="32" color="#fff"><MagicStick /></el-icon>
          <h3 style="margin: 12px 0 4px; color: #fff">渐变卡片</h3>
          <p style="margin: 0; color: rgba(255,255,255,0.85); font-size: 13px">linear-gradient 紫色背景</p>
        </div>
      </el-col>
      <el-col :span="8" style="margin-bottom: 16px">
        <div class="gradient-card gradient-2">
          <el-icon :size="32" color="#fff"><DataAnalysis /></el-icon>
          <h3 style="margin: 12px 0 4px; color: #fff">数据洞察</h3>
          <p style="margin: 0; color: rgba(255,255,255,0.85); font-size: 13px">深紫渐变风格</p>
        </div>
      </el-col>
      <el-col :span="8" style="margin-bottom: 16px">
        <div class="gradient-card gradient-3">
          <el-icon :size="32" color="#fff"><TrophyBase /></el-icon>
          <h3 style="margin: 12px 0 4px; color: #fff">成就解锁</h3>
          <p style="margin: 0; color: rgba(255,255,255,0.85); font-size: 13px">斜向渐变效果</p>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="8" style="margin-bottom: 16px" v-for="card in imageCards" :key="card.title">
        <el-card shadow="hover" :body-style="{ padding: '0' }" class="image-card">
          <img :src="card.img" class="card-image" />
          <div style="padding: 14px 16px">
            <h4 style="margin: 0 0 6px; font-weight: 600; color: #534686">{{ card.title }}</h4>
            <p style="margin: 0; color: #909399; font-size: 13px">{{ card.desc }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="6" v-for="item in hoverCards" :key="item.title" style="margin-bottom: 16px">
        <el-card shadow="hover" class="hover-card">
          <div class="hover-card-icon" :style="{ background: item.bg }">
            <el-icon :size="24" color="#fff"><component :is="item.icon" /></el-icon>
          </div>
          <h4 style="margin: 12px 0 4px; font-weight: 600">{{ item.title }}</h4>
          <p style="margin: 0; color: #909399; font-size: 13px">{{ item.desc }}</p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" class="combo-card" :body-style="{ padding: '0' }">
          <div class="combo-top">
            <el-icon :size="40" color="#fff"><Cpu /></el-icon>
            <h3 style="margin: 0; color: #fff; font-size: 18px">AI 引擎</h3>
          </div>
          <div style="padding: 20px">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="模型">DeepSeek-V3</el-descriptions-item>
              <el-descriptions-item label="上下文">128K tokens</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag type="success" size="small">运行中</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" class="combo-card" :body-style="{ padding: '0' }">
          <div class="combo-top combo-top-2">
            <el-icon :size="40" color="#fff"><Monitor /></el-icon>
            <h3 style="margin: 0; color: #fff; font-size: 18px">部署信息</h3>
          </div>
          <div style="padding: 20px">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="服务器">172.16.127.101</el-descriptions-item>
              <el-descriptions-item label="框架">FastAPI + Vue3</el-descriptions-item>
              <el-descriptions-item label="环境">
                <el-tag type="warning" size="small">生产环境</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { MagicStick, DataAnalysis, TrophyBase, Cpu, Monitor, Box, Bell, Setting, Star } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const imageCards = [
  { title: '自然风光', desc: '风景摄影卡片示例', img: 'https://picsum.photos/seed/card1/400/200' },
  { title: '城市夜景', desc: '都市夜景卡片示例', img: 'https://picsum.photos/seed/card2/400/200' },
  { title: '抽象艺术', desc: '抽象图案卡片示例', img: 'https://picsum.photos/seed/card3/400/200' },
]

const hoverCards = [
  { title: '存储管理', desc: '云端存储服务', icon: Box, bg: '#534686' },
  { title: '消息通知', desc: '实时推送通知', icon: Bell, bg: '#7b6fa8' },
  { title: '系统设置', desc: '全局配置管理', icon: Setting, bg: '#3EBCB9' },
  { title: '收藏夹', desc: '个人收藏内容', icon: Star, bg: '#E56809' },
]
</script>

<style scoped>
.gradient-card {
  background: linear-gradient(135deg, #534686 0%, #7b6fa8 100%);
  border-radius: 12px;
  padding: 28px 24px;
  text-align: center;
  transition: transform 0.3s;
}
.gradient-card:hover {
  transform: translateY(-4px);
}
.gradient-2 {
  background: linear-gradient(135deg, #3d3270 0%, #534686 100%);
}
.gradient-3 {
  background: linear-gradient(120deg, #534686 0%, #9b8fc4 100%);
}
.image-card {
  overflow: hidden;
  transition: transform 0.3s;
}
.image-card:hover {
  transform: translateY(-4px);
}
.card-image {
  width: 100%;
  height: 160px;
  object-fit: cover;
  display: block;
}
.hover-card {
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
}
.hover-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(83, 70, 134, 0.18);
}
.hover-card-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}
.combo-card {
  overflow: hidden;
}
.combo-top {
  background: linear-gradient(135deg, #534686 0%, #7b6fa8 100%);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.combo-top-2 {
  background: linear-gradient(135deg, #3d3270 0%, #534686 100%);
}
</style>
