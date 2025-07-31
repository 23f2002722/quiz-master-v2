<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const handleLogin = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  try {
    console.log("Attempting login API call...");
    const response = await axios.post('/api/login', {
      username: username.value,
      password: password.value,
    });

    console.log("Login API response received:", response.data); 

    const accessToken = response.data.access_token;
    const message = response.data.message;
    const user_role = response.data.user_role; 
    const full_name = response.data.full_name; 

    console.log("Data to store in localStorage:", { accessToken, message, user_role, full_name }); 

    localStorage.setItem('access_token', accessToken); 
    localStorage.setItem('user_role', user_role);
    localStorage.setItem('user_full_name', full_name); 
    successMessage.value = message;

    console.log("Data stored in localStorage. Redirecting to dashboard..."); 

    setTimeout(() => {
      router.push('/dashboard');
    }, 1500);

  } catch (error) {
    console.error("Caught error during login process:", error); 
    if (error.response) {
      errorMessage.value = error.response.data.message || error.response.data || 'An unknown error occurred.';
    } else if (error.request) {
      errorMessage.value = 'No response from server. Check your network or server status.';
    } else {
      errorMessage.value = 'Error: ' + error.message;
    }
  }
};
</script>

<template>
  <div class="container py-5">
    <div class="text-center mb-4">
      <h1 style="color: navy; font-family: 'Montserrat', sans-serif">Welcome to QuizMaster</h1>
      <h4 style="color: #4d4d4d; font-family: 'Lobster', cursive">Challenge Your Mind</h4>
    </div>
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow-lg border-0 rounded-lg">
          <div class="card-body p-4 p-md-5">
            
            <div class="text-center mb-4">
              <h4 class="mb-2">Login</h4>
            </div>

            <form @submit.prevent="handleLogin">
                <div class="mb-4">
                    <div class="input-group">
                        <input type="text"
                               class="form-control"
                               v-model="username"
                               placeholder="Username (email)"
                               required>
                    </div>
                </div>
                <div class="mb-4">
                    <div class="input-group">
                        <input type="password"
                               class="form-control"
                               v-model="password"
                               placeholder="Password"
                               required>
                    </div>
                </div>
                <div class="d-grid mb-4">
                    <button type="submit" class="btn btn-primary btn-lg">
                        <i class="bi bi-box-arrow-in-right me-2"></i>Log In
                    </button>
                </div>
            </form>

            <div class="text-center">
                <div class="mb-3">
                    <span class="text-muted">New to QuizMaster?</span>
                    <div class="mt-2">
                        <router-link to="/register" class="btn btn-outline-primary me-2">
                            <i class="bi bi-mortarboard me-1"></i>Register Yourself
                        </router-link>
                    </div>
                </div>
            </div>

            <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
                {{ errorMessage }}
            </div>
            <div v-if="successMessage" class="alert alert-success mt-3" role="alert">
                {{ successMessage }}
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
h1 {
  color: navy;
  font-family: 'Montserrat', sans-serif;
}
h4 {
  color: #4d4d4d;
  font-family: 'Lobster', cursive;
}
</style>