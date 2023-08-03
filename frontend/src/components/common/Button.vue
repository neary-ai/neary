<template>
  <button :class="[...btn]" @click="$emit('buttonClick')" :disabled="disabled">
    <slot></slot>
  </button>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  buttonType: {
    type: String,
    default: 'btn-pink'
  },
  disabled: Boolean
});

const btn = computed(() => {
  const baseClasses = [
    'rounded-md',
    'px-2.5',
    'py-2',
    'font-semibold',
    'text-sm',
    'shadow-sm',
    'hover:bg-opacity-90'
  ];

  const buttonTypes = {
    'btn-yellow': [
      'bg-nearyyellow-200',
      'text-nearyblue-300',
    ],
    'btn-pink': [
      'bg-nearypink-300',
      'text-white',
    ],
    'btn-outline-pink': [
      'bg-transparent',
      'border',
      'border-nearypink-300',
      'text-nearypink-300',
    ],
    'btn-blue': [
      'bg-nearyblue-50',
      'text-nearygray-100',
    ]
  };

  return [...baseClasses, ...buttonTypes[props.buttonType]];
});
</script>
