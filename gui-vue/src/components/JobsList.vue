<template>
  <section class="mt-6 space-y-4" v-if="jobs.length">
    <JobCard v-for="job in jobs" :key="job.localId" :job="job" @cancel-job="$emit('cancel-job', $event)" @download="(job, type) => $emit('download', job, type)" />
  </section>
</template>

<script setup lang="ts">
import JobCard from './JobCard.vue'
import type { Job } from '../types'

defineProps<{ jobs: Job[] }>()

defineEmits<{
  (e: 'cancel-job', job: Job): void
  (e: 'download', job: Job, type: 'mono' | 'dual'): void
}>()
</script>


