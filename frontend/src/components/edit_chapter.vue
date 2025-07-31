<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const props = defineProps({
  chapterId: {
    type: [String, Number],
    required: true
  }
});

const name = ref('');
const description = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const fetchChapterDetails = async () => {
  try {
    const response = await axios.get(`/api/admin/chapters/${props.chapterId}`);
    name.value = response.data.name;
    description.value = response.data.description;
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load chapter details.';
    console.error('Fetch Chapter Details error:', error);
  }
};

const saveChanges = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!name.value) {
    errorMessage.value = 'Chapter name cannot be empty.';
    return;
  }

  try {
    const response = await axios.put(`/api/admin/edit_chapter/${props.chapterId}`, {
      name: name.value,
      description: description.value,
    });

    successMessage.value = response.data.message;
    
    setTimeout(() => {
      router.push('/dashboard');
    }, 1500);

  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.message || 'An error occurred while saving changes.';
    } else if (error.request) {
      errorMessage.value = 'No response from server. Check your network.';
    } else {
      errorMessage.value = 'Error: ' + error.message;
    }
    console.error("Edit Chapter error:", error);
  }
};

onMounted(() => {
  fetchChapterDetails();
});
</script>

<template>
<div class="container flex-grow-1 d-flex flex-column mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <h2 class="text-center text-warning mb-4">Edit Chapter</h2>
            <div class="card shadow-lg">
                <div class="card-body">
                    <form @submit.prevent="saveChanges">
                        <div class="mb-3">
                            <label for="name" class="form-label">Chapter Name:</label>
                            <input type="text"
                                   class="form-control"
                                   id="name"
                                   v-model="name"
                                   required>
                        </div>

                        <div class="mb-3">
                            <label for="description" class="form-label">Chapter Description:</label>
                            <textarea class="form-control"
                                      id="description"
                                      v-model="description"
                                      rows="3"
                                      required></textarea>
                        </div>

                        <div class="d-flex justify-content-between">
                            <router-link to="/dashboard" class="btn btn-secondary">Cancel</router-link>
                            <button type="submit" class="btn btn-primary">Save Changes</button>
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