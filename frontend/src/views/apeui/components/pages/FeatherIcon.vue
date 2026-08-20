<template>
  <div>
    <PageHeader title="Feather Icon" :breadcrumb="['APEUI库', 'Components', 'Feather Icon']" />

    <el-card shadow="hover" class="feather-card">
      <template #header>
        <span style="color: #7c3aed; font-weight: 600">Element Plus Icons — Purple Theme</span>
      </template>
      <div class="icon-grid">
        <div v-for="item in icons" :key="item.name" class="icon-item">
          <el-icon :size="28" color="#7c3aed"><component :is="item.component" /></el-icon>
          <span class="icon-name">{{ item.name }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import {
  Calendar, Clock, Timer, Stopwatch, Key, Postcard, MessageBox, ChatDotSquare,
  ChatLineSquare, PhoneFilled, Headset, Mic, Microphone, Notification,
  Paperclip, PriceTag, Service, Ticket, Tickets, Wallet, WalletFilled,
  ShoppingCart, ShoppingBag, ShoppingCartFull, ShoppingTrolley, Goods, Present,
  Briefcase, Suitcase, SoldOut, Handbag, Mug, Sugar, Magnet, Brush,
  Cpu, Coordinate, Discount, Sunrise, WindPower, GoldMedal, Trophy, CopyDocument,
  BellFilled, Mouse,
} from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const icons: { name: string; component: Component }[] = [
  { name: 'Calendar', component: Calendar },
  { name: 'Clock', component: Clock },
  { name: 'Timer', component: Timer },
  { name: 'Stopwatch', component: Stopwatch },
  { name: 'Key', component: Key },
  { name: 'Postcard', component: Postcard },
  { name: 'MessageBox', component: MessageBox },
  { name: 'ChatDotSquare', component: ChatDotSquare },
  { name: 'ChatLineSquare', component: ChatLineSquare },
  { name: 'PhoneFilled', component: PhoneFilled },
  { name: 'Headset', component: Headset },
  { name: 'Mic', component: Mic },
  { name: 'Microphone', component: Microphone },
  { name: 'Notification', component: Notification },
  { name: 'Paperclip', component: Paperclip },
  { name: 'PriceTag', component: PriceTag },
  { name: 'Service', component: Service },
  { name: 'Ticket', component: Ticket },
  { name: 'Tickets', component: Tickets },
  { name: 'Wallet', component: Wallet },
  { name: 'WalletFilled', component: WalletFilled },
  { name: 'ShoppingCart', component: ShoppingCart },
  { name: 'ShoppingBag', component: ShoppingBag },
  { name: 'ShoppingCartFull', component: ShoppingCartFull },
  { name: 'ShoppingTrolley', component: ShoppingTrolley },
  { name: 'Goods', component: Goods },
  { name: 'Present', component: Present },
  { name: 'Briefcase', component: Briefcase },
  { name: 'Suitcase', component: Suitcase },
  { name: 'SoldOut', component: SoldOut },
  { name: 'Handbag', component: Handbag },
  { name: 'Mug', component: Mug },
  { name: 'Sugar', component: Sugar },
  { name: 'Magnet', component: Magnet },
  { name: 'Brush', component: Brush },
  { name: 'Cpu', component: Cpu },
  { name: 'Coordinate', component: Coordinate },
  { name: 'Discount', component: Discount },
  { name: 'Sunrise', component: Sunrise },
  { name: 'WindPower', component: WindPower },
  { name: 'GoldMedal', component: GoldMedal },
  { name: 'Trophy', component: Trophy },
  { name: 'CopyDocument', component: CopyDocument },
  { name: 'BellFilled', component: BellFilled },
  { name: 'Mouse', component: Mouse },
]
</script>

<style scoped>
.feather-card {
  --el-card-padding: 20px;
}
.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}
.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  border-radius: 8px;
  background: #faf5ff;
  border: 1px solid #ede9fe;
  transition: all 0.2s;
}
.icon-item:hover {
  background: #f3e8ff;
  border-color: #c4b5fd;
  transform: translateY(-2px);
}
.icon-name {
  font-size: 12px;
  color: #6b21a8;
  text-align: center;
  word-break: break-all;
}
</style>
