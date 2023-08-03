<template>
    <div class="flex items-center gap-4">
      <div id="back-button" @click="handleClick" class="text-lg text-white font-semibold">
        <button
          type="button"
          class="rounded-full bg-slate-400/60 p-1 text-nearyblue-200 shadow-sm hover:bg-slate-400/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
            <path
              fill-rule="evenodd"
              d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
      <div class="flex text-xl text-white font-semibold">{{ sectionName }}</div>
    </div>
  </template>
  
  <script setup>
  defineProps({
    sectionName: {
      type: String,
      required: true,
    },
  });
  
  const emit = defineEmits(['on-click']);

  const handleClick = () => {
    emit('on-click');
  };
  </script>
  