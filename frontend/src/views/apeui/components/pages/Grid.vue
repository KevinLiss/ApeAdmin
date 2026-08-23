<template>
  <div class="grid-page">
    <PageHeader title="栅格布局" :breadcrumb="['APEUI库', '组件示例', '栅格布局']" />

    <!-- 1. 栅格选项 -->
    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <span class="card-title">栅格选项</span>
      </template>
      <p class="card-desc">ApeAdmin 栅格系统支持六个响应式断点，每个断点对应不同的最小宽度和类前缀。下方表格展示了完整的断点参数。</p>
      <el-table :data="gridOptions" border style="width: 100%" :header-cell-style="{ background: '#f5f4fa', color: '#5A67F5', fontWeight: 600 }">
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="minWidth" label="最小宽度" width="140" />
        <el-table-column prop="prefix" label="类前缀" width="140" />
        <el-table-column prop="columns" label="栅格数" width="100" align="center" />
        <el-table-column prop="gutter" label="Gutter 宽度" align="center" />
      </el-table>
    </el-card>

    <!-- 2. Grid Column -->
    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <span class="card-title">Grid Column</span>
      </template>
      <p class="card-desc">Element Plus 的 24 栅格系统，以下展示不同的列等分组合，每行总列数之和为 24。</p>

      <div class="grid-section">
        <p class="grid-label">12 列 × :span="2"（每列占 2/24）</p>
        <el-row :gutter="10" class="grid-row">
          <el-col :span="2" v-for="i in 12" :key="'a' + i">
            <div class="grid-cell">col-2</div>
          </el-col>
        </el-row>
      </div>

      <div class="grid-section">
        <p class="grid-label">6 列 × :span="4"（每列占 4/24）</p>
        <el-row :gutter="10" class="grid-row">
          <el-col :span="4" v-for="i in 6" :key="'b' + i">
            <div class="grid-cell">col-4</div>
          </el-col>
        </el-row>
      </div>

      <div class="grid-section">
        <p class="grid-label">4 列 × :span="6"（每列占 6/24）</p>
        <el-row :gutter="10" class="grid-row">
          <el-col :span="6" v-for="i in 4" :key="'c' + i">
            <div class="grid-cell">col-6</div>
          </el-col>
        </el-row>
      </div>

      <div class="grid-section">
        <p class="grid-label">3 列 × :span="8"（每列占 8/24）</p>
        <el-row :gutter="10" class="grid-row">
          <el-col :span="8" v-for="i in 3" :key="'d' + i">
            <div class="grid-cell">col-8</div>
          </el-col>
        </el-row>
      </div>

      <div class="grid-section">
        <p class="grid-label">2 列 × :span="12"（每列占 12/24）</p>
        <el-row :gutter="10" class="grid-row">
          <el-col :span="12" v-for="i in 2" :key="'e' + i">
            <div class="grid-cell">col-12</div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 3. Setting Column Width -->
    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <span class="card-title">Setting Column Width</span>
      </template>
      <p class="card-desc">通过组合不同的 span 值，可以实现非等宽列布局。以下展示两种三列非等宽组合。</p>

      <div class="grid-section">
        <p class="grid-label">三列等宽：:span="8" + :span="8" + :span="8"</p>
        <el-row :gutter="10" class="grid-row">
          <el-col :span="8"><div class="grid-cell">1 of 3</div></el-col>
          <el-col :span="8"><div class="grid-cell">2 of 3 wider</div></el-col>
          <el-col :span="8"><div class="grid-cell">3 of 3</div></el-col>
        </el-row>
      </div>

      <div class="grid-section">
        <p class="grid-label">三列非等宽：:span="10" + :span="4" + :span="10"</p>
        <el-row :gutter="10" class="grid-row">
          <el-col :span="10"><div class="grid-cell">1 of 3</div></el-col>
          <el-col :span="4"><div class="grid-cell">2 of 3 wider</div></el-col>
          <el-col :span="10"><div class="grid-cell">3 of 3</div></el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 4. Horizontal Alignment -->
    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <span class="card-title">Horizontal Alignment</span>
      </template>
      <p class="card-desc">使用 flex 对齐方式控制行内列的水平排列位置：靠左、居中、靠右。</p>

      <div class="grid-section">
        <p class="grid-label">justify-content-start（靠左对齐）</p>
        <div class="align-row align-start">
          <div class="align-col"><div class="grid-cell">col-8</div></div>
          <div class="align-col"><div class="grid-cell">col-8</div></div>
        </div>
      </div>

      <div class="grid-section">
        <p class="grid-label">justify-content-center（居中对齐）</p>
        <div class="align-row align-center">
          <div class="align-col"><div class="grid-cell">col-8</div></div>
          <div class="align-col"><div class="grid-cell">col-8</div></div>
        </div>
      </div>

      <div class="grid-section">
        <p class="grid-label">justify-content-end（靠右对齐）</p>
        <div class="align-row align-end">
          <div class="align-col"><div class="grid-cell">col-8</div></div>
          <div class="align-col"><div class="grid-cell">col-8</div></div>
        </div>
      </div>
    </el-card>

    <!-- 5. Offset -->
    <el-card shadow="hover">
      <template #header>
        <span class="card-title">Offset</span>
      </template>
      <p class="card-desc">使用 offset 属性将列向右侧偏移指定数量的栅格宽度，实现灵活的列定位。</p>

      <div class="grid-section">
        <p class="grid-label">:span="6" :offset="6"（单列偏移）</p>
        <el-row :gutter="10" class="grid-row">
          <el-col :span="6" :offset="6"><div class="grid-cell">col-6 offset-6</div></el-col>
        </el-row>
      </div>

      <div class="grid-section">
        <p class="grid-label">:span="4" :offset="4" + :span="4" :offset="4"（双列偏移）</p>
        <el-row :gutter="10" class="grid-row">
          <el-col :span="4" :offset="4"><div class="grid-cell">col-4 offset-4</div></el-col>
          <el-col :span="4" :offset="4"><div class="grid-cell">col-4 offset-4</div></el-col>
        </el-row>
      </div>

      <div class="grid-section">
        <p class="grid-label">:span="6" :offset="3"（居中偏移）</p>
        <el-row :gutter="10" class="grid-row">
          <el-col :span="6" :offset="3"><div class="grid-cell">col-6 offset-3</div></el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'

const gridOptions = [
  { name: '超小屏', minWidth: '<576px', prefix: '.col-', columns: 12, gutter: '1.5rem' },
  { name: 'Small', minWidth: '≥576px', prefix: '.col-sm-', columns: 12, gutter: '1.5rem' },
  { name: 'Medium', minWidth: '≥768px', prefix: '.col-md-', columns: 12, gutter: '1.5rem' },
  { name: 'Large', minWidth: '≥992px', prefix: '.col-lg-', columns: 12, gutter: '1.5rem' },
  { name: '超大屏', minWidth: '≥1200px', prefix: '.col-xl-', columns: 12, gutter: '1.5rem' },
  { name: '超超大屏', minWidth: '≥1400px', prefix: '.col-xxl-', columns: 12, gutter: '1.5rem' }
]
</script>

<style scoped>
.card-title {
  font-weight: 600;
  color: #5A67F5;
  font-size: 15px;
}
.card-desc {
  margin: 0 0 18px 0;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.6;
}
.grid-section {
  margin-bottom: 18px;
}
.grid-section:last-child {
  margin-bottom: 0;
}
.grid-label {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #5A67F5;
  font-weight: 500;
}
.grid-row {
  margin-bottom: 0;
}
.grid-cell {
  background: rgba(90, 103, 245, 0.1);
  border-radius: 6px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #5A67F5;
  font-weight: 600;
}

/* Horizontal Alignment */
.align-row {
  display: flex;
  margin-bottom: 0;
}
.align-start {
  justify-content: flex-start;
}
.align-center {
  justify-content: center;
}
.align-end {
  justify-content: flex-end;
}
.align-col {
  width: 33.3333%;
  padding: 0 5px;
  box-sizing: border-box;
}
</style>
