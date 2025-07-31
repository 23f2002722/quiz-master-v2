<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const scores = ref([]);
const errorMessage = ref('');
const successMessage = ref('');

const fetchScores = async () => {
  try {
    const response = await axios.get('/api/user/scores');
    scores.value = response.data.scores;
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load quiz scores.';
    console.error('Fetch Scores error:', error);
  }
};

const formatTimestamp = (timestampString) => {
  if (!timestampString) return '';
  const date = new Date(timestampString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

onMounted(() => {
  fetchScores();
});
</script>

<template>
<div class="container mt-4">
    <h2 class="mb-3">Quiz Scores</h2>
    <div class="table-responsive">
        <table class="table table-striped table-hover">
            <thead class="table-primary">
                <tr>
                    <th>Quiz ID</th>
                    <th>Quiz Type</th>
                    <th>Chapter</th>
                    <th>Subject</th>
                    <th>Date Attempted</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
                <template v-if="scores.length > 0">
                    <tr v-for="score_item in scores" :key="score_item.score_id">
                        <td>{{ score_item.quiz_id }}</td>
                        <td>{{ score_item.quiz_type }}</td>
                        <td>{{ score_item.chapter_name }}</td>
                        <td>{{ score_item.subject_name }}</td>
                        <td>{{ formatTimestamp(score_item.timestamp) }}</td>
                        <td>{{ score_item.total_score }}/{{ score_item.total_questions }}</td>
                    </tr>
                </template>
                <template v-else>
                    <tr>
                        <td colspan="6" class="text-center alert alert-warning">Not attempted any quizzes yet.</td>
                    </tr>
                </template>
            </tbody>
        </table>
    </div>
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