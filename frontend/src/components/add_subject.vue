<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const name = ref('');
const description = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const addSubject = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!name.value || !description.value) {
    errorMessage.value = 'Name and Description are required!';
    return;
  }

  try {
    const response = await axios.post('/api/admin/add_subject', {
      name: name.value,
      description: description.value,
    });

    successMessage.value = response.data.message;
    
    name.value = '';
    description.value = '';

    setTimeout(() => {
      router.push('/dashboard');
    }, 1500);

  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.message || 'An error occurred while adding the subject.';
    } else if (error.request) {
      errorMessage.value = 'No response from server. Check your network.';
    } else {
      errorMessage.value = 'Error: ' + error.message;
    }
    console.error("Add Subject error:", error);
  }
};
</script>

<template>
<div class="container mt-4">
    <h2 class="text-center text-warning mb-4">New Subject</h2>
    
    <div class="row">
        <div class="col-md-6 mx-auto">
            <div class="card shadow-sm rounded p-4">
                <form @submit.prevent="addSubject">
                    <div class="mb-3">
                        <label for="subjectName" class="form-label">Name:</label>
                        <input type="text"
                               class="form-control"
                               id="subjectName"
                               v-model="name"
                               required>
                    </div>
                    <div class="mb-3">
                        <label for="subjectDescription" class="form-label">Description:</label>
                        <textarea class="form-control"
                                  id="subjectDescription"
                                  v-model="description"
                                  rows="3"
                                  required></textarea>
                    </div>
                    <div class="d-flex justify-content-end gap-2">
                        <a @click.prevent="router.go(-1)" class="btn btn-secondary">Cancel</a>
                        <button type="submit" class="btn btn-primary">Save</button>
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
</template>

<style scoped>
</style>