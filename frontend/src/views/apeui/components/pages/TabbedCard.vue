<template>
  <div class="tabbed-card-page">
    <PageHeader title="标签页卡片" :breadcrumb="['APEUI库', '组件示例', '标签页卡片']" />

    <el-row :gutter="30">
      <!-- 1. 简单标签页 -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">简单标签页</span>
          </template>
          <el-tabs v-model="simpleTab">
            <el-tab-pane label="Home" name="home">
              <p class="lorem">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.</p>
              <p class="lorem">Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident sunt in culpa qui officia.</p>
            </el-tab-pane>
            <el-tab-pane label="Profile" name="profile">
              <p class="lorem">Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.</p>
              <p class="lorem">Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore.</p>
            </el-tab-pane>
            <el-tab-pane label="Contact" name="contact">
              <p class="lorem">At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias.</p>
              <p class="lorem">Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus.</p>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 2. Tab With Icon -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Tab With Icon</span>
          </template>
          <el-tabs v-model="iconTab">
            <el-tab-pane name="home">
              <template #label>
                <span class="tab-with-icon"><el-icon><HomeFilled /></el-icon> Home</span>
              </template>
              <p class="lorem">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
              <p class="lorem">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor.</p>
            </el-tab-pane>
            <el-tab-pane name="profile">
              <template #label>
                <span class="tab-with-icon"><el-icon><User /></el-icon> Profile</span>
              </template>
              <p class="lorem">Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat.</p>
              <p class="lorem">Cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum sed ut perspiciatis unde omnis.</p>
            </el-tab-pane>
            <el-tab-pane name="contact">
              <template #label>
                <span class="tab-with-icon"><el-icon><Message /></el-icon> Contact</span>
              </template>
              <p class="lorem">Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam eaque.</p>
              <p class="lorem">Ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo nemo enim ipsam voluptatem.</p>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 3. Color Tab - Primary -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Color Tab — Primary</span>
          </template>
          <el-tabs v-model="colorPrimaryTab" type="card" class="tab-primary">
            <el-tab-pane label="Home" name="home">
              <p class="lorem">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
              <p class="lorem">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute.</p>
            </el-tab-pane>
            <el-tab-pane label="Profile" name="profile">
              <p class="lorem">Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint.</p>
              <p class="lorem">Occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum sed ut perspiciatis.</p>
            </el-tab-pane>
            <el-tab-pane label="Contact" name="contact">
              <p class="lorem">Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam.</p>
              <p class="lorem">Eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo nemo enim ipsam.</p>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 4. Color Tab - Secondary -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Color Tab — Secondary</span>
          </template>
          <el-tabs v-model="colorSecondaryTab" type="card" class="tab-secondary">
            <el-tab-pane label="Home" name="home">
              <p class="lorem">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
              <p class="lorem">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute.</p>
            </el-tab-pane>
            <el-tab-pane label="Profile" name="profile">
              <p class="lorem">Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint.</p>
              <p class="lorem">Occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum sed ut perspiciatis.</p>
            </el-tab-pane>
            <el-tab-pane label="Contact" name="contact">
              <p class="lorem">Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam.</p>
              <p class="lorem">Eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo nemo enim ipsam.</p>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 5. Material Tab -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Material Tab</span>
          </template>
          <el-tabs v-model="materialTab">
            <el-tab-pane label="Home" name="home">
              <p class="lorem">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
              <p class="lorem">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute.</p>
            </el-tab-pane>
            <el-tab-pane label="Profile" name="profile">
              <p class="lorem">Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint.</p>
              <p class="lorem">Occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum sed ut perspiciatis.</p>
            </el-tab-pane>
            <el-tab-pane label="Contact" name="contact">
              <p class="lorem">Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam.</p>
              <p class="lorem">Eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo nemo enim ipsam.</p>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 6. Material Tab With Icon -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Material Tab With Icon</span>
          </template>
          <el-tabs v-model="materialIconTab">
            <el-tab-pane name="home">
              <template #label>
                <span class="tab-with-icon"><el-icon><HomeFilled /></el-icon> Home</span>
              </template>
              <p class="lorem">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
              <p class="lorem">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute.</p>
            </el-tab-pane>
            <el-tab-pane name="profile">
              <template #label>
                <span class="tab-with-icon"><el-icon><User /></el-icon> Profile</span>
              </template>
              <p class="lorem">Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint.</p>
              <p class="lorem">Occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum sed ut perspiciatis.</p>
            </el-tab-pane>
            <el-tab-pane name="contact">
              <template #label>
                <span class="tab-with-icon"><el-icon><Message /></el-icon> Contact</span>
              </template>
              <p class="lorem">Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam.</p>
              <p class="lorem">Eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo nemo enim ipsam.</p>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 7. Material Tab - Success -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Material Tab — Success</span>
          </template>
          <el-tabs v-model="materialSuccessTab" class="tab-success">
            <el-tab-pane name="home">
              <template #label>
                <span class="tab-with-icon"><el-icon><HomeFilled /></el-icon> Home</span>
              </template>
              <p class="lorem">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
              <p class="lorem">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute.</p>
            </el-tab-pane>
            <el-tab-pane name="profile">
              <template #label>
                <span class="tab-with-icon"><el-icon><User /></el-icon> Profile</span>
              </template>
              <p class="lorem">Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint.</p>
              <p class="lorem">Occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum sed ut perspiciatis.</p>
            </el-tab-pane>
            <el-tab-pane name="contact">
              <template #label>
                <span class="tab-with-icon"><el-icon><Message /></el-icon> Contact</span>
              </template>
              <p class="lorem">Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam.</p>
              <p class="lorem">Eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo nemo enim ipsam.</p>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 8. Tab With Table -->
      <el-col :span="12" class="ape-col">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Tab With Table</span>
          </template>
          <el-tabs v-model="tableTab">
            <el-tab-pane label="Online" name="online">
              <el-table :data="onlineUsers" style="width: 100%" size="default">
                <el-table-column prop="name" label="Name" min-width="150" />
                <el-table-column prop="status" label="Status" width="110">
                  <template #default="{ row }">
                    <el-tag type="success" size="small" effect="light">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="date" label="Date" width="130" />
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="Offline" name="offline">
              <el-table :data="offlineUsers" style="width: 100%" size="default">
                <el-table-column prop="name" label="Name" min-width="150" />
                <el-table-column prop="status" label="Status" width="110">
                  <template #default="{ row }">
                    <el-tag type="info" size="small" effect="light">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="date" label="Date" width="130" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { HomeFilled, User, Message } from '@element-plus/icons-vue'
import PageHeader from '../PageHeader.vue'

const simpleTab = ref('home')
const iconTab = ref('home')
const colorPrimaryTab = ref('home')
const colorSecondaryTab = ref('home')
const materialTab = ref('profile')
const materialIconTab = ref('profile')
const materialSuccessTab = ref('home')
const tableTab = ref('online')

const onlineUsers = [
  { name: '艾丽斯·安德森', status: '在线', date: '2026-08-21' },
  { name: '鲍勃·布朗', status: '在线', date: '2026-08-20' },
  { name: '查理·克拉克', status: '在线', date: '2026-08-19' },
  { name: '戴安娜·戴维斯', status: '在线', date: '2026-08-18' },
]

const offlineUsers = [
  { name: '伊万·埃文斯', status: '离线', date: '2026-08-15' },
  { name: '菲奥娜·福斯特', status: '离线', date: '2026-08-12' },
  { name: '乔治·格林', status: '离线', date: '2026-08-10' },
]
</script>

<style scoped>
.card-title {
  font-weight: 600;
  color: #5A67F5;
}

.ape-col {
  margin-bottom: 30px;
}

.lorem {
  margin: 0 0 12px;
  color: #5a6273;
  line-height: 1.7;
  font-size: 14px;
}

.lorem:last-child {
  margin-bottom: 0;
}

.tab-with-icon {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* Color Tab — Primary (purple, card type) */
.tab-primary :deep(.el-tabs__item.is-active) {
  color: #5A67F5;
  background-color: rgba(90, 103, 245, 0.05);
  box-shadow: inset 0 2px 0 #5A67F5;
}

.tab-primary :deep(.el-tabs__item:hover) {
  color: #5A67F5;
}

/* Color Tab — Secondary (orange, card type) */
.tab-secondary :deep(.el-tabs__item.is-active) {
  color: #d97e50;
  background-color: rgba(255, 164, 122, 0.08);
  box-shadow: inset 0 2px 0 #FFA47A;
}

.tab-secondary :deep(.el-tabs__item:hover) {
  color: #d97e50;
}

/* Material Tab — Success (green, line type) */
.tab-success :deep(.el-tabs__item.is-active) {
  color: #529c00;
}

.tab-success :deep(.el-tabs__item:hover) {
  color: #529c00;
}

.tab-success :deep(.el-tabs__active-bar) {
  background-color: #67C100;
}
</style>
