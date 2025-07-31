<script setup>
import Navbar from './components/navbar.vue';
import Footer from './components/footer.vue';
import { useRoute } from 'vue-router';
import { computed } from 'vue';

const route = useRoute();

// Show navbar only if route requires auth
const showNavbar = computed(() => {
  return route.meta.requiresAuth === true;
});
</script>

<template>
  <div id="app-container">
    <Navbar v-if="showNavbar" />
    <router-view />
    <Footer />
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop_shadow(0 0 2em #42b883aa);
}
</style>
