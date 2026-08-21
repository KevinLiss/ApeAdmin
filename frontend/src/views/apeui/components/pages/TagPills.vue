<template>
  <div>
    <PageHeader title="标签与胶囊" :breadcrumb="['APEUI库', '组件示例', '标签与胶囊']" />

    <el-card shadow="hover" header="标签类型" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center">
        <el-tag>默认</el-tag>
        <el-tag type="primary">主要</el-tag>
        <el-tag type="success">成功</el-tag>
        <el-tag type="info">信息</el-tag>
        <el-tag type="warning">警告</el-tag>
        <el-tag type="danger">危险</el-tag>
      </div>
    </el-card>

    <el-card shadow="hover" header="可关闭标签" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center">
        <el-tag v-for="tag in closableTags" :key="tag.name" :type="tag.type" closable @close="handleClose(tag)">
          {{ tag.name }}
        </el-tag>
        <el-input
          v-if="showInput"
          ref="tagInputRef"
          v-model="tagInput"
          size="small"
          style="width: 100px"
          @keyup.enter="confirmTag"
          @blur="confirmTag"
        />
        <el-button v-else size="small" type="primary" plain @click="showTagInput">+ 新建标签</el-button>
      </div>
    </el-card>

    <el-card shadow="hover" header="带图标" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center">
        <el-tag type="primary" :icon="Check">勾选</el-tag>
        <el-tag type="success" :icon="CircleCheck">完成</el-tag>
        <el-tag type="warning" :icon="Warning">警告</el-tag>
        <el-tag type="danger" :icon="Delete">移除</el-tag>
        <el-tag type="info" :icon="InfoFilled">信息</el-tag>
        <el-tag type="primary" disable-transitions>
          <el-icon><Star /></el-icon>
          <span>已收藏</span>
        </el-tag>
      </div>
    </el-card>

    <el-card shadow="hover" header="尺寸与圆角" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center">
        <el-tag size="large">大</el-tag>
        <el-tag>默认</el-tag>
        <el-tag size="small">小</el-tag>
        <el-tag type="primary" round>圆角主要</el-tag>
        <el-tag type="success" round>圆角成功</el-tag>
        <el-tag type="warning" round>圆角警告</el-tag>
        <el-tag type="danger" round>圆角危险</el-tag>
        <el-tag effect="dark" round>深色圆角</el-tag>
        <el-tag effect="plain" round>朴素圆角</el-tag>
      </div>
    </el-card>

    <el-card shadow="hover" header="徽标" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 32px; align-items: center">
        <el-badge :value="12" :max="99">
          <el-button size="small">消息</el-button>
        </el-badge>
        <el-badge :value="200" :max="99">
          <el-button size="small">评论</el-button>
        </el-badge>
        <el-badge :value="new Date().getDay()" class="item" type="primary">
          <el-button size="small">今天</el-button>
        </el-badge>
        <el-badge is-dot type="success">
          <el-button size="small">在线</el-button>
        </el-badge>
        <el-badge is-dot type="warning">
          <el-button size="small">待处理</el-button>
        </el-badge>
        <el-badge value="hot" type="danger">
          <el-button size="small">热门</el-button>
        </el-badge>
        <el-badge :value="8" type="info">
          <el-button size="small">信息</el-button>
        </el-badge>
      </div>
    </el-card>

    <el-card shadow="hover" header="图标徽标">
      <div style="display: flex; gap: 32px; align-items: center">
        <el-badge :value="12" type="primary">
          <el-icon :size="28"><Bell /></el-icon>
        </el-badge>
        <el-badge :value="3" type="danger">
          <el-icon :size="28"><ChatDotRound /></el-icon>
        </el-badge>
        <el-badge is-dot type="success">
          <el-icon :size="28"><Message /></el-icon>
        </el-badge>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { Check, CircleCheck, Delete, Warning, InfoFilled, Star, Bell, ChatDotRound, Message } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const closableTags = ref([
  { name: '主要', type: 'primary' },
  { name: '成功', type: 'success' },
  { name: '信息', type: 'info' },
  { name: '警告', type: 'warning' },
  { name: '危险', type: 'danger' },
])

const tagInput = ref('')
const showInput = ref(false)
const tagInputRef = ref()

const showTagInput = () => {
  showInput.value = true
  nextTick(() => tagInputRef.value?.focus())
}

const confirmTag = () => {
  if (tagInput.value) {
    closableTags.value.push({ name: tagInput.value, type: 'primary' })
  }
  showInput.value = false
  tagInput.value = ''
}

const handleClose = (tag: { name: string; type: string }) => {
  closableTags.value = closableTags.value.filter((t) => t.name !== tag.name)
}
</script>