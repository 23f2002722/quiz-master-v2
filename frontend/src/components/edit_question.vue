<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const props = defineProps({
  questionId: {
    type: [String, Number],
    required: true
  }
});

const question_statement = ref('');
const option1 = ref('');
const option2 = ref('');
const option3 = ref('');
const option4 = ref('');
const correct_option = ref(''); 

const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const correctOptionMap = {
  'A': '1', 'B': '2', 'C': '3', 'D': '4',
  '1': 'A', '2': 'B', '3': 'C', '4': 'D'
};

const mapCorrectOptionToSelect = (optionChar) => {
  return correctOptionMap[optionChar] || '';
};

const fetchQuestionDetails = async () => {
  try {
    const response = await axios.get(`/api/admin/questions/${props.questionId}`);
    const question_data = response.data;
    
    question_statement.value = question_data.question_statement;
    option1.value = question_data.option1;
    option2.value = question_data.option2;
    option3.value = question_data.option3;
    option4.value = question_data.option4;
    correct_option.value = mapCorrectOptionToSelect(question_data.correct_option); 
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load question details.';
    console.error('Fetch Question Details error:', error);
  }
};

const updateQuestion = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!question_statement.value || !option1.value || !option2.value || !option3.value || !option4.value || !correct_option.value) {
    errorMessage.value = 'All fields are required!';
    return;
  }

  try {
    const response = await axios.put(`/api/admin/edit_question/${props.questionId}`, {
      question_statement: question_statement.value,
      option1: option1.value,
      option2: option2.value,
      option3: option3.value,
      option4: option4.value,
      correct_option: correct_option.value, 
    });

    successMessage.value = response.data.message;
    
    setTimeout(() => {
      router.push('/admin/quizzes');
    }, 1500);

  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.message || 'An error occurred while updating the question.';
    } else if (error.request) {
      errorMessage.value = 'No response from server. Check your network.';
    } else {
      errorMessage.value = 'Error: ' + error.message;
    }
    console.error("Update Question error:", error);
  }
};

onMounted(() => {
  fetchQuestionDetails();
});
</script>

<template>
<div class="container mt-5 d-flex flex-column align-items-center">
    <div class="col-md-8">
        <h2 class="text-center text-warning mb-4">Edit Question</h2>

        <div class="card shadow-lg">
            <div class="card-body">
                <form @submit.prevent="updateQuestion">
                    
                    <div class="mb-3">
                        <label for="question_statement" class="form-label">Question Statement</label>
                        <input type="text" id="question_statement" v-model="question_statement" 
                               class="form-control" required>
                    </div>

                    <h4 class="text-primary">Options</h4>

                    <div class="mb-3">
                        <label for="option1" class="form-label">Option A</label>
                        <input type="text" id="option1" v-model="option1" class="form-control" required>
                    </div>

                    <div class="mb-3">
                        <label for="option2" class="form-label">Option B</label>
                        <input type="text" id="option2" v-model="option2" class="form-control" required>
                    </div>

                    <div class="mb-3">
                        <label for="option3" class="form-label">Option C</label>
                        <input type="text" id="option3" v-model="option3" class="form-control" required>
                    </div>

                    <div class="mb-3">
                        <label for="option4" class="form-label">Option D</label>
                        <input type="text" id="option4" v-model="option4" class="form-control" required>
                    </div>

                    <div class="mb-3">
                        <label for="correct_option" class="form-label">Correct Answer</label>
                        <select id="correct_option" v-model="correct_option" class="form-select" required>
                            <option value="1">A</option>
                            <option value="2">B</option>
                            <option value="3">C</option>
                            <option value="4">D</option>
                        </select>
                    </div>

                    <div class="d-flex justify-content-between">
                        <router-link to="/dashboard" class="btn btn-secondary">Cancel</router-link>
                        <button type="submit" class="btn btn-primary">Update Question</button>
                    </div>

                </form>
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