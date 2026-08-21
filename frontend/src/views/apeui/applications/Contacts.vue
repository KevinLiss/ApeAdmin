<template>
  <div>
    <PageHeader title="Contacts" :breadcrumb="['APEUI库', 'Applications', 'Contacts']" />

    <el-row :gutter="30">
      <!-- 左侧联系人列表 -->
      <el-col :span="10">
        <el-card>
          <template #header>
            <span class="card-title">联系人列表</span>
          </template>
          <el-input
            v-model="search"
            placeholder="搜索联系人..."
            :prefix-icon="Search"
            clearable
            style="margin-bottom: 16px"
          />
          <div class="contact-groups">
            <div v-for="group in groupedContacts" :key="group.letter" class="contact-group">
              <div class="group-letter">{{ group.letter }}</div>
              <div
                v-for="person in group.people"
                :key="person.id"
                class="contact-item"
                :class="{ active: selectedId === person.id }"
                @click="selectContact(person.id)"
              >
                <el-avatar :size="36" :src="person.avatar" />
                <div class="contact-info">
                  <div class="contact-name">{{ person.name }}</div>
                  <div class="contact-role">{{ person.position }}</div>
                </div>
              </div>
            </div>
            <el-empty v-if="groupedContacts.length === 0" description="未找到联系人" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧详情 -->
      <el-col :span="14">
        <el-card v-if="selectedContact">
          <template #header>
            <span class="card-title">联系人详情</span>
          </template>
          <div class="detail-top">
            <el-avatar :size="80" :src="selectedContact.avatar" />
            <div class="detail-person">
              <h2 class="detail-name">{{ selectedContact.name }}</h2>
              <p class="detail-position">{{ selectedContact.position }}</p>
              <p class="detail-dept">{{ selectedContact.department }}</p>
            </div>
          </div>

          <el-divider />

          <div class="detail-section">
            <h4 class="section-label">联系信息</h4>
            <div class="info-row">
              <el-icon><Phone /></el-icon>
              <span>{{ selectedContact.phone }}</span>
            </div>
            <div class="info-row">
              <el-icon><Message /></el-icon>
              <span>{{ selectedContact.email }}</span>
            </div>
            <div class="info-row">
              <el-icon><Location /></el-icon>
              <span>{{ selectedContact.address }}</span>
            </div>
          </div>

          <el-divider />

          <div class="detail-section">
            <h4 class="section-label">技能标签</h4>
            <div class="tag-group">
              <el-tag
                v-for="skill in selectedContact.skills"
                :key="skill"
                effect="light"
                round
              >
                {{ skill }}
              </el-tag>
            </div>
          </div>

          <el-divider />

          <div class="detail-actions">
            <el-button type="primary" :icon="Edit">编辑</el-button>
            <el-button :icon="ChatDotRound">发消息</el-button>
            <el-button type="danger" :icon="Delete">删除</el-button>
          </div>
        </el-card>
        <el-card v-else>
          <el-empty description="请选择左侧联系人查看详情" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, Phone, Message, Location, Edit, ChatDotRound, Delete } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

interface Contact {
  id: number
  name: string
  avatar: string
  position: string
  department: string
  phone: string
  email: string
  address: string
  skills: string[]
}

const avatarBase = 'https://api.dicebear.com/7.x/avataaars/svg?seed='

const contacts: Contact[] = [
  { id: 1, name: '安琪', avatar: avatarBase + 'anqi', position: '产品经理', department: '产品部', phone: '138-0013-8001', email: 'anqi@company.com', address: '广州市天河区珠江新城 A 座 12 层', skills: ['产品设计', '需求分析', 'Axure', 'Figma'] },
  { id: 2, name: '艾琳', avatar: avatarBase + 'ailin', position: '前端工程师', department: '研发部', phone: '138-0013-8002', email: 'ailin@company.com', address: '广州市天河区珠江新城 A 座 10 层', skills: ['Vue3', 'TypeScript', 'UI 设计'] },
  { id: 3, name: '毕胜', avatar: avatarBase + 'bisheng', position: '后端工程师', department: '研发部', phone: '138-0013-8003', email: 'bisheng@company.com', address: '广州市天河区珠江新城 B 座 8 层', skills: ['Python', 'FastAPI', 'MySQL', 'Redis'] },
  { id: 4, name: '陈晨', avatar: avatarBase + 'chenchen', position: '全栈工程师', department: '研发部', phone: '138-0013-8004', email: 'chenchen@company.com', address: '广州市天河区珠江新城 A 座 10 层', skills: ['Vue3', 'Node.js', 'Docker', 'K8s'] },
  { id: 5, name: '邓超', avatar: avatarBase + 'dengchao', position: '测试工程师', department: '质量部', phone: '138-0013-8005', email: 'dengchao@company.com', address: '广州市天河区珠江新城 C 座 5 层', skills: ['自动化测试', 'Selenium', 'Jest'] },
  { id: 6, name: '丁一', avatar: avatarBase + 'dingyi', position: '运维工程师', department: '运维部', phone: '138-0013-8006', email: 'dingyi@company.com', address: '广州市天河区珠江新城 C 座 3 层', skills: ['Linux', 'Docker', 'CI/CD', 'Nginx'] },
  { id: 7, name: '陈明', avatar: avatarBase + 'chenming', position: '架构师', department: '研发部', phone: '138-0013-8007', email: 'chenming@company.com', address: '广州市天河区珠江新城 A 座 15 层', skills: ['系统架构', '微服务', 'DDD', '云原生'] },
  { id: 8, name: '丁玲', avatar: avatarBase + 'dingling', position: 'UI 设计师', department: '设计部', phone: '138-0013-8008', email: 'dingling@company.com', address: '广州市天河区珠江新城 D 座 6 层', skills: ['UI 设计', 'Figma', '插画', '品牌设计'] },
  { id: 9, name: '杜甫', avatar: avatarBase + 'dufu', position: '数据分析师', department: '数据部', phone: '138-0013-8009', email: 'dufu@company.com', address: '广州市天河区珠江新城 B 座 11 层', skills: ['SQL', 'Python', '数据可视化', 'Tableau'] },
]

const search = ref('')
const selectedId = ref(1)

const selectedContact = computed(() =>
  contacts.find((c) => c.id === selectedId.value)
)

const filteredContacts = computed(() => {
  if (!search.value) return contacts
  return contacts.filter((c) => c.name.includes(search.value) || c.position.includes(search.value))
})

const groupedContacts = computed(() => {
  const groups: Record<string, Contact[]> = {}
  filteredContacts.value.forEach((c) => {
    const letter = c.name[0].toUpperCase()
    if (!groups[letter]) groups[letter] = []
    groups[letter].push(c)
  })
  return Object.keys(groups)
    .sort()
    .map((letter) => ({ letter, people: groups[letter] }))
})

const selectContact = (id: number) => {
  selectedId.value = id
}
</script>

<style scoped>
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #534686;
}

.contact-groups {
  max-height: 600px;
  overflow-y: auto;
}

.group-letter {
  font-size: 14px;
  font-weight: 700;
  color: #534686;
  padding: 10px 4px 6px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.contact-item:hover {
  background: #f5f3f9;
}

.contact-item.active {
  background: #edeaf4;
}

.contact-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.contact-role {
  font-size: 12px;
  color: #999;
}

.detail-top {
  display: flex;
  align-items: center;
  gap: 24px;
}

.detail-name {
  font-size: 22px;
  font-weight: 700;
  color: #534686;
  margin: 0 0 4px 0;
}

.detail-position {
  font-size: 15px;
  color: #666;
  margin: 0 0 2px 0;
}

.detail-dept {
  font-size: 13px;
  color: #999;
  margin: 0;
}

.detail-section {
  margin-bottom: 8px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: #534686;
  margin: 0 0 12px 0;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 14px;
  color: #555;
}

.info-row .el-icon {
  color: #534686;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-group .el-tag {
  border-color: #d8d2e8;
  color: #534686;
}

.detail-actions {
  display: flex;
  gap: 12px;
}

:deep(.el-button--primary) {
  --el-color-primary: #534686;
  --el-button-bg-color: #534686;
  --el-button-border-color: #534686;
  --el-button-hover-bg-color: #6b5c9e;
  --el-button-hover-border-color: #6b5c9e;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}
</style>
