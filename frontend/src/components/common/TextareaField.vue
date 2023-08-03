<template>
  <div class="w-full flex-grow">
    <label v-if="label" :for="inputId" class="block text-sm font-medium leading-6 text-slate-200 mb-2">{{ label }}</label>
    <div>
      <textarea :name="inputName" :id="inputId" :placeholder="placeholderText" :value="value" @input="handleInput"
        class="focus:ring-0 border border-transparent rounded-md bg-field-default text-field-default-foreground focus:border-field-focused text-sm w-full px-4 py-3 h-32 leading-6"
        spellcheck="false"></textarea>
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
  placeholderText: {
    type: String,
    default: 'Enter text',
  },
  value: {
    type: String,
    default: '',
  },
});

let localValue = ref('');
const emit = defineEmits(['updateInput'])

const handleInput = (event) => {
  const newValue = event.target.value;
  if (localValue.value && localValue.value != newValue) {
    emit('updateInput', newValue);
  }
}

watch(() => props.value, (newValue) => {
  localValue.value = newValue;
}, { immediate: true });

</script>