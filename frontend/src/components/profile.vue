<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const user_full_name_display = ref('');
const name = ref('');
const current_password = ref('');
const new_password = ref('');
const confirm_password = ref('');
const email = ref('');

const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const fetchProfileData = async () => {
  try {
    const response = await axios.get('/api/profile');
    user_full_name_display.value = response.data.full_name;
    name.value = response.data.full_name;
    email.value = response.data.username; 
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load profile data.';
    console.error('Fetch Profile error:', error);
  }
};

const updateProfile = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!current_password.value || !new_password.value || !confirm_password.value) {
    errorMessage.value = 'Please fill out all the required password fields for update.';
    return;
  }

  try {
    const response = await axios.put('/api/profile', {
      name: name.value,
      current_password: current_password.value,
      new_password: new_password.value,
      confirm_password: confirm_password.value,
      email: email.value,
    });

    successMessage.value = response.data.message;
    
    current_password.value = '';
    new_password.value = '';
    confirm_password.value = '';

    user_full_name_display.value = name.value;

  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.message || 'An error occurred while updating the profile.';
    } else if (error.request) {
      errorMessage.value = 'No response from server. Check your network.';
    } else {
      errorMessage.value = 'Error: ' + error.message;
    }
    console.error('Update Profile error:', error);
  }
};

onMounted(() => {
  fetchProfileData();
});
</script>

<template>
<div class="heading">
    <h2 class="display-4">
        Hello
        <span class="text-muted">@{{ user_full_name_display }}</span>
    </h2>
</div>

<form @submit.prevent="updateProfile" class="form">
    <div class="form-group">
        <label for="name" class="form-label">Name:</label>
        <input
            type="text"
            v-model="name"
            id="name"
            class="form-control"
        />
    </div>
    <div class="form-group">
        <label for="current_password" class="form-label">Current Password</label>
        <input
            type="password"
            v-model="current_password"
            id="current_password"
            class="form-control"
            required
        />
    </div>
    <div class="form-group">
        <label for="new_password" class="form-label">New Password:</label>
        <input
            type="password"
            v-model="new_password"
            id="new_password"
            class="form-control"
            required
        />
    </div>
    <div class="form-group">
        <label for="confirm_password" class="form-label">Confirm New Password:</label>
        <input
            type="password"
            v-model="confirm_password"
            id="confirm_password"
            class="form-control"
            required
        />
    </div>
    <div class="form-group">
        <label for="email" class="form-label">Username (Email)</label>
        <input
            type="text"
            v-model="email"
            id="email"
            class="form-control"
        />
    </div>
    <div class="buttons d-flex justify-content-center align-items-center">
        <div class="form-group m-3">
            <input type="submit" value="Update" class="btn btn-primary" />
        </div>
    </div>
</form>

<div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
    {{ errorMessage }}
</div>
<div v-if="successMessage" class="alert alert-success mt-3" role="alert">
    {{ successMessage }}
</div>
</template>

<style scoped>
.heading {
  margin-top: 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.form-group {
  margin-bottom: 1rem;
}

.form {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #dee2e6;
  border-radius: 5px;
  background-color: #fff;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.buttons {
  margin-top: 1.5rem;
}
</style>