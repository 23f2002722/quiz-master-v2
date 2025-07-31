<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const user_full_name = ref('');
const subjects = ref([]);
const chapters = ref([]); 
const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const fetchDashboardData = async () => {
  try {
    const response = await axios.get('/api/dashboard');
    user_full_name.value = response.data.user_details.full_name;
    subjects.value = response.data.subjects;
    chapters.value = response.data.chapters; 

  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load dashboard data.';
    console.error('Fetch Dashboard error:', error);
  }
};

const getChaptersForSubject = (subjectId) => {
  return chapters.value.filter(chapter => chapter.subject_id === subjectId);
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
    subjects.value = subjects.value.filter(sub => sub.id !== subjectId);
    chapters.value = chapters.value.filter(chapter => chapter.subject_id !== subjectId);
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to delete subject.';
    console.error('Delete Subject error:', error);
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
    chapters.value = chapters.value.filter(chapter => chapter.id !== chapterId);
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to delete chapter.';
    console.error('Delete Chapter error:', error);
  }
};

onMounted(() => {
  fetchDashboardData();
});
</script>

<template>
<div class="container mt-4">
    <h1 class="text-center">Welcome, {{ user_full_name }}</h1>
<br>
    <div class="d-flex justify-content-center mb-3">
        <router-link to="/admin/users" class="btn btn-outline-primary me-2">View Users</router-link>
        <router-link to="/admin/subjects/add" class="btn btn-primary">Add Subject</router-link>
    </div>

    <section>
        <h2 class="mb-4">Subjects</h2>

        <template v-if="subjects && subjects.length > 0">
            <div class="row row-cols-1 row-cols-md-3 row-cols-lg-3 justify-content-center g-4">
                <div class="col-md-6 col-lg-5 mb-4 ms-2 me-2" v-for="sub in subjects" :key="sub.id">
                    <div class="card shadow border rounded p-3 d-flex flex-column">
                                
                        <h4 class="text-center">
                            <a href="#" class="text-decoration-none" data-bs-toggle="modal" :data-bs-target="'#modal' + sub.id">
                                {{ sub.name }}
                            </a>
                        </h4>
                        
                        <div class="modal fade" :id="'modal' + sub.id" tabindex="-1"
                            :aria-labelledby="'modalLabel' + sub.id" aria-hidden="true">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title" :id="'modalLabel' + sub.id">{{ sub.name }}</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"
                                            aria-label="Close"></button>
                                    </div>
                                    <div class="modal-body">
                                        <p>{{ sub.description }}</p>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary"
                                            data-bs-dismiss="modal">Close</button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <template v-if="getChaptersForSubject(sub.id).length > 0">
                            <table class="table table-bordered mt-3">
                                <thead class="table-primary text-center align-middle">
                                    <tr>
                                        <th>Chapter Name</th>
                                        <th>No. of Questions</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                
                                <tbody>
                                    <tr v-for="chapter in getChaptersForSubject(sub.id)" :key="chapter.id">
                                        <td class="text-wrap text-break">
                                            <router-link :to="{ name: 'AdminChapterQuizzes', params: { chapterId: chapter.id }}" class="btn btn-link text-decoration-none p-0 border-0">{{ chapter.name }}</router-link>
                                        </td>

                                        <td class="text-center">{{ chapter.questions_count }}</td>

                                        <td>
                                            <div class="btn-group gap-1">
                                                <router-link :to="{ name: 'AdminEditChapter', params: { chapterId: chapter.id }}" class="btn btn-primary btn-sm">Edit</router-link>
                                                <button @click="deleteChapter(chapter.id)" class="btn btn-danger btn-sm">Delete</button>
                                            </div>
                                        </td>
                                        
                                    </tr>
                                </tbody>
                            </table>
                        </template>

                        <div class="text-center mt-3">
                            <router-link :to="{ name: 'AdminAddChapter', params: { subjectId: sub.id }}" class="btn btn-pink">+ Chapter</router-link>
                        </div>

                        <div class="text-center mt-2">
                            <button @click="deleteSubject(sub.id)" class="btn btn-danger btn-sm">Delete Subject</button>
                        </div>
                    </div>
                </div>
            </div>
        </template>
        <template v-else>
            <p class="text-muted">No subjects yet.</p>
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
.btn-pink {
    background-color: #ff69b4; /* Example pink color */
    border-color: #ff69b4;
    color: white;
}
.btn-pink:hover {
    background-color: #e05e9b;
    border-color: #e05e9b;
}
</style>