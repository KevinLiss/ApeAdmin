<template>
  <div>
    <PageHeader title="用户资料" :breadcrumb="['APEUI库', '用户中心', '用户资料']" />

    <!-- 顶部用户信息卡片 -->
    <el-card style="margin-bottom: 16px">
      <div style="display: flex; align-items: center; gap: 24px">
        <el-avatar :size="100" src="https://cube.elemecdn.com/0/88/03b0d432e8c87b879d3e4e37b8f6jpeg.jpeg" />
        <div>
          <h2 style="margin: 0 0 8px 0">张伟</h2>
          <div style="color: #666; margin-bottom: 4px">邮箱：john.doe@example.com</div>
          <div style="margin-bottom: 4px">
            角色： <el-tag size="small" type="primary" effect="light">管理员</el-tag>
          </div>
          <div>
            状态： <el-tag size="small" type="success" effect="light">正常</el-tag>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 两栏布局 -->
    <el-row :gutter="16">
      <!-- 左栏：个人信息 -->
      <el-col :span="12">
        <el-card header="个人信息">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Full Name">张伟</el-descriptions-item>
            <el-descriptions-item label="Email">john.doe@example.com</el-descriptions-item>
            <el-descriptions-item label="Phone">+1 (555) 123-4567</el-descriptions-item>
            <el-descriptions-item label="Department">工程部</el-descriptions-item>
            <el-descriptions-item label="Location">中国 广州</el-descriptions-item>
            <el-descriptions-item label="Joined">2023-06-15</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 右栏：活动记录 -->
      <el-col :span="12">
        <el-card header="操作日志">
          <el-timeline>
            <el-timeline-item timestamp="2025-08-19 14:30" placement="top">
              更新了项目「网站改版」的状态为进行中
            </el-timeline-item>
            <el-timeline-item timestamp="2025-08-18 09:15" placement="top">
              在「移动应用开发」中新建了任务「API 集成」
            </el-timeline-item>
            <el-timeline-item timestamp="2025-08-15 16:45" placement="top">
              完成了里程碑「云基础设施搭建」
            </el-timeline-item>
            <el-timeline-item timestamp="2025-08-12 11:20" placement="top">
              上传了文档「Q3 分析报告.pdf」
            </el-timeline-item>
            <el-timeline-item timestamp="2025-08-10 08:00" placement="top">
              登录了系统
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
</script>

<style scoped>
:deep(.el-tag--primary) {
  --el-tag-bg-color: rgba(90, 103, 245, 0.1);
  --el-tag-border-color: rgba(90, 103, 245, 0.2);
  --el-tag-text-color: #5A67F5;
}
</style>
