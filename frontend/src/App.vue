<script setup>
import { ref, onMounted, reactive, computed, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import Header from '@/components/Header.vue'
import TranslationOptions from '@/components/TranslationOptions.vue'
import ApplicationSettings from '@/components/ApplicationSettings.vue'
import ProjectInfo from '@/components/ProjectInfo.vue'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import api from '@/services/api'
import { Loader2, ChevronDown, ChevronUp, Download, RefreshCw, Check } from 'lucide-vue-next'
import VuePdfEmbed from 'vue-pdf-embed'

const { t, locale } = useI18n()

const config = ref(null)
const selectedFile = ref(null)
const isTranslating = ref(false)
const taskId = ref(null)
const taskStatus = ref(null)
const logs = ref([])
const downloadUrl = ref(null)
const monoPdfUrl = ref(null)
const dualPdfUrl = ref(null)
const isLogsExpanded = ref(false)
const overallProgress = ref(null)
const isTranslationComplete = computed(() => taskStatus.value === 'completed')
const serviceStatus = ref('ready') // ready, busy, error
const showSettings = ref(false)
const isSaved = ref(false)
const isLanguageSwitching = ref(false)

// Load preferences from localStorage
const loadPreferences = () => {
  const stored = localStorage.getItem('translationPreferences')
  if (stored) {
    try {
      return JSON.parse(stored)
    } catch (e) {
      console.error('Failed to parse stored preferences:', e)
    }
  }
  return null
}

// Default preferences
const defaultPreferences = {
  source: 'File',
  langFrom: 'English',
  langTo: 'Simplified Chinese',
  service: 'SiliconFlowFree', // Default service
  url: '', // URL for Link source type
  // Output preferences
  // By default, both mono and dual outputs are enabled
  // noMono: false means mono output is enabled
  // noDual: false means dual/bilingual output is enabled
  noMono: false,
  noDual: false,
  dualTranslateFirst: false,
  useAlternatingPagesDual: false,
  // Rate limiting
  qps: undefined,
  poolMaxWorkers: undefined,
  termQps: undefined,
  termPoolMaxWorkers: undefined,
  // PDF processing
  pages: undefined,
  watermarkOutputMode: 'both',
  maxPagesPerPart: undefined,
  // Translation options
  minTextLength: undefined,
  ignoreCache: false,
  customSystemPrompt: undefined,
  // Advanced options
  translateTableText: false,
  skipScannedDetection: false,
  ocrWorkaround: false,
  autoEnableOcrWorkaround: false,
}

const translationParams = reactive({
  ...defaultPreferences,
  ...(loadPreferences() || {}),
})

// Save preferences to localStorage whenever they change
let saveTimeout
watch(
  translationParams,
  (newParams) => {
    // Create a clean copy without undefined values for storage
    const toStore = { ...newParams }
    // Remove undefined values
    Object.keys(toStore).forEach(key => {
      if (toStore[key] === undefined) {
        delete toStore[key]
      }
    })
    localStorage.setItem('translationPreferences', JSON.stringify(toStore))

    // Show saved indicator
    isSaved.value = true
    if (saveTimeout) clearTimeout(saveTimeout)
    saveTimeout = setTimeout(() => {
      isSaved.value = false
    }, 1000)
  },
  { deep: true }
)

onMounted(async () => {
  try {
    const response = await api.getConfig()
    config.value = response.data
    serviceStatus.value = 'ready'
    // Initialize defaults if needed
  } catch (error) {
    console.error('Failed to load config:', error)
    serviceStatus.value = 'error'
  }
})

const handleFileSelected = async (file) => {
  console.log('File selected:', file?.name, 'Source:', translationParams.source, 'Is translating:', isTranslating.value)
  selectedFile.value = file
  // Ensure source is set to 'File' when a file is selected
  if (file) {
    translationParams.source = 'File'
  }
  // Automatically start translation when a file is selected/dropped
  if (file && !isTranslating.value) {
    // Use nextTick to ensure the file is properly set before starting translation
    await nextTick()
    console.log('Auto-starting translation for file:', file.name)
    startTranslation()
  } else {
    console.log('Translation not started. Reasons:', {
      hasFile: !!file,
      isTranslating: isTranslating.value,
      source: translationParams.source
    })
  }
}

// Watch for URL changes to auto-start translation for Link source
watch(() => translationParams.url, async (newUrl, oldUrl) => {
  // Only auto-start if URL is valid and not empty, and we're not already translating
  if (newUrl && newUrl.trim() && !isTranslating.value && translationParams.source === 'Link' && newUrl !== oldUrl) {
    // Debounce to avoid starting multiple times
    await nextTick()
    setTimeout(() => {
      if (translationParams.url && translationParams.url.trim() && !isTranslating.value) {
        startTranslation()
      }
    }, 500)
  }
})

// Extract overall_progress from logs
const extractOverallProgress = (logEntries) => {
  if (!logEntries || logEntries.length === 0) return null
  
  // Look for progress events in logs (progress_start, progress_update, progress_end)
  // Log format: {'type': 'progress_end', ..., 'overall_progress': 94.41624365482232, ...}
  for (let i = logEntries.length - 1; i >= 0; i--) {
    const log = logEntries[i]
    if (typeof log !== 'string') continue
    
    // Check if this is a progress event
    if (log.includes('progress_start') || log.includes('progress_update') || log.includes('progress_end')) {
      // Extract overall_progress value using regex
      // Pattern: 'overall_progress': <number> or "overall_progress": <number>
      // Handle both single and double quotes, and decimal numbers with full precision
      const match = log.match(/['"]overall_progress['"]\s*[:=]\s*(\d+\.?\d+|\d+)/)
      if (match && match[1]) {
        const progressValue = parseFloat(match[1])
        // Ensure it's a valid number
        if (!isNaN(progressValue) && isFinite(progressValue)) {
          return progressValue
        }
      }
    }
  }
  return null
}

// Watch logs to extract progress
watch(logs, (newLogs) => {
  const progress = extractOverallProgress(newLogs)
  if (progress !== null) {
    overallProgress.value = progress
  }
}, { deep: true })

const startTranslation = async () => {
  if (translationParams.source === 'File' && !selectedFile.value) return
  if (translationParams.source === 'Link' && !translationParams.url) return
  
  isTranslating.value = true
  serviceStatus.value = 'busy'
  logs.value = []
  overallProgress.value = null
  downloadUrl.value = null
  monoPdfUrl.value = null
  dualPdfUrl.value = null
  taskStatus.value = null
  
  try {
    let fileId
    
    if (translationParams.source === 'File') {
      // 1. Upload File
      const uploadResponse = await api.uploadFile(selectedFile.value)
      fileId = uploadResponse.data.file_id
    } else {
      // For URL, we might need a different API endpoint or pass URL directly
      // This depends on your backend API structure
      // For now, assuming URL can be passed directly
      fileId = translationParams.url
    }
    
    // 2. Start Translation
    const params = {
      file_id: fileId,
      lang_from: translationParams.langFrom,
      lang_to: translationParams.langTo,
      service: translationParams.service,
      // Output preferences
      no_mono: translationParams.noMono || undefined,
      no_dual: translationParams.noDual || undefined,
      dual_translate_first: translationParams.dualTranslateFirst || undefined,
      use_alternating_pages_dual: translationParams.useAlternatingPagesDual || undefined,
      // Rate limiting
      qps: translationParams.qps,
      pool_max_workers: translationParams.poolMaxWorkers,
      term_qps: translationParams.termQps,
      term_pool_max_workers: translationParams.termPoolMaxWorkers,
      // PDF processing
      pages: translationParams.pages,
      watermark_output_mode: translationParams.watermarkOutputMode,
      max_pages_per_part: translationParams.maxPagesPerPart,
      // Translation options
      min_text_length: translationParams.minTextLength,
      ignore_cache: translationParams.ignoreCache || undefined,
      custom_system_prompt: translationParams.customSystemPrompt,
      // Advanced options
      translate_table_text: translationParams.translateTableText || undefined,
      skip_scanned_detection: translationParams.skipScannedDetection || undefined,
      ocr_workaround: translationParams.ocrWorkaround || undefined,
      auto_enable_ocr_workaround: translationParams.autoEnableOcrWorkaround || undefined,
    }
    
    // Remove undefined values
    Object.keys(params).forEach(key => {
      if (params[key] === undefined || params[key] === '') {
        delete params[key]
      }
    })
    
    const translateResponse = await api.translate(params)
    taskId.value = translateResponse.data.task_id
    
    // 3. Poll Status
    pollStatus()
    
  } catch (error) {
    console.error('Translation failed:', error)
    isTranslating.value = false
    serviceStatus.value = 'error'
    logs.value.push(`Error: ${error.message}`)
  }
}

const pollStatus = async () => {
  if (!taskId.value) return
  
  try {
    const response = await api.getStatus(taskId.value)
    taskStatus.value = response.data.status
    logs.value = response.data.logs || []
    
    if (taskStatus.value === 'completed') {
      isTranslating.value = false
      serviceStatus.value = 'ready'
      overallProgress.value = 100
      // Set download URLs for mono and dual files
      if (response.data.mono_pdf_path) {
        monoPdfUrl.value = `/api/download_task/${taskId.value}/mono`
      }
      if (response.data.dual_pdf_path) {
        dualPdfUrl.value = `/api/download_task/${taskId.value}/dual`
      }
      // Fallback to old downloadUrl for backward compatibility
      if (!monoPdfUrl.value && !dualPdfUrl.value) {
        downloadUrl.value = `/api/download_task/${taskId.value}`
      }
    } else if (taskStatus.value === 'failed') {
      isTranslating.value = false
      serviceStatus.value = 'error'
      overallProgress.value = null
      logs.value.push(`Error: ${response.data.error}`)
    } else {
      // Extract progress from updated logs
      const progress = extractOverallProgress(logs.value)
      if (progress !== null) {
        overallProgress.value = progress
      }
      setTimeout(pollStatus, 1000)
    }
  } catch (error) {
    console.error('Status check failed:', error)
    isTranslating.value = false
    serviceStatus.value = 'error'
  }
}

const resetTranslation = () => {
  isTranslating.value = false
  taskId.value = null
  taskStatus.value = null
  logs.value = []
  overallProgress.value = null
  downloadUrl.value = null
  monoPdfUrl.value = null
  dualPdfUrl.value = null
  selectedFile.value = null
}

const handleDownload = async (downloadFn) => {
    try {
        if (!taskId.value) return;
        const response = await downloadFn(taskId.value);
        const blob = new Blob([response.data], { type: response.headers['content-type'] });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        let filename = 'download.pdf';
        const disposition = response.headers['content-disposition'];
        if (disposition) {
            const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/);
            if (utf8Match) {
                filename = decodeURIComponent(utf8Match[1]);
            } else {
                const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }
        }
        
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        
        setTimeout(() => {
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        }, 100);
    } catch (error) {
        console.error('Download failed:', error);
    }
}

const downloadResult = async () => {
    await handleDownload(api.downloadTaskResult);
}

const downloadMono = async () => {
    await handleDownload(api.downloadTaskMono);
}

const downloadDual = async () => {
    await handleDownload(api.downloadTaskDual);
}

const handleLanguageChange = (langCode) => {
  isLanguageSwitching.value = true
  setTimeout(() => {
    locale.value = langCode
    localStorage.setItem('locale', langCode)
    setTimeout(() => {
      isLanguageSwitching.value = false
    }, 50)
  }, 200)
}
</script>

<template>
  <div 
    class="min-h-screen bg-background font-sans antialiased overflow-x-hidden transition-opacity duration-200 flex flex-col"
    :class="{ 'opacity-0': isLanguageSwitching, 'opacity-100': !isLanguageSwitching }"
  >
    <Header :show-settings="showSettings" @toggle-settings="showSettings = !showSettings" @change-language="handleLanguageChange" />
    
    <main class="container py-10 mx-auto px-6 flex-1">
      <Transition name="fade" mode="out-in">
        <div v-if="!showSettings" key="main" class="max-w-4xl mx-auto space-y-8">
          <!-- Translation Options - Hidden when translation starts or is in progress -->
          <Card v-if="!isTranslating && overallProgress === null && !isTranslationComplete">
            <CardHeader>
              <CardTitle>{{ t('translation.options') }}</CardTitle>
              <CardDescription>{{ t('translation.optionsDescription') }}</CardDescription>
            </CardHeader>
            <CardContent>
              <TranslationOptions v-model="translationParams" :config="config" @file-selected="handleFileSelected" />
            </CardContent>
          </Card>
          
          <!-- Progress Box - Show during translation -->
          <Card v-if="isTranslating || (overallProgress !== null && !isTranslationComplete)">
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Loader2 v-if="isTranslating" class="h-5 w-5 animate-spin" />
                {{ t('translation.translating') }}
              </CardTitle>
              <CardDescription v-if="overallProgress !== null">
                {{ overallProgress.toFixed(1) }}% {{ t('translation.complete') || 'complete' }}
              </CardDescription>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="space-y-2">
                  <Progress :value="overallProgress !== null ? overallProgress : 0" class="w-full" />
              </div>
              
              <div v-if="logs.length > 0" class="flex flex-col gap-2">
                  <Button 
                      variant="ghost" 
                      size="sm" 
                      class="w-fit h-auto p-1 text-xs text-muted-foreground"
                      @click="isLogsExpanded = !isLogsExpanded"
                  >
                      <ChevronDown v-if="!isLogsExpanded" class="h-3 w-3 mr-1" />
                      <ChevronUp v-else class="h-3 w-3 mr-1" />
                      {{ isLogsExpanded ? 'Hide' : 'Show' }} Logs ({{ logs.length }})
                  </Button>
                  <div v-show="isLogsExpanded" class="p-4 rounded-md max-h-40 overflow-y-auto text-xs font-mono bg-muted/50">
                      <div v-for="(log, index) in logs" :key="index">{{ log }}</div>
                  </div>
              </div>
            </CardContent>
          </Card>
          
          <!-- Translation Result - Show when translation is complete -->
          <Card v-if="isTranslationComplete">
            <CardHeader>
              <CardTitle>{{ t('translation.result') }}</CardTitle>
              <CardDescription>{{ t('translation.resultDescription') }}</CardDescription>
            </CardHeader>
            <CardContent class="space-y-6">
              <!-- Download Buttons -->
              <div class="flex flex-wrap gap-4">
                <Button 
                  v-if="monoPdfUrl" 
                  variant="default" 
                  @click="downloadMono"
                  class="flex items-center gap-2"
                >
                  <Download class="h-4 w-4" />
                  {{ t('translation.downloadMono') }}
                </Button>
                <Button 
                  v-if="dualPdfUrl" 
                  variant="outline" 
                  @click="downloadDual"
                  class="flex items-center gap-2"
                >
                  <Download class="h-4 w-4" />
                  {{ t('translation.downloadDual') }}
                </Button>
                <!-- Fallback for old downloadUrl -->
                <Button 
                  v-if="downloadUrl && !monoPdfUrl && !dualPdfUrl" 
                  variant="outline" 
                  @click="downloadResult"
                  class="flex items-center gap-2"
                >
                  <Download class="h-4 w-4" />
                  {{ t('translation.download') }}
                </Button>
                
                <Button 
                  variant="secondary" 
                  @click="resetTranslation"
                  class="flex items-center gap-2"
                >
                  <RefreshCw class="h-4 w-4" />
                  {{ t('translation.restart') || 'Start New Translation' }}
                </Button>
              </div>

              <!-- PDF Preview - Show first page of mono PDF -->
              <div v-if="monoPdfUrl" class="space-y-4">
                <div class="border rounded-lg overflow-hidden bg-muted/50 p-4 pdf-preview-container" style="max-height: 600px; overflow-y: auto;">
                  <VuePdfEmbed 
                    :source="monoPdfUrl"
                    class="w-full"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div v-else key="settings" class="max-w-3xl mx-auto">
          <Card class="h-full">
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                {{ t('settings.title') }}
                <Transition name="fade">
                  <Check v-if="isSaved" class="h-4 w-4 text-green-500" />
                </Transition>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ApplicationSettings v-model="translationParams" />
            </CardContent>
          </Card>
        </div>
      </Transition>
    </main>

    <ProjectInfo :status="serviceStatus" />
  </div>
</template>

<style scoped>
/* Hide all PDF pages except the first one in the preview */
.pdf-preview-container :deep(.vue-pdf-embed > div:not(:first-child)) {
  display: none;
}

.pdf-preview-container :deep(.vue-pdf-embed canvas:not(:first-of-type)) {
  display: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
