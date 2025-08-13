<template>
  <div class="card">
    <div class="flex items-center justify-between gap-3">
      <div class="truncate">
        <strong class="truncate block">{{ job.file.name }}</strong>
        <span class="text-xs text-slate-500">{{ job.state }}</span>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-outline" v-if="job.state==='PROGRESS'" @click="$emit('cancel-job', job)">Cancel</button>
        <button class="btn btn-primary" v-if="job.state==='SUCCESS'" @click="$emit('download', job, 'mono')">Download -mono</button>
        <button class="btn btn-primary" v-if="job.state==='SUCCESS'" @click="$emit('download', job, 'dual')">Download -dual</button>
      </div>
    </div>
    <div class="mt-3" v-if="job.state==='PROGRESS' && job.info">
      <div class="h-2 bg-slate-200 dark:bg-slate-700 rounded">
        <div class="h-2 bg-accent-500 rounded" :style="{width: progressPercent + '%'}"></div>
      </div>
      <small class="text-slate-500">{{ job.info.n }} / {{ job.info.total }}</small>
    </div>
    <div class="mt-3 grid md:grid-cols-1 gap-3" v-if="job.previewUrl">
      <PdfViewer class="md:grid-rows-4" :src="job.previewUrl" />
      <PdfViewer class="md:grid-rows-4" v-if="job.outputPreviewUrl" :src="job.outputPreviewUrl" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Job } from '../types'
import PdfViewer from './PdfViewer.vue'

const props = defineProps<{ job: Job }>()

const progressPercent = computed(() => {
  if (!props.job.info || !props.job.info.total) return 0
  return Math.round((props.job.info.n / props.job.info.total) * 100)
})
</script>


