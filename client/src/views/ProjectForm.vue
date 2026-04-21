<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center h-16 space-x-4">
          <router-link to="/projects" class="text-gray-600 hover:text-gray-900">项目列表</router-link>
          <span class="text-gray-400">/</span>
          <span class="text-gray-800 font-medium">{{ isEdit ? '编辑项目' : '新增项目' }}</span>
        </div>
      </div>
    </nav>

    <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white rounded-lg shadow p-6">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div v-if="!isEdit">
            <label class="block text-sm font-medium text-gray-700 mb-1">选择已有项目（可选）</label>
            <select
              v-model="selectedExistingProject"
              @change="onSelectExistingProject"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="">-- 选择已有项目（仅修改角色和工作内容）--</option>
              <option v-for="p in uniqueProjects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
            <p class="text-sm text-gray-500 mt-1">选择已有项目将仅允许修改角色和工作内容，新建项目则创建全新项目</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">项目名称</label>
              <input
                v-model="form.name"
                type="text"
                :required="!selectedExistingProject"
                :disabled="!!selectedExistingProject || !canEdit"
                :placeholder="selectedExistingProject ? '' : '请输入新项目名称'"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">项目类型</label>
              <input
                v-model="form.type"
                type="text"
                :disabled="!canEdit"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">项目角色</label>
              <input
                v-model="form.role"
                type="text"
                :disabled="!canEdit"
                :placeholder="selectedExistingProject ? '' : '请输入角色'"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">当前状态</label>
              <select
                v-model="form.status"
                :disabled="!canEdit"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100"
              >
                <option value="未完成">未完成</option>
                <option value="进行中">进行中</option>
                <option value="完成">完成</option>
                <option value="滞后">滞后</option>
                <option value="暂停">暂停</option>
                <option value="取消">取消</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">开始日期</label>
              <input
                v-model="form.start_date"
                type="date"
                :disabled="!canEdit"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">截止日期</label>
              <input
                v-model="form.end_date"
                type="date"
                :disabled="!canEdit"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">进度 ({{ Math.round(form.progress * 100) }}%)</label>
              <input
                v-model.number="form.progress"
                type="range"
                min="0"
                max="1"
                step="0.01"
                :disabled="!canEdit"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:bg-gray-300"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">主要工作内容</label>
            <textarea
              v-model="form.work_content"
              rows="4"
              :disabled="!canEdit"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">备注</label>
            <textarea
              v-model="form.remark"
              rows="2"
              :disabled="!canEdit"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100"
            ></textarea>
          </div>

          <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>

          <div class="flex justify-end space-x-4">
            <router-link to="/projects" class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
              返回
            </router-link>
            <button
              v-if="canEdit"
              type="submit"
              :disabled="loading"
              class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
              {{ loading ? '保存中...' : (selectedExistingProject ? '保存角色和工作内容' : '保存') }}
            </button>
          </div>
        </form>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { projects } from '../api';

const router = useRouter();
const route = useRoute();
const isEdit = computed(() => !!route.params.id);
const loading = ref(false);
const error = ref('');
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));
const isAdmin = computed(() => user.value.role === 'admin');
const isOwner = ref(false);
const canEdit = computed(() => {
  // 新建项目时所有人都可以编辑
  if (!isEdit.value) return true;
  // 编辑时只有 owner 或 admin 可以编辑
  return isAdmin.value || isOwner.value;
});

const selectedExistingProject = ref('');
const existingProjects = ref([]);

const form = ref({
  name: '',
  type: '',
  role: '',
  work_content: '',
  start_date: '',
  end_date: '',
  progress: 0,
  status: '未完成',
  remark: ''
});

// Get unique projects by name
const uniqueProjects = computed(() => {
  const seen = new Set();
  return existingProjects.value.filter(p => {
    if (seen.has(p.name)) return false;
    seen.add(p.name);
    return true;
  });
});

async function fetchAllProjects() {
  try {
    const { data } = await projects.list();
    existingProjects.value = data;
  } catch (err) {
    console.error(err);
  }
}

function onSelectExistingProject() {
  if (!selectedExistingProject.value) {
    // Reset to blank form for new project
    form.value = {
      name: '',
      type: '',
      role: '',
      work_content: '',
      start_date: '',
      end_date: '',
      progress: 0,
      status: '未完成',
      remark: ''
    };
    return;
  }

  const project = existingProjects.value.find(p => p.id === parseInt(selectedExistingProject.value));
  if (project) {
    form.value = {
      name: project.name,
      type: project.type || '',
      role: project.role || '',
      work_content: project.work_content || '',
      start_date: project.start_date || '',
      end_date: project.end_date || '',
      progress: project.progress || 0,
      status: project.status || '未完成',
      remark: project.remark || ''
    };
  }
}

async function fetchProject() {
  if (!isEdit.value) return;
  try {
    const { data } = await projects.list();
    const project = data.find(p => p.id === parseInt(route.params.id));
    if (project) {
      form.value = { ...project };
      isOwner.value = project.user_id === user.value.id;
      if (!isOwner.value && !isAdmin.value) {
        error.value = '您没有权限编辑此项目';
      }
    }
  } catch (err) {
    error.value = '获取项目信息失败';
  }
}

async function handleSubmit() {
  if (!canEdit.value) {
    error.value = '您没有权限修改此项目';
    return;
  }
  loading.value = true;
  error.value = '';

  try {
    if (isEdit.value) {
      await projects.update(route.params.id, form.value);
    } else if (selectedExistingProject.value) {
      // Adding a new user to existing project - create a new project entry
      const newProject = await projects.create({
        name: form.value.name,
        type: form.value.type,
        role: form.value.role,
        work_content: form.value.work_content,
        start_date: form.value.start_date,
        end_date: form.value.end_date,
        progress: form.value.progress,
        status: form.value.status,
        remark: form.value.remark
      });
      router.push('/projects');
    } else {
      await projects.create(form.value);
    }
    router.push('/projects');
  } catch (err) {
    error.value = err.response?.data?.error || '保存失败';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (!isEdit.value) {
    fetchAllProjects();
  }
  fetchProject();
});
</script>
