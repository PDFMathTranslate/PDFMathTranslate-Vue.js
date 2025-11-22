<script setup>
import { TooltipTrigger } from 'reka-ui'

const props = defineProps({
  asChild: { type: Boolean, required: false, default: false },
  as: { type: String, required: false },
})
</script>

<template>
  <TooltipTrigger v-bind="props">
    <slot />
  </TooltipTrigger>
</template>

