<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const props = defineProps({
  subjectId: {
    type: [String, Number],
    required: true
  }
});

const name = ref('');
const description = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const addChapter = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!name.value || !description.value) {
    errorMessage.value = 'Name and Description are required!';
    return;
  }

  try {
    const response = await axios.post(`/api/admin/add_chapter/${props.subjectId}`, {
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
      errorMessage.value = error.response.data.message || 'An error occurred while adding the chapter.';
    } else if (error.request) {
      errorMessage.value = 'No response from server. Check your network.';
    } else {
      errorMessage.value = 'Error: ' + error.message;
    }
    console.error("Add Chapter error:", error);
  }
};
</script>

<template>
<br>
<div class="container flex-grow-1 d-flex flex-column">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <h2 class="text-center text-warning mb-4">New Chapter</h2>
            <div class="card shadow-lg">
                <div class="card-body">
                    <form @submit.prevent="addChapter">
                        <div class="mb-3">
                            <label for="chapterName" class="form-label">Name:</label>
                            <input type="text"
                                   class="form-control"
                                   id="chapterName"
                                   v-model="name"
                                   required>
                        </div>
                        <div class="mb-3">
                            <label for="chapterDescription" class="form-label">Description:</label>
                            <textarea class="form-control"
                                      id="chapterDescription"
                                      v-model="description"
                                      rows="3"
                                      required></textarea>
                        </div>
                        <div class="d-flex justify-content-between">
                            <router-link to="/dashboard" class="btn btn-secondary">Cancel</router-link>
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
</div>
</template>

<style scoped>
</style>