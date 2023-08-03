<template>
  <transition name="fade" @show-alert="showAlert">
    <div v-if="visible" class="flex items-center" :class="textColor">
      <component :is="icon" class="h-6 w-6" aria-hidden="true" />
      <span class="inline-block ml-1">{{ alertMessage }}</span>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { CheckCircleIcon } from "@heroicons/vue/24/outline";
import { XMarkIcon } from "@heroicons/vue/20/solid";

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      alertType: "success",
      alertMessage: "Success!",
      section: "",
    }),
  },
  section: String,
});


const icon = computed(() => {
  return props.modelValue.alertType === "success" ? CheckCircleIcon : XMarkIcon;
});

const textColor = computed(() => {
  return props.modelValue.alertType === "success" ? "text-nearycyan-300" : "text-red-500";
});

const alertMessage = computed(() => {
  return props.modelValue.alertMessage;
});

const visible = ref(false);

const showAlert = () => {
  visible.value = true;
  setTimeout(() => {
    visible.value = false;
  }, 7000);
};

watch(
  () => props.modelValue,
  () => {
    if (!props.modelValue.section || props.modelValue.section === props.section) {
      showAlert();
    }
  },
  { deep: true }
);

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
