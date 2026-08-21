<template>
  <div>
    <PageHeader title="排版样式" :breadcrumb="['APEUI库', '组件示例', '排版样式']" />

    <el-row :gutter="30">
      <!-- Headings -->
      <el-col :lg="12" :xs="24" class="typo-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">标题</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="heading-list">
                <h1>H1. Koho Heading</h1>
                <h2>H2. Koho Heading</h2>
                <h3>H3. Koho Heading</h3>
                <h4>H4. Koho Heading</h4>
                <h5>H5. Koho Heading</h5>
                <h6>H6. Koho Heading</h6>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="heading-list">
                <h1>H1. <small class="text-muted">副标题文字</small></h1>
                <h2>H2. <small class="text-muted">副标题文字</small></h2>
                <h3>H3. <small class="text-muted">副标题文字</small></h3>
                <h4>H4. <small class="text-muted">副标题文字</small></h4>
                <h5>H5. <small class="text-muted">副标题文字</small></h5>
                <h6>H6. <small class="text-muted">副标题文字</small></h6>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- Fancy Display Headings -->
      <el-col :lg="12" :xs="24" class="typo-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Fancy Display Headings</span>
          </template>
          <div class="display-list">
            <div class="display-item">
              <span class="display-text display-1">Display 1</span>
              <span class="display-meta">font-size: 64px / weight: 800</span>
            </div>
            <div class="display-item">
              <span class="display-text display-2">Display 2</span>
              <span class="display-meta">font-size: 52px / weight: 800</span>
            </div>
            <div class="display-item">
              <span class="display-text display-3">Display 3</span>
              <span class="display-meta">font-size: 42px / weight: 800</span>
            </div>
            <div class="display-item">
              <span class="display-text display-4">Display 4</span>
              <span class="display-meta">font-size: 34px / weight: 800</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Font Weight -->
      <el-col :lg="24" :xs="24" class="typo-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Font Weight</span>
          </template>
          <el-row :gutter="20">
            <el-col :lg="4" :sm="8" :xs="12" v-for="(item, i) in fontWeightList" :key="i">
              <div class="weight-box">
                <div class="weight-sample" :style="{ fontWeight: item.value }">{{ item.label }}</div>
                <div class="weight-meta">
                  <span class="weight-name">{{ item.name }}</span>
                  <span class="weight-value">{{ item.value }}</span>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- Lead & Inline Text -->
      <el-col :lg="12" :xs="24" class="typo-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Lead &amp; Inline Text</span>
          </template>
          <p class="lead-text">
            这是一个 Lead 引言段落，用于在内容开头做简要说明或概括。字号 18px，字重 400，
            行高 1.6，颜色偏灰，比正文更醒目但不喧宾夺主。适合产品介绍、章节摘要等场景。
          </p>
          <el-divider content-position="left"><span class="divider-label">Inline Elements</span></el-divider>
          <p class="inline-text">
            You can use the mark tag to <mark>highlight</mark> text.
          </p>
          <p class="inline-text">
            <del>This line of text is meant to be treated as deleted text.</del>
          </p>
          <p class="inline-text">
            <s>This line of text is meant to be treated as no longer accurate.</s>
          </p>
          <p class="inline-text">
            <ins>This line of text is meant to be treated as an addition to the document.</ins>
          </p>
          <p class="inline-text">
            <u>This line of text will render as underlined.</u>
          </p>
          <p class="inline-text">
            <small>This line of text is meant to be treated as fine print.</small>
          </p>
          <p class="inline-text">
            <strong>rendered as bold text.</strong>
          </p>
          <p class="inline-text">
            <em>rendered as italicized text.</em>
          </p>
        </el-card>
      </el-col>

      <!-- Text Color -->
      <el-col :lg="12" :xs="24" class="typo-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Text Color</span>
          </template>
          <div class="text-color-list">
            <p class="text-color-item" :style="{ color: item.color }" v-for="item in textColorList" :key="item.name">
              <span class="text-color-name">{{ item.name }}</span>
              <span class="text-color-value">{{ item.color }}</span>
            </p>
          </div>
        </el-card>
      </el-col>

      <!-- Lists -->
      <el-col :lg="12" :xs="24" class="typo-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Lists</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <h6 class="list-section-title">Unordered</h6>
              <ul class="list-unstyled">
                <li>Lorem ipsum dolor sit amet</li>
                <li>Consectetur adipiscing elit</li>
                <li>Integer molestie lorem at massa</li>
                <li>Facilisis in pretium nisl aliquet</li>
                <li>Nulla volutpat aliquam velit</li>
              </ul>
            </el-col>
            <el-col :span="8">
              <h6 class="list-section-title">Ordered</h6>
              <ol class="list-ordered">
                <li>Lorem ipsum dolor sit amet</li>
                <li>Consectetur adipiscing elit</li>
                <li>Integer molestie lorem at massa</li>
                <li>Facilisis in pretium nisl aliquet</li>
                <li>Nulla volutpat aliquam velit</li>
              </ol>
            </el-col>
            <el-col :span="8">
              <h6 class="list-section-title">Description</h6>
              <dl class="description-list">
                <dt>Description lists</dt>
                <dd>A description list is perfect for defining terms.</dd>
                <dt>Euismod</dt>
                <dd>Vestibulum id ligula porta felis euismod semper.</dd>
                <dt>Malesuada porta</dt>
                <dd>Etiam porta sem malesuada magna mollis euismod.</dd>
              </dl>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- Blockquotes -->
      <el-col :lg="12" :xs="24" class="typo-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Blockquotes</span>
          </template>
          <div class="blockquote-list">
            <blockquote class="blockquote blockquote--left">
              <p class="blockquote-text">
                "代码就像幽默。当你不得不解释它的时候，它就很糟糕。"
              </p>
              <footer class="blockquote-footer">
                <cite title="Cory House">Cory House</cite>
              </footer>
            </blockquote>

            <blockquote class="blockquote blockquote--center">
              <p class="blockquote-text">
                "任何傻瓜都能写出计算机能理解的代码，好的程序员能写出人能理解的代码。"
              </p>
              <footer class="blockquote-footer">
                <cite title="Martin Fowler">Martin Fowler</cite>
              </footer>
            </blockquote>

            <blockquote class="blockquote blockquote--right">
              <p class="blockquote-text">
                "简单是可靠的前提。"
              </p>
              <footer class="blockquote-footer">
                <cite title="Edsger W. Dijkstra">Edsger W. Dijkstra</cite>
              </footer>
            </blockquote>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'

const fontWeightList = [
  { label: 'Heading 1', name: 'Thin',     value: 100 },
  { label: 'Heading 2', name: 'Light',    value: 300 },
  { label: 'Heading 3', name: 'Regular',  value: 400 },
  { label: 'Heading 4', name: 'SemiBold', value: 600 },
  { label: 'Heading 5', name: 'Bold',     value: 700 },
  { label: 'Heading 6', name: 'Black',    value: 900 },
]

const textColorList = [
  { name: 'Primary Text',   color: '#5A67F5' },
  { name: 'Secondary Text', color: '#FFA47A' },
  { name: 'Success Text',   color: '#67C100' },
  { name: '信息文字',      color: '#3EBCB9' },
  { name: 'Warning Text',   color: '#E56809' },
  { name: '危险文字',    color: '#DC0808' },
  { name: '深色文字',      color: '#2C323F' },
]
</script>

<style scoped>
.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #5A67F5;
}

.typo-col {
  margin-bottom: 30px;
}

.text-muted {
  color: #909399;
  font-size: 65%;
  font-weight: 400;
}

/* Headings */
.heading-list h1,
.heading-list h2,
.heading-list h3,
.heading-list h4,
.heading-list h5,
.heading-list h6 {
  margin: 0 0 14px;
  color: #2C323F;
  line-height: 1.3;
}

.heading-list h1:last-child,
.heading-list h2:last-child,
.heading-list h3:last-child,
.heading-list h4:last-child,
.heading-list h5:last-child,
.heading-list h6:last-child {
  margin-bottom: 0;
}

.heading-list h1 { font-size: 2.25rem; font-weight: 600; }
.heading-list h2 { font-size: 1.875rem; font-weight: 600; }
.heading-list h3 { font-size: 1.5rem; font-weight: 600; }
.heading-list h4 { font-size: 1.25rem; font-weight: 600; }
.heading-list h5 { font-size: 1rem; font-weight: 600; }
.heading-list h6 { font-size: 0.875rem; font-weight: 600; }

/* Display Headings */
.display-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.display-item {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.display-text {
  color: #5A67F5;
  font-weight: 800;
  line-height: 1.1;
}

.display-1 { font-size: 64px; }
.display-2 { font-size: 52px; }
.display-3 { font-size: 42px; }
.display-4 { font-size: 34px; }

.display-meta {
  font-size: 12px;
  color: #909399;
  font-family: 'Courier New', Consolas, monospace;
}

/* Font Weight */
.weight-box {
  text-align: center;
  padding: 20px 10px;
  border-radius: 10px;
  background: #F8F8FC;
  transition: background 0.2s ease;
}

.weight-box:hover {
  background: #F0EDF8;
}

.weight-sample {
  font-size: 22px;
  color: #2C323F;
  margin-bottom: 10px;
  line-height: 1.3;
}

.weight-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.weight-name {
  font-size: 13px;
  color: #5A67F5;
  font-weight: 600;
}

.weight-value {
  font-size: 12px;
  color: #909399;
  font-family: 'Courier New', Consolas, monospace;
}

/* Lead & Inline */
.lead-text {
  font-size: 18px;
  font-weight: 400;
  line-height: 1.6;
  color: #5a6273;
  margin: 0;
}

.divider-label {
  font-size: 13px;
  color: #909399;
  font-weight: 600;
}

.inline-text {
  margin: 0 0 10px;
  font-size: 14px;
  line-height: 1.8;
  color: #2C323F;
}

.inline-text:last-child {
  margin-bottom: 0;
}

.inline-text mark {
  background: #FFF3CD;
  padding: 1px 3px;
  border-radius: 3px;
}

/* Text Color */
.text-color-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.text-color-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.text-color-name {
  font-size: 16px;
}

.text-color-value {
  font-size: 13px;
  font-family: 'Courier New', Consolas, monospace;
  font-weight: 400;
  opacity: 0.7;
}

/* Lists */
.list-section-title {
  font-size: 13px;
  font-weight: 700;
  color: #5A67F5;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 12px;
}

.list-unstyled {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list-unstyled li {
  font-size: 14px;
  color: #2C323F;
  line-height: 2;
  padding-left: 14px;
  position: relative;
}

.list-unstyled li::before {
  content: '•';
  color: #5A67F5;
  font-weight: 700;
  position: absolute;
  left: 0;
}

.list-ordered {
  padding-left: 20px;
  margin: 0;
}

.list-ordered li {
  font-size: 14px;
  color: #2C323F;
  line-height: 2;
}

.description-list {
  margin: 0;
}

.description-list dt {
  font-size: 14px;
  font-weight: 700;
  color: #2C323F;
  margin-bottom: 4px;
}

.description-list dd {
  font-size: 13px;
  color: #5a6273;
  margin: 0 0 12px;
  line-height: 1.6;
}

.description-list dd:last-child {
  margin-bottom: 0;
}

/* Blockquotes */
.blockquote-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.blockquote {
  margin: 0;
  padding: 0;
  border: none;
}

.blockquote-text {
  font-size: 16px;
  font-style: italic;
  color: #2C323F;
  line-height: 1.7;
  margin: 0 0 10px;
}

.blockquote-footer {
  font-size: 13px;
  color: #909399;
}

.blockquote-footer::before {
  content: '— ';
}

.blockquote-footer cite {
  font-style: normal;
  font-weight: 600;
}

.blockquote--left {
  border-left: 4px solid #5A67F5;
  padding-left: 16px;
}

.blockquote--center {
  text-align: center;
  border-top: 2px solid #F0EDF8;
  border-bottom: 2px solid #F0EDF8;
  padding: 10px 0;
}

.blockquote--center .blockquote-footer {
  text-align: center;
}

.blockquote--right {
  border-right: 4px solid #5A67F5;
  padding-right: 16px;
  text-align: right;
}

.blockquote--right .blockquote-footer {
  text-align: right;
}
</style>
