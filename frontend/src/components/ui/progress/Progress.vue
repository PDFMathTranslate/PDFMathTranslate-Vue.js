<script setup>
import { computed } from 'vue'
import { cn } from "@/lib/utils";

const props = defineProps({
  value: { type: Number, required: false, default: 0 },
  max: { type: Number, required: false, default: 100 },
  class: { type: null, required: false },
});

const percentage = computed(() => {
  const val = Math.min(Math.max(props.value, 0), props.max);
  return (val / props.max) * 100;
});
</script>

<template>
  <div
    :class="
      cn(
        'relative h-2 w-full overflow-hidden rounded-full bg-primary/20',
        props.class,
      )
    "
  >
    <div
      class="h-full w-full flex-1 bg-primary transition-all"
      :style="{ transform: `translateX(-${100 - percentage}%)` }"
    />
  </div>
</template>

