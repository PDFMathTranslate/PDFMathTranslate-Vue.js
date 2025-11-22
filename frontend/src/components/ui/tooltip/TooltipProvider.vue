<script setup>
import { TooltipProvider } from 'reka-ui'

const props = defineProps({
  delayDuration: { type: Number, default: 0 },
  skipDelayDuration: { type: Number, default: 300 },
  disableHoverableContent: { type: Boolean, default: false },
})
</script>

<template>
  <TooltipProvider v-bind="props">
    <slot />
  </TooltipProvider>
</template>

