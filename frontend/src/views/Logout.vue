<template>
    <div class="logout">
    </div>
  </template>
  
  <script setup>
  import { onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import api from '@/services/apiService';
  
  const router = useRouter();
  
  onMounted(async () => {
    await api.logoutUser();
    router.push('/login');
  });
  </script>