<template>
  <div class="apeui-page-header">
    <div>
      <h3>{{ title }}</h3>
      <div class="breadcrumb" v-if="breadcrumb">
        <template v-for="(item, i) in breadcrumb" :key="i">
          <span v-if="i > 0" class="sep">/</span>
          <span>{{ item }}</span>
        </template>
      </div>
    </div>
    <slot name="actions" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  breadcrumb?: string[]
}>()
</script>
