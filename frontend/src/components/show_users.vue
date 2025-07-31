<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const users = ref([]);
const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const fetchUsers = async () => {
  try {
    const response = await axios.get('/api/admin/show_users');
    console.log("Fetched users:", response.data.users);
    users.value = response.data.users || [];
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load users.';
    console.error('Fetch Users error:', error);
  }
};

const deleteUser = async (userId) => {
  if (!confirm('Are you sure you want to delete this user?')) return;

  try {
    const response = await axios.delete(`/api/admin/delete_user/${userId}`);
    successMessage.value = response.data.message;
    users.value = users.value.filter(user => user.id !== userId);
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to delete user.';
  }
};

onMounted(() => {
  fetchUsers();
});
</script>

<template>
  <div class="container mt-4">
    <section>
      <h2 class="mb-4 text-center">Users</h2>

      <div v-if="users.length > 0" class="list-group">
        <div
          v-for="user_item in users"
          :key="user_item.id"
          class="list-group-item list-group-item-action p-3 mb-3 shadow-sm rounded"
        >
          <h5 class="mb-1">
            <strong>Name:</strong>
            <span class="text-primary">
  {{ user_item.full_name || user_item.name || 'Unnamed User' }}
</span>
          </h5>
          <p class="mb-1"><strong>Email:</strong> {{ user_item.username || user_item.email || 'N/A' }}</p>
          <p class="mb-1"><strong>Qualification:</strong> {{ user_item.qualification || 'N/A' }}</p>
          <p class="mb-3"><strong>DOB:</strong> {{ user_item.dob || 'N/A' }}</p>
          <button @click="deleteUser(user_item.id)" class="btn btn-danger btn-sm">
            Delete
          </button>
        </div>
      </div>

      <p v-else class="text-muted text-center">No Users Found.</p>
    </section>

    <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
      {{ errorMessage }}
    </div>
    <div v-if="successMessage" class="alert alert-success mt-3" role="alert">
      {{ successMessage }}
    </div>
  </div>
</template>

<style scoped>
</style>
