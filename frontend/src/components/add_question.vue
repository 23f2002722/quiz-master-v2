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

const chapterName = ref('');
const quizType = ref('');
const questionCount = ref(1);

const question_statement = ref('');
const option1 = ref('');
const option2 = ref('');
const option3 = ref('');
const option4 = ref('');
const correct_option = ref('1'); 
const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const fetchQuizDetails = async () => {
  try {
    const response = await axios.get(`/api/admin/quiz_details_for_question_add/${props.quizId}`);
    chapterName.value = response.data.chapter_name;
    quizType.value = response.data.quiz_type;
    questionCount.value = response.data.question_count;
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load quiz details.';
    console.error("Fetch quiz details error:", error);
  }
};

const addQuestion = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!question_statement.value || !option1.value || !option2.value || !option3.value || !option4.value || !correct_option.value) {
    errorMessage.value = 'All fields are required!';
    return;
  }

  try {
    const response = await axios.post(`/api/admin/add_question/${props.quizId}`, {
      question_statement: question_statement.value,
      option1: option1.value,
      option2: option2.value,
      option3: option3.value,
      option4: option4.value,
      correct_option: correct_option.value,
    });

    successMessage.value = response.data.message;

    question_statement.value = '';
    option1.value = '';
    option2.value = '';
    option3.value = '';
    option4.value = '';
    correct_option.value = '1';

    questionCount.value++; 

  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.message || 'An error occurred while adding the question.';
    } else if (error.request) {
      errorMessage.value = 'No response from server. Check your network.';
    } else {
      errorMessage.value = 'Error: ' + error.message;
    }
    console.error("Add Question error:", error);
  }
};

onMounted(() => {
  fetchQuizDetails();
});
</script>

<template>
<div class="container flex-grow-1 d-flex flex-column mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <h2 class="text-center text-warning mb-4">New Question</h2>

            <div class="card shadow-lg">
                <div class="card-body">
                    <form @submit.prevent="addQuestion">
                        <div class="mb-3">
                            <h5><strong>Chapter Name:</strong> {{ chapterName }}</h5>
                            <h5><strong>Quiz Type:</strong> {{ quizType }}</h5>
                            <h3 class="mt-3"><strong>Q.No. {{ questionCount }}</strong></h3>
                        </div>

                        <div class="mb-3">
                            <label for="question_statement" class="form-label">Question Statement:</label>
                            <textarea id="question_statement" v-model="question_statement" rows="3" class="form-control" required></textarea>
                        </div>

                        <h4 class="text-primary">Single Option Correct</h4>

                        <div class="mb-3">
                            <label for="option1" class="form-label">Option A:</label>
                            <input type="text" id="option1" v-model="option1" class="form-control" required>
                        </div>

                        <div class="mb-3">
                            <label for="option2" class="form-label">Option B:</label>
                            <input type="text" id="option2" v-model="option2" class="form-control" required>
                        </div>

                        <div class="mb-3">
                            <label for="option3" class="form-label">Option C:</label>
                            <input type="text" id="option3" v-model="option3" class="form-control" required>
                        </div>

                        <div class="mb-3">
                            <label for="option4" class="form-label">Option D:</label>
                            <input type="text" id="option4" v-model="option4" class="form-control" required>
                        </div>

                        <div class="mb-3">
                            <label for="correct_option" class="form-label">Correct Option:</label>
                            <select id="correct_option" v-model="correct_option" class="form-select" required>
                                <option value="1">A</option>
                                <option value="2">B</option>
                                <option value="3">C</option>
                                <option value="4">D</option>
                            </select>
                        </div>

                        <div class="d-flex justify-content-between">
                            <router-link :to="{ name: 'AdminQuizzes' }" class="btn btn-secondary">Cancel</router-link>
                            <button type="submit" class="btn btn-primary">Save and Next</button>
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