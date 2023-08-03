<template>
  <div class="min-h-full w-full flex items-center justify-center">
    <div class="flex flex-col justify-center px-12 py-12 bg-nearyblue-300 w-full max-w-sm rounded-lg shadow mt-8">
      <div class="flex flex-col items-center mx-auto w-full max-w-sm">
        <img :src="logo" class="h-8" />
        <h2 class="mt-4 text-center text-xl font-medium leading-9 tracking-tight text-slate-300">Let's get you setup!</h2>
      </div>
      <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-sm">
        <form @submit.prevent="register" class="space-y-6" action="#" method="POST">
          <div>
            <label for="email" class="block text-sm font-medium leading-6 text-slate-400">Email address</label>
            <div class="mt-2">
              <input v-model="email" placeholder="your@email.com" id="email" name="email" type="email" autocomplete="email" required=""
                class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-nearypink-300 sm:text-sm sm:leading-6" />
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between">
              <label for="password" class="block text-sm font-medium leading-6 text-slate-400">Password</label>
            </div>
            <div class="mt-2">
              <input v-model="password" id="password" name="password" type="password" autocomplete="current-password" placeholder="******"
                required=""
                class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-nearypink-300 sm:text-sm sm:leading-6" />
            </div>
          </div>
          <div class="mt-8">
            <button type="submit"
              class="flex w-full justify-center rounded-md bg-nearypink-300 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-nearypink-300/80 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-nearypink-300">Create Account</button>
          </div>
          <div v-if="errorMessage" class="text-center text-nearypink-300">{{ errorMessage }}</div>
        </form>
      </div>
    </div>
  </div>
</template>
  
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import logo from '@/assets/images/neary.svg';
import api from '@/services/apiService';

const email = ref('');
const password = ref('');
const errorMessage = ref('');

const router = useRouter();

const register = async () => {
  const user = {
    email: email.value,
    password: password.value,
  };

  try {
    await api.registerUser(user);
    router.push('/');
  }
  catch (error) {
    if(!error || !error.data.detail) {
      errorMessage.value = "Can't connect to server!";
    }
    else {
      errorMessage.value = error.data.detail;
    }
  }
};
</script>
  