<template>
  <div class="koho-frame-page">
    <iframe
      :src="`/koho/${page}.html`"
      class="koho-frame"
      frameborder="0"
      allowfullscreen
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const page = computed(() => (route.params.page as string) || 'index')
</script>

<style scoped>
.koho-frame-page {
  position: fixed;
  top: 64px;
  left: 258px;
  right: 0;
  bottom: 0;
  background: #fff;
  z-index: 5;
}
.koho-frame {
  width: 100%;
  height: 100%;
  border: none;
}
</style>