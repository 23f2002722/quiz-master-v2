<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const chapter_id = ref('');
const type = ref('');
const date = ref('');
const duration = ref('');
const remarks = ref('');

const chapters = ref([]); 
const current_date = ref(''); 

const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const fetchChapters = async () => {
  try {
    const response = await axios.get('/api/admin/chapters_list_all'); 
    chapters.value = response.data.chapters;
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load chapters.';
    console.error('Fetch Chapters error:', error);
  }
};

const setMinDate = () => {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  current_date.value = `${year}-${month}-${day}`;
};

const addQuiz = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!chapter_id.value || !date.value || !type.value || !duration.value) {
    errorMessage.value = 'All fields are required to create a quiz.';
    return;
  }

  try {
    const parsedDuration = parseInt(duration.value);
    if (isNaN(parsedDuration) || parsedDuration <= 0) {
      errorMessage.value = 'Invalid duration. Please enter a valid number greater than zero.';
      return;
    }

    const response = await axios.post('/api/admin/add_quiz', {
      type: type.value,
      chapter_id: chapter_id.value,
      date_of_quiz: date.value, 
      duration: parsedDuration,
      remarks: remarks.value,
    });

    successMessage.value = response.data.message;
    
    // Clear form fields after successful submission
    chapter_id.value = '';
    type.value = '';
    date.value = '';
    duration.value = '';
    remarks.value = '';

    setTimeout(() => {
      router.push('/admin/quizzes'); 
    }, 1500);

  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.message || 'An error occurred while adding the quiz.';
    } else if (error.request) {
      errorMessage.value = 'No response from server. Check your network.';
    } else {
      errorMessage.value = 'Error: ' + error.message;
    }
    console.error("Add Quiz error:", error);
  }
};

onMounted(() => {
  fetchChapters();
  setMinDate();
});
</script>

<template>
<div class="container mt-4">
    <h2 class="text-center">New Quiz</h2>
    <div class="card p-4 shadow-sm">
        <form @submit.prevent="addQuiz">
            <div class="mb-3">
                <label for="chapter" class="form-label">Chapter ID</label>
                <select id="chapter" v-model="chapter_id" class="form-select" required>
                    <option value="">Select Chapter</option>
                    <option v-for="ch in chapters" :key="ch.id" :value="ch.id">
                        {{ ch.id }} [{{ ch.name }}]
                    </option>
                </select>
            </div>

            <div class="mb-3">
                <label for="type" class="form-label">Type</label>
                <input type="text" id="type" v-model="type" class="form-control" required>
            </div>

            <div class="mb-3">
                <label for="date" class="form-label">Date</label>
                <input type="date" id="date" v-model="date" :min="current_date" class="form-control" required>
            </div>

            <div class="mb-3">
                <label for="duration" class="form-label">Duration (in minutes)</label>
                <input type="number" id="duration" v-model="duration" class="form-control" required>
            </div>

            <div class="mb-3">
                <label for="remarks" class="form-label">Remarks</label>
                <input type="text" id="remarks" v-model="remarks" class="form-control">
            </div>

            <div class="d-flex justify-content-between">
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
</template>

<style scoped>
</style>