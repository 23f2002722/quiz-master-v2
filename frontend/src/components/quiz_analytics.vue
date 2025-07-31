<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const props = defineProps({
  quizId: {
    type: [String, Number],
    required: true
  }
});

const quiz_title = ref('');
const quiz_attempts = ref([]);
const total_questions_in_quiz = ref(0);
const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const fetchQuizAnalytics = async () => {
  try {
    const response = await axios.get(`/api/admin/quiz_analytics/${props.quizId}`);
    quiz_title.value = response.data.quiz_title;
    quiz_attempts.value = response.data.quiz_attempts;
    total_questions_in_quiz.value = response.data.total_questions_in_quiz;
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load quiz analytics.';
    console.error('Fetch Quiz Analytics error:', error);
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
  fetchQuizAnalytics();
});
</script>

<template>
<div class="container mt-4">
    <h1 class="text-center">Quiz Analytics</h1>
    <h3 class="text-muted">Quiz ID: {{ quizId }}</h3>
    <h4 class="text-muted">Quiz Type: {{ quiz_title }}</h4>

    <div class="card shadow-sm p-4 mt-3">
        <div class="table-responsive">
            <table class="table table-bordered table-striped">
                <thead class="table-primary">
                    <tr>
                        <th>User ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Score</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="attempt in quiz_attempts" :key="attempt.user_id">
                        <td>{{ attempt.user_id }}</td>
                        <td>
  {{ attempt.full_name }}
</td>
                        <td>{{ attempt.username }}</td>
                        <td>{{ attempt.total_score }}/{{ total_questions_in_quiz }}</td>
                        <td>{{ formatTimestamp(attempt.timestamp) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
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