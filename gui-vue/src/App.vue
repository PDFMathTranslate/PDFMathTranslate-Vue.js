<template>
  <div class="max-w-6xl mx-auto p-6">
    <header class="mb-6">
      <h1 class="text-2xl font-semibold text-accent-700 dark:text-accent-200">PDFMathTranslate</h1>
      <p class="text-sm text-slate-500 dark:text-slate-400">Translate PDFs with preserved format</p>
    </header>

    <section class="card">
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Input Language</label>
          <select v-model="langIn" class="w-full rounded-lg border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900">
            <option v-for="(code, name) in langOptions" :key="name" :value="code">{{ name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Output Language</label>
          <select v-model="langOut" class="w-full rounded-lg border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900">
            <option v-for="(code, name) in langOptions" :key="name" :value="code">{{ name }}</option>
          </select>
        </div>
        <div class="sm:col-span-2 flex items-end gap-3">
          <input class="block w-full text-sm text-slate-900 dark:text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-accent-100 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-accent-700 hover:file:bg-accent-200 dark:file:bg-accent-700 dark:file:text-white" type="file" accept="application/pdf" multiple @change="onFiles" />
          <button class="btn btn-primary" :disabled="!files.length || !hasPending" @click="startAll">Start</button>
          <button class="btn btn-outline" :disabled="!isWorking" @click="cancelAll">Cancel</button>
        </div>
      </div>
    </section>

    <section class="mt-6 space-y-4" v-if="jobs.length">
      <div class="card" v-for="job in jobs" :key="job.localId">
        <div class="flex items-center justify-between gap-3">
          <div class="truncate">
            <strong class="truncate block">{{ job.file.name }}</strong>
            <span class="text-xs text-slate-500">{{ job.state }}</span>
          </div>
          <div class="flex gap-2">
            <button class="btn btn-outline" v-if="job.state==='PROGRESS'" @click="cancelJob(job)">Cancel</button>
            <button class="btn btn-primary" v-if="job.state==='SUCCESS'" @click="download(job, 'mono')">Download -mono</button>
            <button class="btn btn-primary" v-if="job.state==='SUCCESS'" @click="download(job, 'dual')">Download -dual</button>
          </div>
        </div>
        <div class="mt-3" v-if="job.state==='PROGRESS' && job.info">
          <div class="h-2 bg-slate-200 dark:bg-slate-700 rounded">
            <div class="h-2 bg-accent-500 rounded" :style="{width: progressPercent(job) + '%'}"></div>
          </div>
          <small class="text-slate-500">{{ job.info.n }} / {{ job.info.total }}</small>
        </div>
        <div class="mt-3 grid md:grid-cols-1 gap-3" v-if="job.previewUrl">
          <PdfViewer class="md:grid-rows-4" :src="job.previewUrl" />
          <PdfViewer class="md:grid-rows-4" v-if="job.outputPreviewUrl" :src="job.outputPreviewUrl" />
        </div>
      </div>
    </section>

    <footer class="mt-6 text-sm text-slate-500 dark:text-slate-400">
      <div class="text-sm text-slate-600 dark:text-slate-300">Backend: {{ healthText }}</div>
    </footer>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import PdfViewer from './components/PdfViewer.vue'

type JobState = 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE' | 'REVOKED'

interface Job {
  localId: string
  file: File
  id?: string
  state: JobState
  info?: { n: number; total: number }
  previewUrl?: string
  outputPreviewUrl?: string
  pollTimer?: number
}

const langOptions: Record<string, string> = {
  'Simplified Chinese': 'zh',
  'Traditional Chinese': 'zh-TW',
  'English': 'en',
  'French': 'fr',
  'German': 'de',
  'Japanese': 'ja',
  'Korean': 'ko',
  'Russian': 'ru',
  'Spanish': 'es',
  'Italian': 'it',
}

const langIn = ref('en')
const langOut = ref('zh')
const files = ref<File[]>([])
const jobs = ref<Job[]>([])
const healthCode = ref<number | null>(null)
let healthTimer: number | null = null

const isWorking = computed(() => jobs.value.some(j => j.state === 'PENDING' || j.state === 'PROGRESS'))
const hasPending = computed(() => jobs.value.some(j => j.state === 'PENDING'))

function onFiles(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files) return
  files.value = Array.from(input.files)
  jobs.value = files.value.map((f) => ({
    localId: `${f.name}-${Date.now()}-${Math.random()}`,
    file: f,
    state: 'PENDING',
    previewUrl: URL.createObjectURL(f),
  }))
  // Auto-start translation once files are chosen
  startAll()
}

async function startAll() {
  for (const job of jobs.value) {
    if (job.state !== 'PENDING') continue
    await startJob(job)
  }
}

async function startJob(job: Job) {
  const form = new FormData()
  form.append('file', job.file)
  form.append('data', JSON.stringify({ lang_in: langIn.value, lang_out: langOut.value, service: 'google', thread: 4 }))
  const resp = await fetch('/v1/translate', { method: 'POST', body: form })
  const data = await resp.json()
  job.id = data.id
  job.state = 'PROGRESS'
  job.pollTimer = window.setInterval(() => poll(job), 1000)
}

async function poll(job: Job) {
  if (!job.id) return
  const r = await fetch(`/v1/translate/${job.id}`)
  const j = await r.json()
  job.state = j.state
  job.info = j.info
  if (j.state === 'SUCCESS' || j.state === 'FAILURE' || j.state === 'REVOKED') {
    if (job.pollTimer) window.clearInterval(job.pollTimer)
    if (j.state === 'SUCCESS') {
      // switch preview to translated mono-lingual version
      const monoBlob = await (await fetch(`/v1/translate/${job.id}/mono`)).blob()
      job.previewUrl = URL.createObjectURL(monoBlob)
      job.outputPreviewUrl = undefined
    }
  }
}

function progressPercent(job: Job) {
  if (!job.info || !job.info.total) return 0
  return Math.round((job.info.n / job.info.total) * 100)
}

async function cancelJob(job: Job) {
  if (!job.id) return
  await fetch(`/v1/translate/${job.id}`, { method: 'DELETE' })
  job.state = 'REVOKED'
}

async function cancelAll() {
  await Promise.all(jobs.value.map(j => j.id ? fetch(`/v1/translate/${j.id}`, { method: 'DELETE' }) : Promise.resolve()))
  jobs.value.forEach(j => j.state = 'REVOKED')
}

async function download(job: Job, type: 'mono'|'dual') {
  if (!job.id) return
  const resp = await fetch(`/v1/translate/${job.id}/${type}`)
  const blob = await resp.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const suffix = type === 'mono' ? '-mono' : '-dual'
  a.download = job.file.name.replace(/\.pdf$/i, `${suffix}.pdf`)
  a.click()
  URL.revokeObjectURL(url)
}

async function checkHealth() {
  try {
    const resp = await fetch('/v1/health', { method: 'GET' })
    healthCode.value = resp.status
  } catch {
    healthCode.value = 500
  }
}

const healthText = computed(() => {
  if (healthCode.value === 200) return 'Healthy'
  if (healthCode.value && healthCode.value >= 400 && healthCode.value < 500) return `Client error (${healthCode.value})`
  if (healthCode.value && healthCode.value >= 500) return `Server error (${healthCode.value})`
  return 'Unknown'
})

onMounted(() => {
  checkHealth()
  healthTimer = window.setInterval(() => checkHealth(), 2000)
})

onBeforeUnmount(() => {
  if (healthTimer) {
    window.clearInterval(healthTimer)
    healthTimer = null
  }
})
</script>

<style>
  body { margin: 0; }
</style>


