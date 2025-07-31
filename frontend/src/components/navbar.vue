<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const isLoggedIn = computed(() => {
  return localStorage.getItem('access_token') ? true : false;
});

const userRole = computed(() => {
  return localStorage.getItem('user_role') || '';
});

const usernameDisplay = computed(() => {
  const role = localStorage.getItem('user_role');
  return role ? role.charAt(0).toUpperCase() + role.slice(1) : '';
});


const logout = async () => {
  try {
    await axios.post('/api/logout'); 
  } catch (error) {
    console.error("Logout API call failed:", error);
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    router.push('/login');
  }
};
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/dashboard">Quiz Master</router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <template v-if="isLoggedIn">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">Home</router-link>
            </li>
            <template v-if="userRole === 'user'">
              <li class="nav-item">
                <router-link class="nav-link" to="/dashboard/scores">Scores</router-link>
              </li>
            </template>
            <template v-else-if="userRole === 'admin'">
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/quizzes">Quiz</router-link>
              </li>
            </template>
            <template v-if="userRole === 'user'">
              <li class="nav-item">
                <router-link class="nav-link" to="/summary">Summary</router-link>
              </li>
            </template>
            <template v-else-if="userRole === 'admin'">
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/summary">Summary</router-link>
              </li>
            </template>
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="logout">Logout</a>
            </li>
          </template>
        </ul>
        
        <template v-if="isLoggedIn">
          <div class="d-flex align-items-center">
            <router-link class="nav-link me-3" to="/search">
              <button class="btn btn-outline-primary">Search</button>
            </router-link>
            <span class="navbar-text">
              Welcome, <router-link class="fw-bold text-decoration-none" to="/profile">{{ usernameDisplay }}</router-link>
            </span>
          </div>
        </template>
      </div>
    </div>
  </nav>
</template>

