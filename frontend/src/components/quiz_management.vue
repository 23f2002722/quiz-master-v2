<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';

const quizzes = ref([]);
const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();
const route = useRoute();

const fetchQuizManagementData = async () => {
  try {
    const chapterId = route.params.chapterId;

    let response;
    if (chapterId) {
      response = await axios.get(`/api/admin/quiz/chapter/${chapterId}`);
    } else {
      response = await axios.get('/api/admin/quiz_management');
    }

    quizzes.value = response.data.quizzes;
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load quiz management data.';
    console.error('Fetch Quiz Management error:', error);
  }
};

const formatQuizDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}-${month}-${year}`;
};

const deleteQuestion = async (questionId) => {
  if (!confirm('Are you sure you want to delete this question?')) return;

  errorMessage.value = '';
  successMessage.value = '';
  try {
    const response = await axios.delete(`/api/admin/delete_question/${questionId}`);
    successMessage.value = response.data.message;
    fetchQuizManagementData();
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to delete question.';
    console.error('Delete Question error:', error);
  }
};

const deleteQuiz = async (quizId) => {
  if (!confirm('Are you sure you want to delete this quiz?')) return;

  errorMessage.value = '';
  successMessage.value = '';
  try {
    const response = await axios.delete(`/api/admin/delete_quiz/${quizId}`);
    successMessage.value = response.data.message;
    quizzes.value = quizzes.value.filter(quiz => quiz.id !== quizId);
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to delete quiz.';
    console.error('Delete Quiz error:', error);
  }
};

onMounted(fetchQuizManagementData);
watch(() => route.params.chapterId, fetchQuizManagementData);
</script>

<template>
  <div class="container mt-4">
    <h2 class="mb-4">Quiz Management</h2>
    <div class="row">
      <div class="col-md-6 mb-4" v-for="quiz_item in quizzes" :key="quiz_item.id">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title">
              {{ quiz_item.type }}
              (<a href="#" class="text-decoration-none" data-bs-toggle="modal" :data-bs-target="'#modal' + quiz_item.chapter_id">
                {{ quiz_item.chapter_name }}
              </a>)
            </h5>

            <!-- Modal for Chapter Description -->
            <div class="modal fade" :id="'modal' + quiz_item.chapter_id" tabindex="-1" :aria-labelledby="'modalLabel' + quiz_item.chapter_id" aria-hidden="true">
              <div class="modal-dialog">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title" :id="'modalLabel' + quiz_item.chapter_id">{{ quiz_item.chapter_name }}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                  </div>
                  <div class="modal-body">
                    <p>{{ quiz_item.chapter_description }}</p>
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                  </div>
                </div>
              </div>
            </div>

            <h6 class="text-muted">{{ quiz_item.subject_name }}</h6>
            <p><strong>Date:</strong> {{ formatQuizDate(quiz_item.date_of_quiz) }}</p>
            <p class="mb-1"><strong>Duration:</strong> {{ quiz_item.time_duration }}</p>
            <p class="mb-3"><strong>Remarks:</strong> {{ quiz_item.remarks }}</p>
            <p class="mb-3"><strong>No. of questions:</strong> {{ quiz_item.questions_count }}</p>

            <table class="table table-bordered table-sm">
              <thead class="thead-light">
                <tr>
                  <th>ID</th>
                  <th>Question Statement</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="question in quiz_item.questions" :key="question.id">
                  <td>{{ question.id }}</td>
                  <td style="width:70%;">{{ question.question_statement.substring(0, 50) }}{{ question.question_statement.length > 50 ? '...' : '' }}</td>
                  <td>
                    <router-link :to="{ name: 'AdminEditQuestion', params: { questionId: question.id } }" class="btn btn-primary btn-sm">Edit</router-link>
                    <button @click="deleteQuestion(question.id)" class="btn btn-danger btn-sm ms-1">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>

            <div class="d-flex justify-content-between">
              <router-link :to="{ name: 'AdminAddQuestion', params: { quizId: quiz_item.id } }" class="btn btn-success btn-sm">Add Question</router-link>
              <router-link :to="{ name: 'AdminQuizAnalytics', params: { quizId: quiz_item.id } }" class="btn btn-info btn-sm">View Analytics</router-link>
              <button @click="deleteQuiz(quiz_item.id)" class="btn btn-danger btn-sm">Delete Quiz</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <router-link to="/admin/quizzes/add" class="btn btn-success mt-3">+ New Quiz</router-link>

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
