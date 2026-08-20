<template>
  <div>
    <PageHeader title="Typography" :breadcrumb="['APEUI库', 'Components', 'Typography']" />

    <el-row :gutter="16">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Headings">
          <h1>H1. 标题文字 30px</h1>
          <h2>H2. 标题文字 24px</h2>
          <h3>H3. 标题文字 20px</h3>
          <h4>H4. 标题文字 16px</h4>
          <h5>H5. 标题文字 14px</h5>
          <h6>H6. 标题文字 12px</h6>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Display & Lead">
          <div style="font-size: 48px; font-weight: 900; color: #534686; line-height: 1.1">Display 1</div>
          <div style="font-size: 36px; font-weight: 800; color: #534686; line-height: 1.2">Display 2</div>
          <p style="font-size: 18px; font-weight: 400; margin: 16px 0 0; color: #5a6273">Lead paragraph — 用于引言或段落描述，字号 18px，颜色偏灰。</p>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Text Elements">
          <p>Normal body text at 14px.</p>
          <p><strong>Bold text</strong> / <em>Italic text</em> / <u>Underline</u> / <s>Strikethrough</s></p>
          <p><small>Small text 12px</small> / <mark>Highlighted text</mark> / <abbr>abbr</abbr></p>
          <p style="text-align: left; color: #909399">Left aligned</p>
          <p style="text-align: center">Center aligned</p>
          <p style="text-align: right; color: #909399">Right aligned</p>
          <blockquote style="border-left: 4px solid #534686; padding-left: 16px; margin: 12px 0; color: #5a6273">
            Blockquote — 这是引用块，左侧有紫色边框。
          </blockquote>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Lists">
          <ul>
            <li>Unordered list item 1</li>
            <li>Unordered list item 2</li>
            <li>Unordered list item 3</li>
          </ul>
          <ol>
            <li>Ordered list item 1</li>
            <li>Ordered list item 2</li>
            <li>Ordered list item 3</li>
          </ol>
          <dl>
            <dt>Description term</dt>
            <dd>Description detail</dd>
          </dl>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'
</script>
