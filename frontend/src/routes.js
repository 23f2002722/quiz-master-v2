import { createRouter, createWebHistory } from 'vue-router';

import login from './components/login.vue';
import register_user from './components/register_user.vue';
import dashboard_user from './components/dashboard_user.vue';
import dashboard_admin from './components/dashboard_admin.vue';
import dashboard from './components/dashboard.vue';
import profile from './components/profile.vue';
import summary_user from './components/summary_user.vue';
import summary_admin from './components/summary_admin.vue';
import scores from './components/scores.vue';
import quiz from './components/quiz.vue';

import show_users from './components/show_users.vue';
import add_subject from './components/add_subject.vue';
import add_chapter from './components/add_chapter.vue';
import edit_chapter from './components/edit_chapter.vue';
import quiz_management from './components/quiz_management.vue';
import add_quiz from './components/add_quiz.vue';
import add_question from './components/add_question.vue';
import edit_question from './components/edit_question.vue';
import quiz_analytics from './components/quiz_analytics.vue';
import search from './components/search.vue';
import NotFoundPage from './components/NotFoundPage.vue';


const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: login },
  { path: '/register', name: 'Register', component: register_user },

  {
    path: '/dashboard',
    name: 'Dashboard',
    component: dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/summary',
    name: 'Summary',
    component: summary_user,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/summary',
    name: 'AdminSummary',
    component: summary_admin,
    meta: { requiresAuth: true, requiresAdmin: true }
  },

  {
    path: '/dashboard/scores',
    name: 'UserScores',
    component: scores,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/quiz/:quizId',
    name: 'Quiz',
    component: quiz,
    props: true,
    meta: { requiresAuth: true, requiresUser: true }
  },

  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: show_users,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/subjects/add',
    name: 'AdminAddSubject',
    component: add_subject,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/subjects/:subjectId/edit',
    name: 'AdminEditSubject',
    component: NotFoundPage,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/subjects/:subjectId/chapters/add',
    name: 'AdminAddChapter',
    component: add_chapter,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/chapters/:chapterId/edit',
    name: 'AdminEditChapter',
    component: edit_chapter,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes',
    name: 'AdminQuizzes',
    component: quiz_management,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/chapters/:chapterId/quizzes',
    name: 'AdminChapterQuizzes',
    component: quiz_management,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes/add',
    name: 'AdminAddQuiz',
    component: add_quiz,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes/:quizId/edit',
    name: 'AdminEditQuiz',
    component: NotFoundPage,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes/:quizId/questions/add',
    name: 'AdminAddQuestion',
    component: add_question,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/questions/:questionId/edit',
    name: 'AdminEditQuestion',
    component: edit_question,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes/:quizId/analytics',
    name: 'AdminQuizAnalytics',
    component: quiz_analytics,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  
  {
    path: '/search',
    name: 'Search',
    component: search,
    meta: { requiresAuth: true }
  },

  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFoundPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('access_token');
  const userRole = localStorage.getItem('user_role');

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' });
  }
  else if ((to.name === 'Login' || to.name === 'Register') && isAuthenticated) {
    next({ name: 'Dashboard' });
  }
  else if (to.meta.requiresAdmin && userRole !== 'admin') {
    next({ name: 'Dashboard' });
  }
  else if (to.meta.requiresUser && userRole !== 'user') {
     next({ name: 'Dashboard' });
  }
  else {
    next();
  }
});

export { router };