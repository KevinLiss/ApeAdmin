<template>
  <div>
    <PageHeader title="Avatars" :breadcrumb="['APEUI库', 'Components', 'Avatars']" />

    <el-row :gutter="16">
      <el-col :span="8" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Sizes">
          <div style="display: flex; align-items: flex-end; gap: 16px">
            <el-avatar :size="100">XL</el-avatar>
            <el-avatar :size="64">L</el-avatar>
            <el-avatar :size="40">M</el-avatar>
            <el-avatar :size="28">S</el-avatar>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Status">
          <div style="display: flex; gap: 24px; align-items: center">
            <el-badge :value="3" :max="99">
              <el-avatar :size="48">A</el-avatar>
            </el-badge>
            <el-badge is-dot type="success">
              <el-avatar :size="48">B</el-avatar>
            </el-badge>
            <el-badge is-dot type="danger">
              <el-avatar :size="48">C</el-avatar>
            </el-badge>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Group">
          <el-avatar-group>
            <el-avatar>U1</el-avatar>
            <el-avatar>U2</el-avatar>
            <el-avatar>U3</el-avatar>
            <el-avatar>U4</el-avatar>
          </el-avatar-group>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="With Icons">
          <div style="display: flex; gap: 16px">
            <el-avatar :size="56" src="https://cube.elemecdn.com/0/88/03b0d432e8c87b879d3e4e37b8f6jpeg.jpeg" />
            <el-avatar :size="56">
              <el-icon :size="24"><User /></el-icon>
            </el-avatar>
            <el-avatar :size="56" style="background: #534686">
              <el-icon :size="24"><Avatar /></el-icon>
            </el-avatar>
            <el-avatar :size="56" style="background: #67C100">
              <el-icon :size="24"><CircleCheck /></el-icon>
            </el-avatar>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover" header="Rounded & Shape">
          <div style="display: flex; gap: 16px; align-items: center">
            <el-avatar :size="56" shape="square" style="background: #534686">方</el-avatar>
            <el-avatar :size="56" shape="round" style="background: #3EBCB9">圆</el-avatar>
            <el-avatar :size="56" shape="circle" style="background: #E56809">O</el-avatar>
            <el-avatar :size="56" style="background: linear-gradient(135deg, #534686, #7b6fa8)">渐</el-avatar>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'
</script>
