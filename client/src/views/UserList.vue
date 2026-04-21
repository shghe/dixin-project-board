<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center space-x-4">
            <router-link to="/" class="text-gray-600 hover:text-gray-900">首页</router-link>
            <span class="text-gray-400">/</span>
            <span class="text-gray-800 font-medium">用户管理</span>
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
        <h2 class="text-2xl font-bold text-gray-800">用户管理</h2>
        <button @click="showAddModal = true" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          新增用户
        </button>
      </div>

      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户名</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">姓名</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">角色</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-gray-900">{{ u.username }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-600">{{ u.name }}</td>
              <td class="px-6 py-4 text-center">
                <span :class="u.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'" class="px-2 py-1 rounded-full text-xs">
                  {{ u.role === 'admin' ? '管理员' : '成员' }}
                </span>
              </td>
              <td class="px-6 py-4 text-center space-x-2">
                <button @click="editUser(u)" class="text-blue-600 hover:text-blue-800">编辑</button>
                <button v-if="u.id !== user.id" @click="handleDelete(u.id)" class="text-red-600 hover:text-red-800">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">{{ editingUser ? '编辑用户' : '新增用户' }}</h3>
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input v-model="form.username" type="text" required :disabled="editingUser" class="w-full px-4 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">姓名</label>
            <input v-model="form.name" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码 {{ editingUser ? '(留空则不修改)' : '' }}</label>
            <input v-model="form.password" type="password" :required="!editingUser" class="w-full px-4 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">角色</label>
            <select v-model="form.role" class="w-full px-4 py-2 border border-gray-300 rounded-lg">
              <option value="member">成员</option>
              <option value="admin">管理员</option>
            </select>
          </div>
          <div class="flex justify-end space-x-2">
            <button type="button" @click="closeModal" class="px-4 py-2 text-gray-600">取消</button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { users as userApi } from '../api';

const router = useRouter();
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));
const users = ref([]);
const showAddModal = ref(false);
const editingUser = ref(null);
const form = ref({ username: '', name: '', password: '', role: 'member' });

async function fetchUsers() {
  try {
    const { data } = await userApi.list();
    users.value = data;
  } catch (err) {
    console.error(err);
  }
}

function editUser(u) {
  editingUser.value = u;
  form.value = { username: u.username, name: u.name, password: '', role: u.role };
  showAddModal.value = true;
}

function closeModal() {
  showAddModal.value = false;
  editingUser.value = null;
  form.value = { username: '', name: '', password: '', role: 'member' };
}

async function handleSubmit() {
  try {
    if (editingUser.value) {
      await userApi.update(editingUser.value.id, form.value);
    } else {
      await userApi.create(form.value);
    }
    closeModal();
    fetchUsers();
  } catch (err) {
    alert(err.response?.data?.error || '操作失败');
  }
}

async function handleDelete(id) {
  if (!confirm('确定要删除这个用户吗？')) return;
  try {
    await userApi.delete(id);
    fetchUsers();
  } catch (err) {
    alert(err.response?.data?.error || '删除失败');
  }
}

function handleLogout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  router.push('/login');
}

onMounted(() => {
  fetchUsers();
});
</script>
