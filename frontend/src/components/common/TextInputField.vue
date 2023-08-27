<template>
  <div class="flex-grow w-full">
    <label v-if="label" :for="inputId" class="block text-sm font-medium leading-6 text-field-label mb-2">{{ label
    }}</label>
    <div>
      <input :type="inputType" :name="inputName" :id="inputId" :placeholder="placeholderText" :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)" @change="$emit('change', $event.target.value)"
        class="focus:ring-0 border border-transparent rounded-md bg-field-default text-field-default-foreground focus:border-field-focused placeholder:text-field-default-foreground/70 text-sm w-full px-3 py-2" />
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
  inputType: {
    type: String,
    default: 'text',
  },
  placeholderText: {
    type: String,
    default: 'Type something..',
  },
});

const emit = defineEmits(['update:modelValue', 'change'])

</script>