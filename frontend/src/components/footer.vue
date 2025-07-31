<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const admin_email = ref('loading...'); 

onMounted(async () => {
  try {
    const response = await axios.get('/api/admin_contact');
    admin_email.value = response.data.admin_email;
  } catch (error) {
    console.error("Error fetching admin email:", error);
    admin_email.value = 'error@quizmaster.com'; 
  }
});
</script>

<template>
  <footer class="text-center mt-5 p-3 bg-light">
    <p>For any queries or issues, contact: {{ admin_email }}</p>
    <p>&copy; 2025 QuizMaster. All rights reserved.</p>
  </footer>
</template>
