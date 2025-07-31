<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const props = defineProps({
  quizId: {
    type: [String, Number],
    required: true
  }
});

const quizData = ref(null); 
const questions = ref([]);
const currentQuestionIndex = ref(0); 
const userResponses = ref({}); 

const timeLeftSeconds = ref(0);
const timerInterval = ref(null); 

const selectedOption = ref(null);

const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const fetchQuizQuestionsAndStart = async () => {
  try {
    const response = await axios.post(`/api/user/start_quiz/${props.quizId}`); 
    quizData.value = response.data.quiz_data;
    questions.value = quizData.value.questions;
    timeLeftSeconds.value = quizData.value.time_duration_seconds;

    const storedResponses = JSON.parse(localStorage.getItem(`quiz_${props.quizId}_responses`)) || {};
    userResponses.value = storedResponses;

    const lastIndex = parseInt(localStorage.getItem(`quiz_${props.quizId}_last_index`)) || 0;
    currentQuestionIndex.value = lastIndex;

    selectedOption.value = userResponses.value[currentQuestionIndex.value] || null;

    startTimer();
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to start quiz or load questions.';
    console.error('Start Quiz error:', error);
    setTimeout(() => router.push('/dashboard'), 3000);
  }
};

const startTimer = () => {
  if (timerInterval.value) clearInterval(timerInterval.value); 

  const startTime = Date.now(); 
  const endTime = startTime + (timeLeftSeconds.value * 1000); 

  timerInterval.value = setInterval(() => {
    const now = Date.now();
    const remaining = Math.max(0, endTime - now);
    timeLeftSeconds.value = Math.floor(remaining / 1000);

    if (timeLeftSeconds.value <= 0) {
      clearInterval(timerInterval.value);
      submitQuiz(true); 
    }
  }, 1000);
};

const stopTimer = () => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value);
    timerInterval.value = null;
  }
};

const currentQuestion = computed(() => {
  return questions.value[currentQuestionIndex.value];
});

const currentMinutes = computed(() => {
  return Math.floor(timeLeftSeconds.value / 60);
});

const currentSeconds = computed(() => {
  const seconds = timeLeftSeconds.value % 60;
  return seconds.toString().padStart(2, '0');
});

const isFirstQuestion = computed(() => {
  return currentQuestionIndex.value === 0;
});

const isLastQuestion = computed(() => {
  return currentQuestionIndex.value === questions.value.length - 1;
});

const saveCurrentResponse = () => {
  if (selectedOption.value !== null) {
    userResponses.value[currentQuestionIndex.value] = selectedOption.value;
    localStorage.setItem(`quiz_${props.quizId}_responses`, JSON.stringify(userResponses.value));
  }
};

const navigateQuestion = (direction) => {
  saveCurrentResponse(); 

  if (direction === 'next' && !isLastQuestion.value) {
    currentQuestionIndex.value++;
  } else if (direction === 'prev' && !isFirstQuestion.value) {
    currentQuestionIndex.value--;
  }
  
  selectedOption.value = userResponses.value[currentQuestionIndex.value] || null;
  localStorage.setItem(`quiz_${props.quizId}_last_index`, currentQuestionIndex.value);
};

const submitQuiz = async (timedOut = false) => {
  stopTimer(); 
  saveCurrentResponse(); 

  errorMessage.value = '';
  successMessage.value = '';

  try {
    const response = await axios.post('/api/user/submit_quiz', {
      quiz_id: props.quizId,
      responses: userResponses.value,
      start_time: quizData.value.start_time,
      end_time: new Date().toISOString() 
    });

    successMessage.value = response.data.message;

    localStorage.removeItem(`quiz_${props.quizId}_responses`);
    localStorage.removeItem(`quiz_${props.quizId}_last_index`);

    setTimeout(() => {
      router.push('/dashboard/scores'); 
    }, 2000);

  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.message || 'An error occurred during submission.';
      if (timedOut && !errorMessage.value) {
        errorMessage.value = 'Time ran out! Quiz submitted automatically.';
      }
    } else if (error.request) {
      errorMessage.value = 'No response from server. Check your network.';
    } else {
      errorMessage.value = 'Error: ' + error.message;
    }
    console.error("Submit Quiz error:", error);
  }
};

onMounted(() => {
  fetchQuizQuestionsAndStart();
});

onBeforeUnmount(() => {
  stopTimer(); 
});
</script>

<template>
<div class="container mt-4">
    <template v-if="currentQuestion">
        <h2 class="mb-3">Question {{ currentQuestionIndex + 1 }}/{{ questions.length }}</h2>
        
        <div class="alert alert-info">Time Remaining: <span id="timer" class="fw-bold">{{ currentMinutes }}</span> minutes <span id="timer-seconds" class="fw-bold">{{ currentSeconds }}</span> seconds</div>

        <div class="card shadow-sm p-4">
            <form @submit.prevent>
                <p class="h5">{{ currentQuestion.question_statement }}</p>
                <div class="form-check">
                    <input class="form-check-input" type="radio" id="option1" value="1" v-model="selectedOption">
                    <label class="form-check-label" for="option1">{{ currentQuestion.option1 }}</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="radio" id="option2" value="2" v-model="selectedOption">
                    <label class="form-check-label" for="option2">{{ currentQuestion.option2 }}</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="radio" id="option3" value="3" v-model="selectedOption">
                    <label class="form-check-label" for="option3">{{ currentQuestion.option3 }}</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="radio" id="option4" value="4" v-model="selectedOption">
                    <label class="form-check-label" for="option4">{{ currentQuestion.option4 }}</label>
                </div>
                <div class="mt-4">
                    <button type="button" class="btn btn-secondary me-2" @click="navigateQuestion('prev')" :disabled="isFirstQuestion">Previous</button>
                    <button type="button" class="btn btn-primary me-2" @click="navigateQuestion('next')" :disabled="isLastQuestion">Next</button>
                    <button type="button" class="btn btn-success" @click="submitQuiz()">Submit</button>
                </div>
            </form>
        </div>
    </template>
    <template v-else-if="!errorMessage">
        <div class="text-center">Loading quiz...</div>
    </template>

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