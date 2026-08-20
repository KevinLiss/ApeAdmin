<template>
  <div>
    <PageHeader title="Tag & Pills" :breadcrumb="['APEUI库', 'Components', 'Tag & Pills']" />

    <el-card shadow="hover" header="Tag Types" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center">
        <el-tag>Default</el-tag>
        <el-tag type="primary">Primary</el-tag>
        <el-tag type="success">Success</el-tag>
        <el-tag type="info">Info</el-tag>
        <el-tag type="warning">Warning</el-tag>
        <el-tag type="danger">Danger</el-tag>
      </div>
    </el-card>

    <el-card shadow="hover" header="Closable Tags" style="margin-bottom: 16px">
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
        <el-button v-else size="small" type="primary" plain @click="showTagInput">+ New Tag</el-button>
      </div>
    </el-card>

    <el-card shadow="hover" header="With Icons" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center">
        <el-tag type="primary" :icon="Check">Check</el-tag>
        <el-tag type="success" :icon="CircleCheck">Done</el-tag>
        <el-tag type="warning" :icon="Warning">Warning</el-tag>
        <el-tag type="danger" :icon="Delete">Remove</el-tag>
        <el-tag type="info" :icon="InfoFilled">Info</el-tag>
        <el-tag type="primary" disable-transitions>
          <el-icon><Star /></el-icon>
          <span>Starred</span>
        </el-tag>
      </div>
    </el-card>

    <el-card shadow="hover" header="Sizes & Round" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center">
        <el-tag size="large">Large</el-tag>
        <el-tag>Default</el-tag>
        <el-tag size="small">Small</el-tag>
        <el-tag type="primary" round>Round Primary</el-tag>
        <el-tag type="success" round>Round Success</el-tag>
        <el-tag type="warning" round>Round Warning</el-tag>
        <el-tag type="danger" round>Round Danger</el-tag>
        <el-tag effect="dark" round>Dark Round</el-tag>
        <el-tag effect="plain" round>Plain Round</el-tag>
      </div>
    </el-card>

    <el-card shadow="hover" header="Badges" style="margin-bottom: 16px">
      <div style="display: flex; flex-wrap: wrap; gap: 32px; align-items: center">
        <el-badge :value="12" :max="99">
          <el-button size="small">Messages</el-button>
        </el-badge>
        <el-badge :value="200" :max="99">
          <el-button size="small">Comments</el-button>
        </el-badge>
        <el-badge :value="new Date().getDay()" class="item" type="primary">
          <el-button size="small">Today</el-button>
        </el-badge>
        <el-badge is-dot type="success">
          <el-button size="small">Online</el-button>
        </el-badge>
        <el-badge is-dot type="warning">
          <el-button size="small">Pending</el-button>
        </el-badge>
        <el-badge value="hot" type="danger">
          <el-button size="small">Trending</el-button>
        </el-badge>
        <el-badge :value="8" type="info">
          <el-button size="small">Info</el-button>
        </el-badge>
      </div>
    </el-card>

    <el-card shadow="hover" header="Badge on Icons">
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
  { name: 'Primary', type: 'primary' },
  { name: 'Success', type: 'success' },
  { name: 'Info', type: 'info' },
  { name: 'Warning', type: 'warning' },
  { name: 'Danger', type: 'danger' },
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