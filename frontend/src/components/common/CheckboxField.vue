<template>
  <div class="flex-grow">
    <label v-if="label" :for="inputId" class="block text-sm font-medium leading-6 text-field-label mb-2">{{ label }}</label>
    <div>
      <input type="checkbox" class="rounded text-field-default focus:ring-0" :name="inputName" :id="inputId" :checked="modelValue" @change="$emit('update:modelValue', $event.target.checked)">
      <label :for="inputId" class="ml-2">{{label}}</label>
    </div>
  </div>
</template>

<script setup>

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
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
});

const emit = defineEmits(['update:modelValue'])

</script>