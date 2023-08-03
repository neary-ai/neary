<template>
  <div class="flex-grow">
    <label v-if="label" :for="inputId" class="block text-sm font-medium leading-6 text-field-label mb-2">{{ label }}</label>
    <div>
      <input type="checkbox" class="rounded text-field-default focus:ring-0" :name="inputName" :id="inputId" :checked="localValue" @input="handleInput">
      <label :for="inputId" class="ml-2">{{label}}</label>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  label: {
    type: String,
  },
  inputName: {
    type: String,
  },
  inputId: {
    type: String,
  },
  value: {
    type: Boolean,
    default: false,
  },
});

let localValue = ref(null);
const emit = defineEmits(['updateInput'])

const handleInput = (event) => {
  const newValue = event.target.checked;
  if (localValue.value !== null) {
    emit('updateInput', newValue);
  }
}

watch(() => props.value, (newValue) => {
  localValue.value = newValue;
}, { immediate: true });

</script>