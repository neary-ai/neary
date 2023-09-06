<template>
  <div class="w-full flex-grow">
    <label v-if="label" :for="inputId" class="block text-sm font-medium leading-6 text-slate-200 mb-2">{{ label }}</label>
    <div>
      <input type="number" :name="inputName" :id="inputId" :placeholder="placeholderNumber" :value="modelValue"
        :step="step" :max="maxValue" :min="minValue" @input="$emit('update:modelValue', $event.target.valueAsNumber)"
        @change="$emit('change', $event.target.valueAsNumber)"
        class="focus:ring-0 border border-transparent rounded-md bg-field-default text-field-default-foreground focus:border-field-focused w-full text-sm px-3 py-2" />
    </div>
  </div>
</template>

<script setup>

const props = defineProps({
  modelValue: {
    type: Number,
    default: 0,
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
  placeholderNumber: {
    type: Number,
    default: 0,
  },
  step: {
    type: Number,
    default: 1,
  },
  maxValue: {
    type: Number,
    default: Number.MAX_SAFE_INTEGER,
  },
  minValue: {
    type: Number,
    default: Number.MIN_SAFE_INTEGER,
  },
});

const emit = defineEmits(['update:modelValue', 'change'])

</script>
