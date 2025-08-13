<template>
  <footer class="mt-6 ml-6 text-sm text-slate-300 dark:text-slate-300 flex items-center gap-3">
    <div class="flex items-center gap-2">
      <span class="sr-only">Backend status</span>
      <div class="traffic">
        <span :class="['dot', activeClass('ok')]" aria-hidden="true"></span>
        <span :class="['dot', activeClass('error')]" aria-hidden="true"></span>
        <span :class="['dot', activeClass('warn')]" aria-hidden="true"></span>
      </div>
    </div>
    <div class="text-sm text-slate-300 dark:text-slate-300"> {{ healthText }}</div>
  </footer>
  
</template>

<script setup lang="ts">
const props = defineProps<{ healthText: string, healthLevel?: 'ok'|'warn'|'error'|'unknown' }>()

function activeClass(level: 'ok'|'warn'|'error') {
  return props.healthLevel === level ? `is-${level}` : ''
}
</script>

<style scoped>
.traffic {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 9999px;
  background-color: #e2e2e2; /* slate-600 as base off state */
  box-shadow: 0 0 0 rgba(0,0,0,0);
}
.dot.is-error {
  background-color: #ef4444; /* red-500 */
  box-shadow: 0 0 6px 2px rgba(239, 68, 68, 0.75);
}
.dot.is-warn {
  background-color: #f59e0b; /* amber-500 */
  box-shadow: 0 0 6px 2px rgba(245, 158, 11, 0.75);
}
.dot.is-ok {
  background-color: #22c55e; /* green-500 */
  box-shadow: 0 0 6px 2px rgba(34, 197, 94, 0.75);
}
</style>
