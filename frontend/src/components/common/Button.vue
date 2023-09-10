<template>
  <button :class="[...btn, ...buttonSize]" @click="$emit('buttonClick')" :disabled="disabled">
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
  buttonSize: {
    type: String,
    default: 'medium'
  },
  disabled: Boolean
});

const btn = computed(() => {
  const baseClasses = [
    'rounded-md',
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
    'btn-light': [
      'bg-nearylight-300',
      'text-black',
    ],
    'btn-outline-light': [
      'bg-transparent',
      'border',
      'border-nearylight-200',
      'text-nearylight-200',
    ],
  };

  return [...baseClasses, ...buttonTypes[props.buttonType]];
});

const buttonSize = computed(() => {
  const buttonSizes = {
    'small': ['px-2', 'py-1.5'],
    'medium': ['px-2.5', 'py-2'],
    'large': ['px-4', 'py-4'],
  };
  
  return buttonSizes[props.buttonSize] || [];
});
</script>
