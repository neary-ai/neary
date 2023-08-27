<template>
  <div class="w-full flex-grow">
    <label v-if="label" :for="inputId" class="block text-sm font-medium leading-6 text-slate-200 mb-2">{{ label }}</label>
    <div>
      <textarea :name="inputName" :id="inputId" :placeholder="placeholderText" :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)" @change="$emit('change', $event.target.value)"
        class="focus:ring-0 border border-transparent rounded-md bg-field-default text-field-default-foreground focus:border-field-focused placeholder:text-field-default-foreground/70 text-sm w-full px-4 py-3 h-32 leading-6"
        spellcheck="false"></textarea>
    </div>
  </div>
</template>
  
<script setup>

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
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
  }
});

const emit = defineEmits(['update:modelValue', 'change'])

</script>