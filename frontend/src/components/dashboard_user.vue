<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const user_full_name = ref('');
const quizzes = ref([]);
const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const fetchDashboardData = async () => {
  try {
    const response = await axios.get('/api/dashboard');
    user_full_name.value = response.data.user_details.full_name;
    quizzes.value = response.data.quizzes;
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load dashboard data.';
    console.error('Fetch Dashboard error:', error);
  }
};

const formatQuizDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

onMounted(() => {
  fetchDashboardData();
});
</script>

<template>
<div class="container mt-4">
    <br><h1 class="mb-4 text-center">Welcome, {{ user_full_name }}</h1><br>
    
    <section>
        <h2 class="mb-3">Upcoming Quizzes</h2>
    
        <template v-if="quizzes && quizzes.length > 0">
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-primary">
                    <tr>
                        <th>Quiz</th>
                        <th>No. of questions</th>
                        <th>Date</th>
                        <th>Duration</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <template v-for="quiz_item in quizzes" :key="quiz_item.id">
                    <tr v-if="quiz_item.questions_count > 0">
                        <td>{{ quiz_item.type }} ({{ quiz_item.chapter_name }}) </td>
                        <td>{{ quiz_item.questions_count }}</td>
                        <td>{{ formatQuizDate(quiz_item.date_of_quiz) }}</td>
                        <td>{{ quiz_item.time_duration }} minutes </td>
                        <td>
                            <button type="button" class="btn btn-info btn-sm" data-bs-toggle="modal" :data-bs-target="'#quizModal' + quiz_item.id">
                                View
                            </button>
                            <router-link :to="{ name: 'Quiz', params: { quizId: quiz_item.id } }" class="btn btn-primary btn-sm ms-2">Start Quiz</router-link>
                        </td>
                    </tr>
                    
                    <div class="modal fade" :id="'quizModal' + quiz_item.id" tabindex="-1" aria-labelledby="quizModalLabel" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="quizModalLabel">View the Quiz</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <p><strong>ID:</strong> {{ quiz_item.id }}</p>
                                    <p><strong>Subject:</strong> <span class="badge bg-success">{{ quiz_item.subject_name }}</span></p>
                                    <p><strong>Description:</strong> {{ quiz_item.chapter_name }}</p>
                                    <p><strong>Chapter:</strong> <span class="badge bg-primary">{{ quiz_item.chapter_name }}</span></p>
                                    <p><strong>Description:</strong> {{ quiz_item.chapter_description }}</p>
                                    <p><strong>Number of Questions:</strong> {{ quiz_item.questions_count }}</p>
                                    <p><strong>Date:</strong> {{ formatQuizDate(quiz_item.date_of_quiz) }}</p>
                                    <p><strong>Duration (minutes):</strong> {{ quiz_item.time_duration }}</p>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    </template>
                </tbody>
            </table>
        </div>
        </template>
        <template v-else>
        <p class="alert alert-warning">No quiz yet.</p>
        </template>
    </section>

    <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
        {{ errorMessage }}
    </div>
    <div v-if="successMessage" class="alert alert-success mt-3" role="alert">
        {{ successMessage }}
    </div>
</div>
</template>

<style scoped>
</style>