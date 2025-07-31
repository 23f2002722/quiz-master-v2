<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const username = ref('');
const name = ref('');
const password = ref('');
const confirm_password = ref('');
const dob = ref('');
const qualification = ref('');

const current_date = ref(''); 

const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const setMaxDate = () => {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  current_date.value = `${year}-${month}-${day}`;
};

const registerUser = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!username.value || !name.value || !password.value || !confirm_password.value || !dob.value || !qualification.value) {
    errorMessage.value = 'Please fill in all fields.';
    return;
  }
  
  if (password.value !== confirm_password.value) {
    errorMessage.value = 'Passwords do not match.';
    return;
  }

  try {
    const response = await axios.post('/api/register_user', {
      username: username.value,
      name: name.value,
      password: password.value,
      confirm_password: confirm_password.value,
      dob: dob.value,
      qualification: qualification.value,
    });

    successMessage.value = response.data.message;
    
    username.value = '';
    name.value = '';
    password.value = '';
    confirm_password.value = '';
    dob.value = '';
    qualification.value = '';

    setTimeout(() => {
      router.push('/login'); 
    }, 1500);

  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.message || 'An error occurred during registration.';
    } else if (error.request) {
      errorMessage.value = 'No response from server. Check your network.';
    } else {
      errorMessage.value = 'Error: ' + error.message;
    }
    console.error("Registration error:", error);
  }
};

onMounted(() => {
  setMaxDate();
});
</script>

<template>
<div class="container py-5">
  <div class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
      <div class="card shadow-lg border-0 rounded-lg">
        <div class="card-body p-4 p-md-5">
          
          <div class="text-center mb-4">
            <h1 class="display-5 text-primary fw-bold mb-2">Welcome</h1>
            <h4 class="mb-2">QuizMaster - Challenge Your Mind</h4>
            <p class="text-muted">Registration</p>
          </div>

          <form @submit.prevent="registerUser" class="needs-validation" novalidate>

            <div class="row g-3">
              <div class="col-md-6">
                <div class="form-floating mb-3">
                  <input type="email" class="form-control" id="username" v-model="username"
                    placeholder="Username (email)" required>
                  <label for="username">Username (email)</label>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-floating mb-3">
                  <input type="text" class="form-control" id="name" v-model="name" placeholder="Full Name" required>
                  <label for="name">Full Name</label>
                </div>
              </div>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <div class="form-floating mb-3">
                  <input type="password" class="form-control" id="password" v-model="password" placeholder="Password"
                    required>
                  <label for="password">Password</label>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-floating mb-3">
                  <input type="password" class="form-control" id="confirm_password" v-model="confirm_password"
                    placeholder="Confirm Password" required>
                  <label for="confirm_password">Confirm Password</label>
                </div>
              </div>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <label for="date" class="form-label">
                  <i class="bi bi-calendar-event me-2"></i>Date of birth
                </label>
                <div class="input-group">
                  <input type="date" class="form-control" id="date" v-model="dob" required :max="current_date" />
                </div>
                <div class="invalid-feedback">
                  <i class="bi bi-exclamation-circle me-1"></i>
                  Please select a valid date of birth.
                </div>
              </div>

              <div class="col-md-6">
                <label for="qualification" class="form-label">
                  <i class="bi bi-calendar-event me-2"></i>Qualification</label>
                <select v-model="qualification" class="form-select" id="qualification" required>
                  <option value="" selected disabled>Please select your qualification</option>
                  <option value="High School">High School</option>
                  <option value="Entermediate">Entermediate</option>
                  <option value="Graduation">Graduation</option>
                  <option value="Post Graduation">Post Graduation</option>
                </select>

              </div>
            </div><br>


            <div class="d-grid gap-3">
              <button type="submit" class="btn btn-primary btn-lg">
                <i class="bi bi-person-plus me-2"></i>Register
              </button>
              <router-link to="/login" class="btn btn-outline-secondary">
                <i class="bi bi-arrow-left me-2"></i>Back to Login
              </router-link>
            </div>
          </form>

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
</style>