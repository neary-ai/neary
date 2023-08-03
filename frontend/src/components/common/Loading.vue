<template>
  <transition name="fade">
    <div v-if="visible" :class="['flex items-center', textColor]">
      <span class="inline-block ml-1">
          Loading{{ loadingDots }}</span>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

let intervalId;
const visible = ref(true);
const loadingDots = ref('');

onMounted(() => {
let count = 0;
intervalId = setInterval(() => {
  count += 1;
  loadingDots.value = '.'.repeat(count % 4);
}, 500);
});

onUnmounted(() => {
clearInterval(intervalId);
});

const props = defineProps({
textColor: {
  type: String,
  default: 'text-nearypink-300'
}
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
transition: opacity 0.5s;
}

.fade-enter,
.fade-leave-to {
opacity: 0;
}
</style>
