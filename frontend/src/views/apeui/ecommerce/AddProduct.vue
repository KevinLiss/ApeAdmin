<template>
  <div class="add-product-page">
    <PageHeader title="Add Product" :breadcrumb="['APEUI库', 'Ecommerce', 'Add Product']">
      <template #actions>
        <el-button @click="onCancel">Cancel</el-button>
        <el-button type="primary" @click="onSave">Save Product</el-button>
      </template>
    </PageHeader>

    <el-row :gutter="30">
      <!-- Left: Basic Info -->
      <el-col :xs="24" :md="16">
        <el-card class="koho-card form-card" shadow="never">
          <h3 class="card-title">Basic Information</h3>
          <el-form :model="form" label-width="140px" label-position="right">
            <el-form-item label="Product Name" required>
              <el-input v-model="form.name" placeholder="Enter product name" />
            </el-form-item>
            <el-form-item label="Product Category" required>
              <el-cascader
                v-model="form.category"
                :options="categoryOptions"
                :props="{ expandTrigger: 'hover' }"
                placeholder="Select category"
                style="width: 100%"
                clearable
              />
            </el-form-item>
            <el-form-item label="Price" required>
              <el-input v-model="form.price" type="number" placeholder="0.00">
                <template #prepend>$</template>
              </el-input>
            </el-form-item>
            <el-form-item label="Original Price">
              <el-input v-model="form.oldPrice" type="number" placeholder="0.00">
                <template #prepend>$</template>
              </el-input>
            </el-form-item>
            <el-form-item label="Stock Quantity" required>
              <el-input-number v-model="form.stock" :min="0" :max="99999" style="width: 200px" />
            </el-form-item>
            <el-form-item label="Description">
              <el-input
                v-model="form.description"
                type="textarea"
                :rows="5"
                placeholder="Enter product description"
                maxlength="500"
                show-word-limit
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- SEO / Meta -->
        <el-card class="koho-card form-card" shadow="never">
          <h3 class="card-title">SEO & Meta</h3>
          <el-form :model="form" label-width="140px" label-position="right">
            <el-form-item label="Meta Title">
              <el-input v-model="form.metaTitle" placeholder="SEO title for search engines" />
            </el-form-item>
            <el-form-item label="Meta Keywords">
              <el-input v-model="form.metaKeywords" placeholder="Comma-separated keywords" />
            </el-form-item>
            <el-form-item label="Meta Description">
              <el-input v-model="form.metaDescription" type="textarea" :rows="3" placeholder="Brief description for SEO" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- Right: Media + Status -->
      <el-col :xs="24" :md="8">
        <el-card class="koho-card form-card" shadow="never">
          <h3 class="card-title">Product Image</h3>
          <el-upload
            action="#"
            :auto-upload="false"
            list-type="picture-card"
            :on-change="handleUploadChange"
            :on-remove="handleUploadRemove"
            :limit="5"
            :file-list="fileList"
            drag
            class="upload-area"
          >
            <el-icon class="upload-icon"><Plus /></el-icon>
            <div class="el-upload__text">Drop image here or<em>click to upload</em></div>
            <template #tip>
              <div class="upload-tip">JPG, PNG files up to 5MB. Max 5 images.</div>
            </template>
          </el-upload>
        </el-card>

        <el-card class="koho-card form-card" shadow="never">
          <h3 class="card-title">Status</h3>
          <el-form :model="form" label-width="140px" label-position="right">
            <el-form-item label="Publish Status">
              <el-switch
                v-model="form.isPublished"
                active-text="Published"
                inactive-text="Draft"
                inline-prompt
                style="--el-switch-on-color: #67C100"
              />
            </el-form-item>
            <el-form-item label="Featured">
              <el-switch
                v-model="form.featured"
                inline-prompt
                active-text="Yes"
                inactive-text="No"
                style="--el-switch-on-color: #534686"
              />
            </el-form-item>
            <el-form-item label="Allow Pre-order">
              <el-switch
                v-model="form.preOrder"
                inline-prompt
                active-text="Yes"
                inactive-text="No"
                style="--el-switch-on-color: #3EBCB9"
              />
            </el-form-item>
          </el-form>
          <div class="status-preview">
            <el-tag :type="form.isPublished ? 'success' : 'info'" effect="dark" size="large">
              {{ form.isPublished ? 'Published' : 'Draft' }}
            </el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Footer Actions -->
    <div class="footer-actions">
      <el-button @click="onCancel">Cancel</el-button>
      <el-button type="primary" @click="onSave">Save Product</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

const form = ref({
  name: '',
  category: [] as string[],
  price: '',
  oldPrice: '',
  stock: 0,
  description: '',
  metaTitle: '',
  metaKeywords: '',
  metaDescription: '',
  isPublished: false,
  featured: false,
  preOrder: false,
})

const categoryOptions = [
  {
    value: 'electronics',
    label: 'Electronics',
    children: [
      { value: 'headphones', label: 'Headphones & Audio' },
      { value: 'wearables', label: 'Wearables' },
      { value: 'phones', label: 'Smartphones' },
      { value: 'accessories', label: 'Accessories' },
    ],
  },
  {
    value: 'fashion',
    label: 'Fashion',
    children: [
      { value: 'mens', label: "Men's Clothing" },
      { value: 'womens', label: "Women's Clothing" },
      { value: 'shoes', label: 'Shoes' },
      { value: 'bags', label: 'Bags & Accessories' },
    ],
  },
  {
    value: 'home',
    label: 'Home & Living',
    children: [
      { value: 'kitchen', label: 'Kitchen & Dining' },
      { value: 'decor', label: 'Home Decor' },
      { value: 'furniture', label: 'Furniture' },
    ],
  },
  {
    value: 'sports',
    label: 'Sports & Fitness',
    children: [
      { value: 'fitness', label: 'Fitness Equipment' },
      { value: 'outdoor', label: 'Outdoor Gear' },
      { value: 'yoga', label: 'Yoga & Wellness' },
    ],
  },
]

const fileList = ref<any[]>([])

const handleUploadChange = (file: any) => {
  fileList.value.push(file)
}

const handleUploadRemove = (file: any) => {
  fileList.value = fileList.value.filter(f => f.uid !== file.uid)
}

const onSave = () => {
  if (!form.value.name) {
    ElMessage.warning('Please enter product name')
    return
  }
  if (!form.value.price) {
    ElMessage.warning('Please enter product price')
    return
  }
  ElMessage.success('Product saved successfully')
}

const onCancel = () => {
  form.value = {
    name: '',
    category: [],
    price: '',
    oldPrice: '',
    stock: 0,
    description: '',
    metaTitle: '',
    metaKeywords: '',
    metaDescription: '',
    isPublished: false,
    featured: false,
    preOrder: false,
  }
  fileList.value = []
  ElMessage.info('Form reset')
}
</script>

<style scoped>
.form-card {
  margin-bottom: 30px;
  border-radius: 12px;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #534686;
  margin: 0 0 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid #f0f2f5;
}

/* Upload */
.upload-area :deep(.el-upload-dragger) {
  padding: 20px;
  border-radius: 10px;
}
.upload-icon {
  font-size: 32px;
  color: #534686;
  margin-bottom: 8px;
}
:deep(.el-upload__text) {
  font-size: 13px;
  color: #909399;
}
:deep(.el-upload__text em) {
  color: #534686;
  font-style: normal;
}
.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

/* Status Preview */
.status-preview {
  text-align: center;
  padding-top: 10px;
  border-top: 1px solid #f0f2f5;
  margin-top: 10px;
}

/* Footer */
.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 10px;
}

:deep(.el-button--primary) {
  --el-button-bg-color: #534686;
  --el-button-border-color: #534686;
  --el-button-hover-bg-color: #6b5c9e;
  --el-button-hover-border-color: #6b5c9e;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}
</style>
