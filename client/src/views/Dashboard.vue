<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-800">地信院项目看板</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-gray-600">{{ user.name }} ({{ user.role === 'admin' ? '管理员' : '成员' }})</span>
            <button @click="handleLogout" class="text-gray-500 hover:text-red-600">退出</button>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-6 flex justify-between items-center">
        <h2 class="text-2xl font-bold text-gray-800">
          {{ selectedUserName || (isAdmin ? '全员统计' : '我的统计') }}
        </h2>
        <div class="flex space-x-2">
          <button @click="fetchStats" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
            刷新
          </button>
          <button v-if="selectedUserId" @click="clearSelection" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
            取消筛选
          </button>
          <select v-model="selectedUserId" @change="fetchStats" class="px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">全部人员</option>
            <option v-for="u in users.filter(u => allStats.find(s => s.userId === u.id && s.total > 0))" :key="u.id" :value="u.id">{{ u.name }}</option>
          </select>
          <router-link to="/projects" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            查看项目
          </router-link>
        </div>
      </div>

      <div v-if="loading" class="text-center py-8">加载中...</div>

      <div v-else class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-gray-500 text-sm">正常项目</div>
          <div class="text-3xl font-bold text-green-600">{{ computedStats.normal }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-gray-500 text-sm">进行中</div>
          <div class="text-3xl font-bold text-blue-600">{{ computedStats.inProgress }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-gray-500 text-sm">完成项目</div>
          <div class="text-3xl font-bold text-purple-600">{{ computedStats.completed }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-gray-500 text-sm">超期项目</div>
          <div class="text-3xl font-bold text-red-600">{{ computedStats.overdue }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-gray-500 text-sm">滞后项目</div>
          <div class="text-3xl font-bold text-orange-600">{{ computedStats.delayed }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-gray-500 text-sm">暂停</div>
          <div class="text-3xl font-bold text-gray-600">{{ computedStats.paused }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-gray-500 text-sm">总计</div>
          <div class="text-3xl font-bold text-gray-800">{{ computedStats.total }}</div>
        </div>
      </div>

      <div class="mt-8">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">人员统计列表（点击姓名查看详情）</h3>
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">姓名</th>
                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">正常</th>
                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">进行中</th>
                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">完成</th>
                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">超期</th>
                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">滞后</th>
                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">暂停</th>
                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">取消</th>
                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">总计</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="s in displayedStats" :key="s.userId" class="hover:bg-blue-50 cursor-pointer" @click="selectUser(s)">
                <td class="px-6 py-4 whitespace-nowrap font-medium text-blue-600">{{ s.userName }}</td>
                <td class="px-6 py-4 text-center text-green-600">{{ s.normal }}</td>
                <td class="px-6 py-4 text-center text-blue-600">{{ s.inProgress }}</td>
                <td class="px-6 py-4 text-center text-purple-600">{{ s.completed }}</td>
                <td class="px-6 py-4 text-center text-red-600">{{ s.overdue }}</td>
                <td class="px-6 py-4 text-center text-orange-600">{{ s.delayed }}</td>
                <td class="px-6 py-4 text-center text-gray-600">{{ s.paused }}</td>
                <td class="px-6 py-4 text-center text-gray-500">{{ s.cancelled }}</td>
                <td class="px-6 py-4 text-center font-bold">{{ s.total }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="selectedUserId" class="mt-8">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">{{ selectedUserName }} 的项目</h3>
        <div v-if="loadingProjects" class="text-center py-4 text-gray-500">加载中...</div>
        <div v-else-if="userProjects.length === 0" class="text-center py-4 text-gray-500">暂无项目</div>
        <div v-else class="bg-white rounded-lg shadow overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">项目名称</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">角色</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">进度</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">状态</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">超期</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">截止日期</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="p in filteredUserProjects" :key="p.id">
                <td class="px-4 py-3">
                  <router-link :to="`/projects/${p.id}/edit`" class="font-medium text-blue-600 hover:text-blue-800 hover:underline">{{ p.name || '-' }}</router-link>
                  <div class="text-sm text-gray-500 truncate max-w-xs">{{ p.work_content || '' }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-600">{{ p.role || '-' }}</td>
                <td class="px-4 py-3 text-center">
                  <div class="flex items-center justify-center">
                    <div class="w-12 bg-gray-200 rounded-full h-1.5">
                      <div class="bg-blue-600 h-1.5 rounded-full" :style="{ width: (p.progress * 100) + '%' }"></div>
                    </div>
                    <span class="ml-1 text-xs text-gray-600">{{ Math.round(p.progress * 100) }}%</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-center">
                  <span :class="statusClass(p.status)">{{ p.status || '未完成' }}</span>
                </td>
                <td class="px-4 py-3 text-center">
                  <span v-if="p.is_overdue" class="text-red-600 font-bold">是</span>
                  <span v-else class="text-gray-400">否</span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-600">{{ p.end_date || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { projects as projectsApi, users as userApi } from '../api';

const router = useRouter();
const route = useRoute();
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));
const isAdmin = computed(() => user.value.role === 'admin');
const loading = ref(false);
const stats = ref({});
const allStats = ref([]);
const users = ref([]);
const selectedUserId = ref('');
const userProjects = ref([]);
const loadingProjects = ref(false);

const selectedUserName = computed(() => {
  if (!selectedUserId.value) return '全部';
  const u = users.value.find(x => x.id === parseInt(selectedUserId.value));
  return u?.name || '';
});

const filteredUserProjects = computed(() => {
  if (!selectedUserId.value) return [];
  return userProjects.value
    .filter(p => p.user_id === parseInt(selectedUserId.value))
    .sort((a, b) => (a.progress || 0) - (b.progress || 0));
});

const displayedStats = computed(() => {
  if (selectedUserId.value) {
    return allStats.value.filter(s => s.userId === parseInt(selectedUserId.value));
  }
  return allStats.value.filter(s => s.total > 0);
});

const computedStats = computed(() => {
  if (selectedUserId.value) {
    const userStat = allStats.value.find(s => s.userId === parseInt(selectedUserId.value));
    return userStat || { normal: 0, completed: 0, overdue: 0, inProgress: 0, delayed: 0, paused: 0, cancelled: 0, total: 0 };
  }
  const s = { normal: 0, completed: 0, overdue: 0, inProgress: 0, delayed: 0, paused: 0, cancelled: 0, total: 0 };
  allStats.value.forEach(u => {
    s.normal += u.normal || 0;
    s.completed += u.completed || 0;
    s.overdue += u.overdue || 0;
    s.inProgress += u.inProgress || 0;
    s.delayed += u.delayed || 0;
    s.paused += u.paused || 0;
    s.cancelled += u.cancelled || 0;
    s.total += u.total || 0;
  });
  return s;
});

async function fetchStats() {
  loading.value = true;
  try {
    const { data } = await projectsApi.stats();
    console.log('Stats fetched:', data);
    if (Array.isArray(data)) {
      allStats.value = data;
    } else {
      allStats.value = [data];
    }
    if (selectedUserId.value) {
      fetchUserProjects();
    }
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
}

async function fetchUserProjects() {
  if (!selectedUserId.value) {
    userProjects.value = [];
    return;
  }
  loadingProjects.value = true;
  try {
    const { data } = await projectsApi.list(selectedUserId.value);
    userProjects.value = data;
  } catch (err) {
    console.error(err);
  } finally {
    loadingProjects.value = false;
  }
}

async function fetchUsers() {
  try {
    const { data } = await userApi.list();
    console.log('Users fetched:', data);
    users.value = data;
  } catch (err) {
    console.error('Failed to fetch users:', err);
  }
}

function selectUser(s) {
  selectedUserId.value = parseInt(s.userId);
  fetchUserProjects();
}

function clearSelection() {
  selectedUserId.value = '';
  userProjects.value = [];
}

function statusClass(status) {
  const map = {
    '完成': 'px-2 py-0.5 bg-green-100 text-green-800 rounded text-xs',
    '进行中': 'px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs',
    '滞后': 'px-2 py-0.5 bg-orange-100 text-orange-800 rounded text-xs',
    '暂停': 'px-2 py-0.5 bg-gray-100 text-gray-800 rounded text-xs',
    '取消': 'px-2 py-0.5 bg-red-100 text-red-800 rounded text-xs',
    '未完成': 'px-2 py-0.5 bg-yellow-100 text-yellow-800 rounded text-xs'
  };
  return map[status] || 'px-2 py-0.5 bg-gray-100 text-gray-800 rounded text-xs';
}

function handleLogout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  router.push('/login');
}

onMounted(() => {
  if (route.query.userId) {
    selectedUserId.value = route.query.userId;
  }
  fetchStats();
  fetchUsers();
});
</script>
