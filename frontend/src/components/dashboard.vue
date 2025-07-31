<script setup>
import { ref, onMounted } from 'vue';
import DashboardUser from './dashboard_user.vue'; 
import DashboardAdmin from './dashboard_admin.vue'; 

const userRole = ref('');

onMounted(() => {
  userRole.value = localStorage.getItem('user_role');
});
</script>

<template>
  <div>
    <template v-if="userRole === 'admin'">
      <DashboardAdmin />
    </template>
    <template v-else-if="userRole === 'user'">
      <DashboardUser />
    </template>
    <template v-else>
      <p>Loading dashboard content or unauthorized access...</p>
    </template>
  </div>
</template>
