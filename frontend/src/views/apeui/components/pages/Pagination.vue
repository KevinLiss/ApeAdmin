<template>
  <div>
    <PageHeader title="分页" :breadcrumb="['APEUI库', '组件示例', '分页']" />

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="基础分页">
          <div class="pager-block">
            <span class="pager-label">页数较少</span>
            <el-pagination layout="prev, pager, next" :total="50" v-model:current-page="p1" />
          </div>
          <div class="pager-block">
            <span class="pager-label">页数较多</span>
            <el-pagination layout="prev, pager, next" :total="500" v-model:current-page="p2" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="带背景">
          <div class="pager-block">
            <span class="pager-label">背景样式</span>
            <el-pagination background layout="prev, pager, next" :total="100" v-model:current-page="p3" />
          </div>
          <div class="pager-block">
            <span class="pager-label">紫色背景</span>
            <el-pagination background layout="prev, pager, next, jumper" :total="200" v-model:current-page="p4" class="purple-pager" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="小尺寸 (small)">
          <div class="pager-block">
            <el-pagination small background layout="prev, pager, next" :total="50" v-model:current-page="p5" />
          </div>
          <div class="pager-block">
            <el-pagination small layout="prev, pager, next" :total="50" v-model:current-page="p6" />
          </div>
          <div class="pager-block">
            <el-pagination small background layout="prev, pager, next, jumper" :total="100" v-model:current-page="p7" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="总数 + 跳转">
          <div class="pager-block">
            <span class="pager-label">带总数</span>
            <el-pagination background layout="total, prev, pager, next" :total="1024" v-model:current-page="p8" />
          </div>
          <div class="pager-block">
            <span class="pager-label">带跳转</span>
            <el-pagination background layout="prev, pager, next, jumper" :total="2048" v-model:current-page="p9" />
          </div>
          <div class="pager-block">
            <span class="pager-label">全部功能</span>
            <el-pagination background layout="total, sizes, prev, pager, next, jumper" :total="4096" :page-sizes="[10, 20, 50, 100]" v-model:current-page="p10" v-model:page-size="ps1" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" header="不同 Layout 组合">
      <div class="pager-block" v-for="item in layoutDemos" :key="item.layout">
        <span class="pager-label">{{ item.label }}</span>
        <el-pagination
          background
          :layout="item.layout"
          :total="1000"
          :page-sizes="[10, 20, 30, 50]"
          v-model:current-page="p11"
          v-model:page-size="ps2"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '../PageHeader.vue'

const p1 = ref(1), p2 = ref(1), p3 = ref(1), p4 = ref(1)
const p5 = ref(1), p6 = ref(1), p7 = ref(1), p8 = ref(1)
const p9 = ref(1), p10 = ref(1), p11 = ref(1)
const ps1 = ref(20), ps2 = ref(10)

const layoutDemos = [
  { label: 'prev, pager, next', layout: 'prev, pager, next' },
  { label: 'prev, pager, next, jumper', layout: 'prev, pager, next, jumper' },
  { label: 'total, prev, pager, next', layout: 'total, prev, pager, next' },
  { label: 'total, sizes, prev, pager, next', layout: 'total, sizes, prev, pager, next' },
  { label: 'total, sizes, prev, pager, next, jumper', layout: 'total, sizes, prev, pager, next, jumper' },
]
</script>

<style scoped>
.pager-block {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f5;
}
.pager-block:last-child {
  border-bottom: none;
}
.pager-label {
  width: 200px;
  color: #5a6273;
  font-size: 13px;
  white-space: nowrap;
}
</style>
