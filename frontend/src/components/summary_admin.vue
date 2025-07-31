<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const subject_wise_top_scores = ref([]);
const subject_wise_user_attempts = ref([]);
const errorMessage = ref('');
const successMessage = ref('');

const fetchSummaryData = async () => {
  try {
    const response = await axios.get('/api/summary');
    subject_wise_top_scores.value = response.data.subject_wise_top_scores;
    subject_wise_user_attempts.value = response.data.subject_wise_user_attempts;
    
    renderCharts();
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load summary data.';
    console.error('Fetch Summary error:', error);
  }
};

const renderCharts = () => {
  const topScoresCtx = document.getElementById('topScoresChart').getContext('2d');
  new Chart(topScoresCtx, {
    type: 'bar',
    data: {
      labels: subject_wise_top_scores.value.map(s => s.subject_name),
      datasets: [{
        label: 'Top Score',
        data: subject_wise_top_scores.value.map(s => s.top_score),
        backgroundColor: ['rgba(54, 162, 235, 0.6)', 'rgba(255, 99, 132, 0.6)', 'rgba(255, 206, 86, 0.6)'],
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });

  const userAttemptsCtx = document.getElementById('userAttemptsChart').getContext('2d');
  new Chart(userAttemptsCtx, {
    type: 'doughnut',
    data: {
      labels: subject_wise_user_attempts.value.map(s => s.subject_name),
      datasets: [{
        label: 'Number of Users Attempted',
        data: subject_wise_user_attempts.value.map(s => s.user_count),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)'
        ],
        borderColor: 'rgba(255, 255, 255, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });
};

onMounted(() => {
  fetchSummaryData();
});
</script>

<template>
<div class="container mt-4">
    <h1 class="text-center mb-4">Summary Charts</h1>
    
    <div class="row align-items-center">
        <div class="col-md-6 d-flex flex-column align-items-center">
            <h3 class="text-center">Subject-wise Top Scores</h3>
            <div style="width: 300px; height: 300px;">
                <canvas id="topScoresChart"></canvas>
            </div>
        </div>
        <div class="col-md-6 d-flex flex-column align-items-center">
            <h3 class="text-center">Subject-wise User Attempts</h3>
            <div style="width: 300px; height: 300px;">
                <canvas id="userAttemptsChart"></canvas>
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
</template>

<style scoped>
</style>