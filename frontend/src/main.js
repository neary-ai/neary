import { createPinia } from 'pinia';
import { createApp } from 'vue';
import Vue3TouchEvents from 'vue3-touch-events';
import App from './App.vue';
import router from './router';
import './tailwind.css';
import './assets/global.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(Vue3TouchEvents);

app.mount('#app');
