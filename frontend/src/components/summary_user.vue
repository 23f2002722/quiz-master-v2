<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const user_full_name = ref('');
const subject_wise_attempts = ref([]);
const month_wise_attempts = ref([]);
const errorMessage = ref('');
const successMessage = ref('');

const fetchSummaryData = async () => {
  try {
    const response = await axios.get('/api/summary');
    user_full_name.value = response.data.user_details.full_name;
    subject_wise_attempts.value = response.data.subject_wise_attempts;
    month_wise_attempts.value = response.data.month_wise_attempts;
    
    renderCharts();
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load summary data.';
    console.error('Fetch Summary error:', error);
  }
};

const renderCharts = () => {
  const subjectAttemptsCtx = document.getElementById('subjectAttemptsChart').getContext('2d');
  new Chart(subjectAttemptsCtx, {
    type: 'bar',
    data: {
      labels: subject_wise_attempts.value.map(s => s.subject_name),
      datasets: [{
        label: 'Number of Attempts',
        data: subject_wise_attempts.value.map(s => s.attempt_count),
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

  const monthAttemptsCtx = document.getElementById('monthAttemptsChart').getContext('2d');
  new Chart(monthAttemptsCtx, {
    type: 'doughnut',
    data: {
      labels: month_wise_attempts.value.map(m => m.month),
      datasets: [{
        label: 'Number of Attempts',
        data: month_wise_attempts.value.map(m => m.attempt_count),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)'
        ],
        borderColor: 'rgba(255, 255, 255, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
    }
  });
};

onMounted(() => {
  fetchSummaryData();
});
</script>

<template>
<div class="container mt-4">
    <h1 class="text-center mb-4">Welcome, {{ user_full_name }}</h1>
    
    <div class="row align-items-center">
        <div class="col-md-6 d-flex flex-column align-items-center">
            <h3 class="text-center">Subject-wise Number of Attempts</h3>
            <div style="width: 300px; height: 300px;">
                <canvas id="subjectAttemptsChart"></canvas>
            </div>
        </div>
        <div class="col-md-6 d-flex flex-column align-items-center">
            <h3 class="text-center">Month-wise Number of Quizzes Attempted</h3>
            <div style="width: 300px; height: 300px;">
                <canvas id="monthAttemptsChart"></canvas>
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