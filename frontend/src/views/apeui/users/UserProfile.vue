<template>
  <div>
    <PageHeader title="Users Profile" :breadcrumb="['APEUI库', 'Users', 'Users Profile']" />

    <!-- 顶部用户信息卡片 -->
    <el-card style="margin-bottom: 16px">
      <div style="display: flex; align-items: center; gap: 24px">
        <el-avatar :size="100" src="https://cube.elemecdn.com/0/88/03b0d432e8c87b879d3e4e37b8f6jpeg.jpeg" />
        <div>
          <h2 style="margin: 0 0 8px 0">John Doe</h2>
          <div style="color: #666; margin-bottom: 4px">Email: john.doe@example.com</div>
          <div style="margin-bottom: 4px">
            Role: <el-tag size="small" type="primary" effect="light">Administrator</el-tag>
          </div>
          <div>
            Status: <el-tag size="small" type="success" effect="light">Active</el-tag>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 两栏布局 -->
    <el-row :gutter="16">
      <!-- 左栏：个人信息 -->
      <el-col :span="12">
        <el-card header="Personal Information">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Full Name">John Doe</el-descriptions-item>
            <el-descriptions-item label="Email">john.doe@example.com</el-descriptions-item>
            <el-descriptions-item label="Phone">+1 (555) 123-4567</el-descriptions-item>
            <el-descriptions-item label="Department">Engineering</el-descriptions-item>
            <el-descriptions-item label="Location">San Francisco, CA</el-descriptions-item>
            <el-descriptions-item label="Joined">2023-06-15</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 右栏：活动记录 -->
      <el-col :span="12">
        <el-card header="Activity Log">
          <el-timeline>
            <el-timeline-item timestamp="2025-08-19 14:30" placement="top">
              Updated project "Website Redesign" status to Ongoing
            </el-timeline-item>
            <el-timeline-item timestamp="2025-08-18 09:15" placement="top">
              Created new task "API Integration" in Mobile App Development
            </el-timeline-item>
            <el-timeline-item timestamp="2025-08-15 16:45" placement="top">
              Completed milestone "Cloud Infrastructure Setup"
            </el-timeline-item>
            <el-timeline-item timestamp="2025-08-12 11:20" placement="top">
              Uploaded document "Q3 Analytics Report.pdf"
            </el-timeline-item>
            <el-timeline-item timestamp="2025-08-10 08:00" placement="top">
              Logged into the system
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
  --el-tag-bg-color: rgba(83, 70, 134, 0.1);
  --el-tag-border-color: rgba(83, 70, 134, 0.2);
  --el-tag-text-color: #534686;
}
</style>
