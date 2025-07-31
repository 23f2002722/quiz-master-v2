<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const userRole = ref('');
const category = ref('');
const query = ref('');

const usersResult = ref([]);
const quizzesResult = ref([]);
const chaptersResult = ref([]);
const subjectsResult = ref([]);
const scoresResult = ref([]);

const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

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

const formatQuizDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const performSearch = async () => {
  errorMessage.value = '';
  successMessage.value = '';
  
  usersResult.value = [];
  quizzesResult.value = [];
  chaptersResult.value = [];
  subjectsResult.value = [];
  scoresResult.value = [];

  if (!category.value || !query.value) {
    errorMessage.value = 'Please select a category and enter a search query.';
    return;
  }

  try {
    const response = await axios.get('/api/search', {
      params: {
        category: category.value,
        query: query.value
      }
    });

    if (response.data.users) { 
      usersResult.value = response.data.users;
    } else if (response.data.quizzes) { 
      quizzesResult.value = response.data.quizzes;
    } else if (response.data.chapters) {
      chaptersResult.value = response.data.chapters;
    } else if (response.data.subjects) { 
      subjectsResult.value = response.data.subjects;
    } else if (response.data.scores) { 
      scoresResult.value = response.data.scores;
    }

  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Error performing search.';
    console.error('Search error:', error);
  }
};

const deleteUser = async (userId) => {
  if (!confirm('Are you sure you want to delete this user?')) {
    return;
  }
  errorMessage.value = '';
  successMessage.value = '';
  try {
    const response = await axios.delete(`/api/admin/delete_user/${userId}`);
    successMessage.value = response.data.message;
    usersResult.value = usersResult.value.filter(user => user.id !== userId);
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to delete user.';
    console.error('Delete User error:', error);
  }
};

const deleteQuestion = async (questionId) => {
  if (!confirm('Are you sure you want to delete this question?')) {
    return;
  }
  errorMessage.value = '';
  successMessage.value = '';
  try {
    const response = await axios.delete(`/api/admin/delete_question/${questionId}`);
    successMessage.value = response.data.message;
    performSearch();
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to delete question.';
    console.error('Delete Question error:', error);
  }
};

const deleteQuiz = async (quizId) => {
  if (!confirm('Are you sure you want to delete this quiz?')) {
    return;
  }
  errorMessage.value = '';
  successMessage.value = '';
  try {
    const response = await axios.delete(`/api/admin/delete_quiz/${quizId}`);
    successMessage.value = response.data.message;
    quizzesResult.value = quizzesResult.value.filter(quiz => quiz.id !== quizId);
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to delete quiz.';
    console.error('Delete Quiz error:', error);
  }
};

const deleteChapter = async (chapterId) => {
  if (!confirm('Are you sure you want to delete this chapter?')) {
    return;
  }
  errorMessage.value = '';
  successMessage.value = '';
  try {
    const response = await axios.delete(`/api/admin/delete_chapter/${chapterId}`);
    successMessage.value = response.data.message;
    chaptersResult.value = chaptersResult.value.filter(chapter => chapter.id !== chapterId);
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to delete chapter.';
    console.error('Delete Chapter error:', error);
  }
};

const deleteSubject = async (subjectId) => {
  if (!confirm('Are you sure you want to delete this subject?')) {
    return;
  }
  errorMessage.value = '';
  successMessage.value = '';
  try {
    const response = await axios.delete(`/api/admin/delete_subject/${subjectId}`);
    successMessage.value = response.data.message;
    subjectsResult.value = subjectsResult.value.filter(subject => subject.id !== subjectId);
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to delete subject.';
    console.error('Delete Subject error:', error);
  }
};

onMounted(() => {
  userRole.value = localStorage.getItem('user_role');
});
</script>

<template>
<div class="container mt-4">
    <form @submit.prevent="performSearch">
        <template v-if="userRole === 'user'">
        <br><h2 class="mb-4">Search Quiz and Score Card</h2>
        <div class="form-group">
            <label for="category">Select Category</label>
            <select class="form-control" id="category" v-model="category">
                <option value="">Select Category</option>
                <option value="quiz">Quiz</option>
                <option value="scores">Score Card</option>
            </select>
        </div>
        </template>
        <template v-else>
        <br><h2 class="mb-4">Search Users, Quiz, Chapters, Subjects</h2>
        <div class="form-group">
            <label for="category">Select Category</label>
            <select class="form-control" id="category" v-model="category">
                <option value="">Select Category</option>
                <option value="users">Users</option>
                <option value="quiz">Quiz</option>
                <option value="chapters">Chapters</option>
                <option value="subjects">Subjects</option>
            </select>
        </div>
        </template>
        <div class="form-group">
            <label for="query">Search</label>
            <input type="text" class="form-control" id="query" v-model="query" placeholder="Search for..." />
        </div><br>
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>

    <template v-if="category">
    <hr>
    <h4>Results for {{ category.charAt(0).toUpperCase() + category.slice(1) }}</h4><br>

    <template v-if="category === 'users'">
        <template v-if="usersResult && usersResult.length > 0">
        <div class="list-group">
            <div class="list-group-item list-group-item-action p-3 mb-3 shadow-sm rounded" v-for="user_item in usersResult" :key="user_item.id">
                <h5 class="mb-1">
  <strong>Name:</strong> {{ user_item.full_name }}
</h5>
                <p class="mb-1"><strong>Email:</strong> {{ user_item.username }}</p>
                <p class="mb-1"><strong>Qualification:</strong> {{ user_item.qualification }}</p>
                <p class="mb-3"><strong>DOB:</strong> {{ user_item.dob }}</p>
                <button @click="deleteUser(user_item.id)" class="btn btn-danger btn-sm">Delete</button>
            </div>
        </div>
        </template>
        <template v-else>
        <p class="text-center">No users found matching your query.</p>
        </template>
    </template>

    <template v-else-if="category === 'quiz'">
        <template v-if="quizzesResult && quizzesResult.length > 0">
        <template v-if="userRole === 'admin'">
        <div class="row">
            <div class="col-md-6 mb-4" v-for="quiz_item in quizzesResult" :key="quiz_item.id">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title">{{ quiz_item.type }} (<a href="#" class="text-decoration-none" data-bs-toggle="modal" :data-bs-target="'#modal' + quiz_item.chapter_id"> {{quiz_item.chapter_name }} </a>)</h5>
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
                                    <th>Question_Statement</th>
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
        </template>
        <template v-else>
        <div>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Quiz</th>
                        <th>No. of questions</th>
                        <th>Date</th>
                        <th>Duration</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="q_item in quizzesResult" :key="q_item.id">
                        <td>{{ q_item.type }} ({{ q_item.chapter_name }})</td>
                        <td>{{ q_item.questions_count }}</td>
                        <td>{{ formatQuizDate(q_item.date_of_quiz) }}</td>
                        <td>{{ q_item.time_duration }} minutes</td>
                        <td><router-link :to="{ name: 'Quiz', params: { quizId: q_item.id } }" class="btn btn-primary">Start Quiz</router-link></td>
                    </tr>
                </tbody>
            </table>
        </div>
        </template>
        </template>
        <template v-else>
        <p>No quiz found matching your query.</p>
        </template>
    </template>

    <template v-else-if="category === 'chapters'">
        <template v-if="chaptersResult && chaptersResult.length > 0">
        <div><table class="table table-striped">
            <thead>
                <tr>
                    <th>Chapter Name</th>
                    <th>No. of Questions</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="chapter_item in chaptersResult" :key="chapter_item.id">
                    <td>{{ chapter_item.name }}</td>
                    <td>{{ chapter_item.questions_count }}</td>
                    <td>
                        <router-link :to="{ name: 'AdminEditChapter', params: { chapterId: chapter_item.id } }" class="btn btn-primary btn-sm">Edit</router-link>
                        <button @click="deleteChapter(chapter_item.id)" class="btn btn-danger btn-sm ms-1">Delete</button>
                    </td>
                </tr>
            </tbody>
        </table>
        </div>
        </template>
        <template v-else>
        <p>No chapters found matching your query.</p>
        </template>
    </template>

    <template v-else-if="category === 'subjects'">
        <template v-if="subjectsResult && subjectsResult.length > 0">
        <div><table class="table table-striped">
            <thead>
                <tr>
                    <th>Subject Name</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="subject_item in subjectsResult" :key="subject_item.id">
                    <td>{{ subject_item.name }}</td>
                    <td>
                        <router-link :to="{ name: 'AdminAddChapter', params: { subjectId: subject_item.id } }" class="btn btn-success btn-sm me-1">+ Chapter</router-link>
                        <button @click="deleteSubject(subject_item.id)" class="btn btn-danger btn-sm">Delete</button>
                    </td>
                </tr>
            </tbody>
        </table>
        </div>
        </template>
        <template v-else>
        <p>No subjects found matching your query.</p>
        </template>
    </template>

    <template v-else-if="category === 'scores'">
        <template v-if="scoresResult && scoresResult.length > 0">
        <div><table class="table table-striped">
            <thead>
                <tr>
                    <th>Quiz Type</th>
                    <th>Chapter</th>
                    <th>Subject</th>
                    <th>Date of Attempt</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="score_item in scoresResult" :key="score_item.score_id">
                    <td>{{ score_item.quiz_type }}</td>
                    <td>{{ score_item.chapter_name }}</td>
                    <td>{{ score_item.subject_name }}</td>
                    <td>{{ formatTimestamp(score_item.timestamp) }}</td>
                    <td>{{ score_item.total_score }}/{{ score_item.total_questions }}</td>
                </tr>
            </tbody>
        </table>
        </div>
        </template>
        <template v-else>
        <p>No scores found matching your query.</p>
        </template>
    </template>
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