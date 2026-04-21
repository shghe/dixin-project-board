<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center space-x-4">
            <router-link to="/" class="text-gray-600 hover:text-gray-900">首页</router-link>
            <span class="text-gray-400">/</span>
            <span class="text-gray-800 font-medium">项目列表</span>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-gray-600">{{ user.name }}</span>
            <button @click="handleLogout" class="text-gray-500 hover:text-red-600">退出</button>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-6 flex justify-between items-center">
        <h2 class="text-2xl font-bold text-gray-800">项目列表</h2>
        <div class="flex space-x-2">
          <button @click="fetchProjects" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
            刷新
          </button>
          <select v-if="isAdmin" v-model="filterUserId" @change="fetchProjects" class="px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">全部人员</option>
            <option v-for="u in userList" :key="u.id" :value="u.id">{{ u.name }}</option>
          </select>
          <router-link to="/projects/new" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            新增项目
          </router-link>
          <button v-if="isAdmin" @click="showImportModal = true" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
            导入Excel
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-center py-8">加载中...</div>

      <div v-else class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">项目名称</th>
              <th v-if="isAdmin" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">负责人</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">角色</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">进度</th>
              <th class="px-6 py-3 whitespace-nowrap text-center text-xs font-medium text-gray-500 uppercase">状态</th>
              <th class="px-6 py-3 whitespace-nowrap text-center text-xs font-medium text-gray-500 uppercase">超期</th>
              <th class="px-6 py-3 whitespace-nowrap text-left text-xs font-medium text-gray-500 uppercase">截止日期</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="p in projects" :key="p.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <router-link :to="`/projects/${p.id}/edit`" class="font-medium text-blue-600 hover:text-blue-800 hover:underline">{{ p.name || '-' }}</router-link>
                <div class="text-sm text-gray-500 truncate max-w-xs">{{ p.work_content || '' }}</div>
              </td>
              <td v-if="isAdmin" class="px-6 py-4 whitespace-nowrap">
                <router-link :to="`/?userId=${p.user_id}`" class="text-blue-600 hover:text-blue-800 hover:underline">
                  {{ getUserName(p.user_id) }}
                </router-link>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-600">{{ p.role || '-' }}</td>
              <td class="px-6 py-4 text-center">
                <div class="flex items-center justify-center">
                  <div class="w-16 bg-gray-200 rounded-full h-2">
                    <div class="bg-blue-600 h-2 rounded-full" :style="{ width: (p.progress * 100) + '%' }"></div>
                  </div>
                  <span class="ml-2 text-sm text-gray-600">{{ Math.round(p.progress * 100) }}%</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span :class="statusClass(p.status || '未完成')">{{ p.status || '未完成' }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span v-if="p.is_overdue" class="text-red-600 font-bold">是</span>
                <span v-else class="text-gray-400">否</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-600">{{ p.end_date || '-' }}</td>
              <td class="px-6 py-4 text-center" style="min-width: 100px;">
                <span v-if="isAdmin || p.user_id === user.id" class="inline-flex">
                  <router-link :to="`/projects/${p.id}/edit`" class="text-blue-600 hover:text-blue-800 mr-3">编辑</router-link>
                  <button @click="handleDelete(p.id)" class="text-red-600 hover:text-red-800">删除</button>
                </span>
                <span v-else class="text-gray-400">-</span>
              </td>
            </tr>
            <tr v-if="projects.length === 0">
              <td :colspan="isAdmin ? 8 : 7" class="px-6 py-8 text-center text-gray-500">暂无项目</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <div v-if="showImportModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">导入Excel数据</h3>
        <input type="file" accept=".xlsx,.xls" @change="handleFileChange" class="mb-4" />
        <div v-if="uploadProgress" class="mb-4 text-blue-600">{{ uploadProgress }}</div>
        <div class="flex justify-end space-x-2">
          <button @click="showImportModal = false" class="px-4 py-2 text-gray-600 hover:text-gray-800">取消</button>
          <button @click="handleImport" :disabled="!selectedFile || uploading" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400">
            {{ uploading ? '导入中...' : '确认导入' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { projects as projectsApi, users as userApi, upload } from '../api';

const router = useRouter();
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));
const isAdmin = computed(() => user.value.role === 'admin');
const loading = ref(false);
const projectsList = ref([]);
const userList = ref([]);
const filterUserId = ref('');
const showImportModal = ref(false);
const selectedFile = ref(null);
const uploading = ref(false);
const uploadProgress = ref('');

const projects = computed(() => {
  let list = projectsList.value;
  if (filterUserId.value) {
    list = list.filter(p => p.user_id === parseInt(filterUserId.value));
  }
  return list.sort((a, b) => (a.progress || 0) - (b.progress || 0));
});

async function fetchProjects() {
  loading.value = true;
  try {
    const { data } = await projectsApi.list();
    projectsList.value = data;
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
}

async function fetchUsers() {
  if (!isAdmin.value) return;
  try {
    const { data } = await userApi.list();
    userList.value = data;
  } catch (err) {
    console.error(err);
  }
}

function getUserName(userId) {
  const u = userList.value.find(x => x.id === userId);
  return u?.name || userId;
}

function statusClass(status) {
  const map = {
    '完成': 'px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs',
    '进行中': 'px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs',
    '滞后': 'px-2 py-1 bg-orange-100 text-orange-800 rounded-full text-xs',
    '暂停': 'px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs',
    '取消': 'px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs'
  };
  return map[status] || 'px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs';
}

async function handleDelete(id) {
  if (!confirm('确定要删除这个项目吗？')) return;
  try {
    await projectsApi.delete(id);
    fetchProjects();
  } catch (err) {
    alert(err.response?.data?.error || '删除失败');
  }
}

function handleFileChange(e) {
  selectedFile.value = e.target.files[0];
}

async function handleImport() {
  if (!selectedFile.value) return;
  uploading.value = true;
  uploadProgress.value = '上传中...';

  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    uploadProgress.value = '导入中...';
    const { data } = await upload.importExcel(formData);
    alert(`导入成功！新建用户: ${data.results.users}，导入项目: ${data.results.projects}`);
    showImportModal.value = false;
    fetchProjects();
  } catch (err) {
    alert(err.response?.data?.error || '导入失败');
  } finally {
    uploading.value = false;
    uploadProgress.value = '';
  }
}

function handleLogout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  router.push('/login');
}

onMounted(() => {
  fetchProjects();
  fetchUsers();
});
</script>
