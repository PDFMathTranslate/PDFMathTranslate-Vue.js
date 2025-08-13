<template>
  <div class="max-w-6xl mx-auto p-6">
    <AppHeader />

    <ControlsPanel
      v-model:lang-in="langIn"
      v-model:lang-out="langOut"
      :lang-options="langOptions"
      :has-pending="hasPending"
      :is-working="isWorking"
      :has-files="!!jobs.length"
      @files-selected="onFiles"
      @start-all="startAll"
      @cancel-all="cancelAll"
    />

    <JobsList
      :jobs="jobs"
      @cancel-job="cancelJob"
      @download="download"
    />

    <AppFooter :health-text="healthText" :health-level="healthLevel" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import AppHeader from './components/AppHeader.vue'
import ControlsPanel from './components/ControlsPanel.vue'
import JobsList from './components/JobsList.vue'
import AppFooter from './components/AppFooter.vue'
import type { Job, LanguageOptions } from './types'

const langOptions: LanguageOptions = {
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
const jobs = ref<Job[]>([])
const healthCode = ref<number | null>(null)
let healthTimer: number | null = null

const isWorking = computed(() => jobs.value.some(j => j.state === 'PENDING' || j.state === 'PROGRESS'))
const hasPending = computed(() => jobs.value.some(j => j.state === 'PENDING'))

function onFiles(droppedFiles: File[]) {
  const pdfs = droppedFiles.filter(isPdf).filter(f => f.size > 0)
  if (!pdfs.length) return

  if (pdfs.length === 1) {
    const f = pdfs[0]
    const job: Job = {
      localId: `${f.name}-${Date.now()}-${Math.random()}`,
      file: f,
      state: 'PENDING',
      previewUrl: URL.createObjectURL(f),
    }
    jobs.value.push(job)
    // Auto-start single file immediately
    startJob(job)
  } else {
    for (const f of pdfs) {
      const job: Job = {
        localId: `${f.name}-${Date.now()}-${Math.random()}`,
        file: f,
        state: 'PENDING',
        previewUrl: URL.createObjectURL(f),
      }
      jobs.value.push(job)
    }
    // Start all pending jobs
    startAll()
  }
}

async function startAll() {
  for (const job of jobs.value) {
    if (job.state !== 'PENDING') continue
    await startJob(job)
  }
}

async function startJob(job: Job) {
  try {
    if (!job.file || job.file.size === 0) {
      job.state = 'REVOKED'
      return
    }
    const form = new FormData()
    form.append('file', job.file)
    form.append('data', JSON.stringify({ lang_in: langIn.value, lang_out: langOut.value, service: 'google', thread: 4 }))
    const resp = await fetch('/v1/translate', { method: 'POST', body: form })
    if (!resp.ok) {
      job.state = 'REVOKED'
      return
    }
    const data = await resp.json().catch(() => null)
    if (!data || !data.id) {
      job.state = 'REVOKED'
      return
    }
    job.id = data.id
    job.state = 'PROGRESS'
    job.pollTimer = window.setInterval(() => poll(job), 1000)
  } catch {
    job.state = 'REVOKED'
  }
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

// progress calculation moved into JobCard component

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
  if (healthCode.value && healthCode.value >= 400 && healthCode.value < 500) return `Client Error (${healthCode.value})`
  if (healthCode.value && healthCode.value >= 500) return `Server Stopped (${healthCode.value})`
  return 'Unknown'
})

const healthLevel = computed<'ok'|'warn'|'error'|'unknown'>(() => {
  if (healthCode.value === 200) return 'ok'
  if (healthCode.value && healthCode.value >= 400 && healthCode.value < 500) return 'warn'
  if (healthCode.value && healthCode.value >= 500) return 'error'
  return 'nknown'
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

function isPdf(f: File) {
  return f && (f.type === 'application/pdf' || /\.pdf$/i.test(f.name))
}
</script>

<style>
  body { margin: 0; }
</style>


