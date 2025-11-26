<script setup>
import { ref, onMounted, onUnmounted, reactive, computed, watch, watchEffect, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import Header from '@/components/Header.vue'
import TranslationOptions from '@/components/TranslationOptions.vue'
import ApplicationSettings from '@/components/ApplicationSettings.vue'
import ProjectInfo from '@/components/ProjectInfo.vue'
import DevStatsCard from '@/components/DevStatsCard.vue'
import DevSettings from '@/components/DevSettings.vue'
import ServiceChangerCard from '@/components/ServiceChangerCard.vue'
import BatchProgressCard from '@/components/BatchProgressCard.vue'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import api from '@/services/api'
import { Loader2, ChevronDown, ChevronUp, Download, RefreshCw, Check, Square, AlertCircle, FileText, Link as LinkIcon, Trash2, Zap, X } from 'lucide-vue-next'
import VuePdfEmbed from 'vue-pdf-embed'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

import { useColorMode, onKeyStroke } from '@vueuse/core'

const { t, locale } = useI18n()

const colorMode = useColorMode({
  disableTransition: false  // Enable smooth 300ms color transitions
})

// Sync meta theme-color with color mode
watch(colorMode, (newMode) => {
  const themeColor = newMode === 'dark' ? '#18181b' : '#ffffff'
  const metaThemeColor = document.querySelector('meta[name="theme-color"]')
  if (metaThemeColor) {
    metaThemeColor.setAttribute('content', themeColor)
  }
}, { immediate: true })

const config = ref(null)
const selectedFile = ref(null)
const isTranslating = ref(false)
const taskId = ref(null)
const taskStatus = ref(null)
const logs = ref([])
const stages = ref([])
const activeStageIndex = computed(() => {
  const index = stages.value.findIndex(s => s.status === 'active')
  if (index !== -1) return index
  if (stages.value.length > 0 && stages.value.every(s => s.status === 'completed')) return stages.value.length - 1
  return 0
})
const currentStage = ref(null)
const downloadUrl = ref(null)
const monoPdfUrl = ref(null)
const dualPdfUrl = ref(null)
const isLogsExpanded = ref(false)
const overallProgress = ref(null)
const isTranslationComplete = computed(() => taskStatus.value === 'completed')

// Check if user is on the index/home view (no translation in progress or completed)
const isOnIndex = computed(() => 
  !isTranslating.value && 
  overallProgress.value === null && 
  taskStatus.value !== 'completed' && 
  taskStatus.value !== 'failed'
)

// Check if running in PWA mode (standalone or window-controls-overlay)
const isPWA = computed(() => {
  if (typeof window === 'undefined') return false
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches
  const isWcoMode = window.matchMedia('(display-mode: window-controls-overlay)').matches
  return isStandalone || isWcoMode
})

// Ensure installed PWA windows display a consistent title
watchEffect(() => {
  if (isPWA.value && typeof document !== 'undefined') {
    document.title = 'PDFMathTranslate'
  }
})
const serviceStatus = ref('ready') // ready, busy, error
const healthInfo = ref(null) // Store health information including CPU load
const showSettings = ref(false)
const isSaved = ref(false)
const isLanguageSwitching = ref(false)
const openAccordionItem = ref('')

// Recent translated files
const recentFiles = ref([])

// Development mode
const devMode = ref(false)
const devModeFromServer = ref(false)
const escPressCount = ref(0)
const escPressTimeout = ref(null)
const DEV_MODE_ESC_PRESSES = 4
const ESC_PRESS_TIMEOUT_MS = 3000

// Load dev mode preference from localStorage
const loadDevModePreference = () => {
  const stored = localStorage.getItem('devMode')
  if (stored) {
    return stored === 'true'
  }
  return false
}

// Save dev mode preference
const saveDevModePreference = (enabled) => {
  localStorage.setItem('devMode', enabled ? 'true' : 'false')
}

// Toggle dev mode
const toggleDevMode = () => {
  devMode.value = !devMode.value
  saveDevModePreference(devMode.value)
}

// Preview URL for selected file
const selectedFilePreviewUrl = ref(null)

watch(selectedFile, (newFile) => {
    // Revoke previous URL to avoid memory leaks
    if (selectedFilePreviewUrl.value) {
        URL.revokeObjectURL(selectedFilePreviewUrl.value)
        selectedFilePreviewUrl.value = null
    }
    
    if (newFile && newFile instanceof File) {
        selectedFilePreviewUrl.value = URL.createObjectURL(newFile)
    }
})

// Clean up on unmount
onUnmounted(() => {
    if (selectedFilePreviewUrl.value) {
        URL.revokeObjectURL(selectedFilePreviewUrl.value)
    }
})

const isWco = ref(false)

let wcoMql = null
let standaloneMql = null

const checkWco = () => {
  // Only enable WCO if we are in the correct display mode or the API reports it's visible
  // 1. Check modern media query
  const isWcoMode = window.matchMedia('(display-mode: window-controls-overlay)').matches
  
  // 2. Check if we are in standalone and the overlay is visible via API
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches
  const isApiVisible = 'windowControlsOverlay' in navigator && 
      navigator.windowControlsOverlay && 
                       navigator.windowControlsOverlay.visible

  if (isWcoMode || (isStandalone && isApiVisible)) {
    isWco.value = true
  } else {
    isWco.value = false
  }
}

// Health monitoring
const healthPollInterval = ref(null)

const fetchHealthInfo = async () => {
  try {
    const response = await api.getHealth()
    healthInfo.value = response.data
    if (response.data.status) {
      serviceStatus.value = response.data.status
    }
  } catch (error) {
    console.error('Failed to fetch health info:', error)
    serviceStatus.value = 'error'
    healthInfo.value = { status: 'error', error: error.message }
  }
}

onMounted(async () => {
  // Initialize WCO detection
  checkWco()
  
  if ('windowControlsOverlay' in navigator) {
    navigator.windowControlsOverlay.addEventListener('geometrychange', checkWco)
  }
  
  // Listen for display mode changes
  wcoMql = window.matchMedia('(display-mode: window-controls-overlay)')
  standaloneMql = window.matchMedia('(display-mode: standalone)')
  
  try {
    wcoMql.addEventListener('change', checkWco)
    standaloneMql.addEventListener('change', checkWco)
  } catch (e) {
    // Fallback for older browsers that use addListener
    wcoMql.addListener(checkWco)
    standaloneMql.addListener(checkWco)
  }

  try {
    const response = await api.getConfig()
    config.value = response.data
    serviceStatus.value = 'ready'
    
    // Check if dev mode was enabled via CLI (--gui-dev)
    if (response.data.dev_mode) {
      devModeFromServer.value = true
      devMode.value = true
    } else {
      // Load from localStorage if not from server
      devMode.value = loadDevModePreference()
    }
  } catch (error) {
    console.error('Failed to load config:', error)
    serviceStatus.value = 'error'
  }

  // Start health monitoring
  fetchHealthInfo() // Initial fetch
  healthPollInterval.value = setInterval(fetchHealthInfo, 2000) // Poll every 2 seconds
})

onUnmounted(() => {
  if ('windowControlsOverlay' in navigator) {
    navigator.windowControlsOverlay.removeEventListener('geometrychange', checkWco)
  }
  
  // Clean up media query listeners
  if (wcoMql) {
    try {
      wcoMql.removeEventListener('change', checkWco)
    } catch (e) {
      wcoMql.removeListener(checkWco)
    }
  }
  if (standaloneMql) {
    try {
      standaloneMql.removeEventListener('change', checkWco)
    } catch (e) {
      standaloneMql.removeListener(checkWco)
    }
  }

  // Clean up health polling
  if (healthPollInterval.value) {
    clearInterval(healthPollInterval.value)
  }
})

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
  // Translation backend mode: 'stable' (pdf2zh) or 'experimental' (pdf2zh_next)
  translationBackend: 'stable', // Default to stable mode
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
  watermarkOutputMode: 'no_watermark',
  maxPagesPerPart: undefined,
  // Translation options
  minTextLength: undefined,
  ignoreCache: false,
  customSystemPrompt: undefined,
  // Appearance
  accentColor: 'black',
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

// Apply accent color dynamically
watch(() => translationParams.accentColor, (newColor) => {
  if (newColor) {
    document.documentElement.setAttribute('data-accent', newColor)
  }
}, { immediate: true })

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
    
    const backends = response.data.backends || {}
    const savedBackend = loadPreferences()?.translationBackend
    const savedService = loadPreferences()?.service
    
    // Check for deprecated services and reset to default
    const deprecatedServices = ['Google', 'Bing']
    if (savedService && deprecatedServices.includes(savedService)) {
      console.log(`Service '${savedService}' is deprecated, switching to SiliconFlowFree`)
      translationParams.service = 'SiliconFlowFree'
    }
    
    // If user has stable saved but it's not available, switch to experimental
    if (savedBackend === 'stable' && backends.stable && !backends.stable.available) {
      console.log('Stable backend not available, switching to experimental')
      translationParams.translationBackend = 'experimental'
    }
    // Set default backend mode from server if not already set in localStorage
    else if (response.data.default_backend && !savedBackend) {
      translationParams.translationBackend = response.data.default_backend
    }
  } catch (error) {
    console.error('Failed to load config:', error)
    serviceStatus.value = 'error'
  }
})

const batchQueue = ref([])
const currentBatchIndex = ref(-1)
const isBatchMode = computed(() => batchQueue.value.length > 0)
const completedBatchCount = computed(() => batchQueue.value.filter(t => t.status === 'completed' || t.status === 'failed').length)
const isBatchComplete = computed(() => isBatchMode.value && batchQueue.value.length > 0 && batchQueue.value.every(t => t.status === 'completed' || t.status === 'failed'))

const resetBatch = () => {
  resetTranslation()
}

const retryBatch = () => {
  // Find failed tasks
  const failedTasks = batchQueue.value.filter(t => t.status === 'failed')
  if (failedTasks.length === 0) return

  // Reset their status
  failedTasks.forEach(t => {
    t.status = 'pending'
    t.progress = 0
    t.logs = []
    t.error = null
  })

  // Find the index of the first pending task (which was failed)
  const firstPendingIndex = batchQueue.value.findIndex(t => t.status === 'pending')
  if (firstPendingIndex !== -1) {
    currentBatchIndex.value = firstPendingIndex
    processNextTask()
  }
}

const handleFileSelected = async (files) => {
  // Handle single file or array of files
  const fileList = Array.isArray(files) ? files : [files]
  
  if (fileList.length === 0) return
  
  console.log('Files selected:', fileList.length, 'Source:', translationParams.source)
  
  // If multiple files or we already have a queue, treat as batch
  if (fileList.length > 1) {
    // Reset existing state
    resetTranslation()
    
    // Create tasks
    batchQueue.value = fileList.map((file, index) => ({
      id: Date.now() + index,
      file: file,
      status: 'pending',
      taskId: null,
      progress: 0,
      logs: [],
      stages: [],
      error: null,
      monoPdfUrl: null,
      dualPdfUrl: null
    }))
    
    translationParams.source = 'File'
    
    // Start batch
    await nextTick()
    startBatchTranslation()
  } else {
    // Single file - standard behavior
    const file = fileList[0]
    selectedFile.value = file
    if (file) {
      translationParams.source = 'File'
    }
    if (file && !isTranslating.value) {
      await nextTick()
      startTranslation()
    }
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

// Process logs to extract stages and progress
const processLogs = (logEntries) => {
  if (!logEntries || logEntries.length === 0) return

  let foundStages = [...stages.value]
  let current = currentStage.value
  let overall = overallProgress.value

  // Helper to parse Python-dict-like strings
  const parseLogEntry = (logStr) => {
    try {
      // Try standard JSON first
      if (logStr.startsWith('{') && logStr.includes('"type"')) {
         try { return JSON.parse(logStr) } catch(e){}
      }
      
      // Handle Python dict string format
      // Replace None/True/False with JS equivalents
      const sanitized = logStr
          .replace(/: None/g, ': null')
          .replace(/: True/g, ': true')
          .replace(/: False/g, ': false')
      
      // Use new Function to parse loosely
      // This handles single quotes used in Python dicts
      return new Function('return ' + sanitized)()
    } catch (e) {
      return null
    }
  }

  // Iterate through all logs to rebuild state
  // Optimization: only process new logs if we could track index, but here we process all for correctness
  // In a real app with many logs, we should optimize. For now, it's fine.
  logEntries.forEach(log => {
    if (typeof log !== 'string') return
    
    // Check if it's a progress-related log before parsing to save perf
    if (!log.includes('type') && !log.includes('stage')) return

    const data = parseLogEntry(log)
    if (!data) return

    if (data.type === 'stage_summary') {
      // Only set stages if not already set or if different
      if (foundStages.length === 0) {
        foundStages = data.stages.map(s => ({
            name: s.name,
            percent: s.percent,
            status: 'pending'
        }))
      }
    } else if (data.type === 'progress_start') {
      current = data.stage
      if (foundStages.length > 0) {
        const s = foundStages.find(st => st.name === data.stage)
        if (s) {
            s.status = 'active'
            // Mark previous stages as completed
            const idx = foundStages.findIndex(st => st.name === data.stage)
            if (idx > 0) {
                for(let i=0; i<idx; i++) {
                    if (foundStages[i].status !== 'completed') {
                        foundStages[i].status = 'completed'
                    }
                }
            }
        }
      }
      if (data.overall_progress !== undefined) overall = data.overall_progress
    } else if (data.type === 'progress_update') {
      if (data.overall_progress !== undefined) overall = data.overall_progress
    } else if (data.type === 'progress_end') {
      if (foundStages.length > 0) {
        const s = foundStages.find(st => st.name === data.stage)
        if (s) s.status = 'completed'
      }
      if (data.overall_progress !== undefined) overall = data.overall_progress
    }
  })

  // Update state
  if (foundStages.length > 0) {
    stages.value = foundStages
  }
  
  if (current) {
    currentStage.value = current
  }

  if (overall !== null) {
    overallProgress.value = overall
  }
}

// Watch logs to extract progress
watch(logs, (newLogs) => {
  processLogs(newLogs)
}, { deep: true })

const startBatchTranslation = async () => {
  if (batchQueue.value.length === 0) return
  
  isTranslating.value = true
  serviceStatus.value = 'busy'
  currentBatchIndex.value = 0
  
  await processNextTask()
}

const processNextTask = async () => {
  if (currentBatchIndex.value >= batchQueue.value.length) {
    // All tasks done
    isTranslating.value = false
    serviceStatus.value = 'ready'
    taskStatus.value = 'completed' // Global status
    return
  }
  
  const task = batchQueue.value[currentBatchIndex.value]
  task.status = 'processing'
  
  // Update global state to reflect current task
  selectedFile.value = task.file
  logs.value = []
  stages.value = []
  currentStage.value = null
  overallProgress.value = 0
  taskStatus.value = 'processing'
  
  // Start translation for this task
  await startTranslation(task)
}

const startTranslation = async (task = null) => {
  if (!task && translationParams.source === 'File' && !selectedFile.value) return
  if (!task && translationParams.source === 'Link' && !translationParams.url) return
  
  // If called directly (single file), set global state
  if (!task) {
    isTranslating.value = true
    serviceStatus.value = 'busy'
    logs.value = []
    stages.value = []
    currentStage.value = null
    overallProgress.value = null
    downloadUrl.value = null
    monoPdfUrl.value = null
    dualPdfUrl.value = null
    taskStatus.value = null
  }
  
  try {
    let fileId
    
    if (translationParams.source === 'File') {
      // 1. Upload File
      const fileToUpload = task ? task.file : selectedFile.value
      const uploadResponse = await api.uploadFile(fileToUpload)
      fileId = uploadResponse.data.file_id
    } else {
      fileId = translationParams.url
    }
    
    // 2. Start Translation
    const params = {
      ...translationParams,
      file_id: fileId,
      lang_from: translationParams.langFrom,
      lang_to: translationParams.langTo,
      service: translationParams.service,
    }
    
    Object.keys(params).forEach(key => {
      if (params[key] === undefined || params[key] === '') {
        delete params[key]
      }
    })
    
    const translateResponse = await api.translate(params)
    const newTaskId = translateResponse.data.task_id
    
    if (task) {
      task.taskId = newTaskId
    } else {
      taskId.value = newTaskId
    }
    
    // 3. Poll Status
    pollStatus(task)
    
  } catch (error) {
    console.error('Translation failed:', error)
    if (task) {
      task.status = 'failed'
      task.error = error.message
      // Move to next task even if this one failed
      currentBatchIndex.value++
      setTimeout(processNextTask, 1000)
    } else {
      isTranslating.value = false
      serviceStatus.value = 'error'
      taskStatus.value = 'failed'
      logs.value.push(`Error: ${error.message}`)
      isLogsExpanded.value = true
    }
  }
}

const pollStatus = async (task = null) => {
  const currentTaskId = task ? task.taskId : taskId.value
  if (!currentTaskId) return
  
  try {
    const response = await api.getStatus(currentTaskId)
    const status = response.data.status
    const newLogs = response.data.logs || []
    
    if (task) {
      task.status = status
      task.logs = newLogs
      // Update global logs for display if this is the current task
      if (batchQueue.value[currentBatchIndex.value] === task) {
        logs.value = newLogs
        taskStatus.value = status
      }
      
      // Calculate progress for task
      // We need to parse logs to get progress for the task object too
      // Reuse processLogs logic but for the task object?
      // For now, just rely on the global 'overallProgress' which is updated by the 'logs' watcher
      // and sync it back to the task
      if (overallProgress.value !== null) {
        task.progress = overallProgress.value
      }
      
      // Also sync stages
      if (stages.value.length > 0) {
        task.stages = stages.value
      }
    } else {
      taskStatus.value = status
      logs.value = newLogs
    }
    
    if (status === 'completed') {
      if (task) {
        task.progress = 100
        task.monoPdfUrl = response.data.mono_pdf_path ? `/api/download_task/${currentTaskId}/mono` : null
        task.dualPdfUrl = response.data.dual_pdf_path ? `/api/download_task/${currentTaskId}/dual` : null
        
        // Save to recent files
        saveToRecentFiles(
          currentTaskId,
          task.file.name,
          translationParams.langFrom,
          translationParams.langTo,
          !!response.data.mono_pdf_path,
          !!response.data.dual_pdf_path
        ).catch(err => console.error('Failed to save recent file:', err))
        
        // Move to next task
        currentBatchIndex.value++
        setTimeout(processNextTask, 500)
      } else {
        isTranslating.value = false
        serviceStatus.value = 'ready'
        overallProgress.value = 100
        if (response.data.mono_pdf_path) {
          monoPdfUrl.value = `/api/download_task/${currentTaskId}/mono`
        }
        if (response.data.dual_pdf_path) {
          dualPdfUrl.value = `/api/download_task/${currentTaskId}/dual`
        }
        if (!monoPdfUrl.value && !dualPdfUrl.value) {
          downloadUrl.value = `/api/download_task/${currentTaskId}`
        }

        const filename = selectedFile.value?.name || translationParams.url || 'Translated PDF'
        saveToRecentFiles(
          currentTaskId,
          filename,
          translationParams.langFrom,
          translationParams.langTo,
          !!response.data.mono_pdf_path,
          !!response.data.dual_pdf_path
        ).catch(err => console.error('Failed to save recent file:', err))

        if (monoPdfUrl.value) downloadMono()
        if (dualPdfUrl.value) setTimeout(downloadDual, 1000)
      }
    } else if (status === 'failed') {
      if (task) {
        task.error = response.data.error
        // Move to next task
        currentBatchIndex.value++
        setTimeout(processNextTask, 1000)
      } else {
        isTranslating.value = false
        serviceStatus.value = 'error'
        overallProgress.value = null
        logs.value.push(`Error: ${response.data.error}`)
        isLogsExpanded.value = true
      }
    } else {
      setTimeout(() => pollStatus(task), 1000)
    }
  } catch (error) {
    console.error('Status check failed:', error)
    if (task) {
      task.status = 'failed'
      task.error = error.message
      currentBatchIndex.value++
      setTimeout(processNextTask, 1000)
    } else {
      isTranslating.value = false
      serviceStatus.value = 'error'
    }
  }
}

const resetTranslation = () => {
  isTranslating.value = false
  taskId.value = null
  taskStatus.value = null
  logs.value = []
  stages.value = []
  currentStage.value = null
  overallProgress.value = null
  downloadUrl.value = null
  monoPdfUrl.value = null
  dualPdfUrl.value = null
  selectedFile.value = null
  
  // Reset batch state
  batchQueue.value = []
  currentBatchIndex.value = -1
}

const stopTranslation = async () => {
  if (!taskId.value) return
  
  try {
    await api.cancelTranslation(taskId.value)
    // Immediate feedback
    isTranslating.value = false
    logs.value.push(t('translation.stoppedByUser') || 'Stopped by user')
    // Delay slightly to let the user see it stopped? 
    // Or just reset immediately as requested "go back to the main file selector"
    resetTranslation()
  } catch (error) {
    console.error('Failed to stop translation:', error)
  }
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

const handleOpenServiceSettings = () => {
  showSettings.value = true
  openAccordionItem.value = 'service'
}

// Handle going home - reset to index view if not already there
const handleGoHome = () => {
  // Close settings if open
  if (showSettings.value) {
    showSettings.value = false
  }
  // Only reset if not already on index to avoid unnecessary refresh
  if (!isOnIndex.value) {
    resetTranslation()
  }
}

// Keyboard Shortcuts
onKeyStroke(['n', 'N', 'r', 'R'], (e) => {
  if ((e.metaKey || e.ctrlKey) && !e.shiftKey && !e.altKey) {
    e.preventDefault()
    if (isTranslating.value) {
      stopTranslation()
    } else {
      resetTranslation()
    }
  }
})

onKeyStroke([',', 'p', 'P'], (e) => {
  if ((e.metaKey || e.ctrlKey) && !e.shiftKey && !e.altKey) {
    e.preventDefault()
    showSettings.value = !showSettings.value
  }
})

onKeyStroke(['d', 'D'], (e) => {
  if ((e.metaKey || e.ctrlKey) && !e.shiftKey && !e.altKey) {
    e.preventDefault()
    colorMode.value = colorMode.value === 'dark' ? 'light' : 'dark'
  }
})

onKeyStroke('Escape', (e) => {
  // Don't toggle if an input is focused
  const target = e.target
  if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) return
  
  // Optional: Check if a dropdown is open (heuristic)
  if (document.querySelector('[role="menu"]')) return

  e.preventDefault()
  
  // Track ESC presses for dev mode activation
  escPressCount.value++
  
  if (escPressTimeout.value) {
    clearTimeout(escPressTimeout.value)
  }
  
  if (escPressCount.value >= DEV_MODE_ESC_PRESSES) {
    toggleDevMode()
    escPressCount.value = 0
    return
  }
  
  escPressTimeout.value = setTimeout(() => {
    escPressCount.value = 0
  }, ESC_PRESS_TIMEOUT_MS)
  
  showSettings.value = !showSettings.value
})

onKeyStroke(['l', 'L'], (e) => {
  if ((e.metaKey || e.ctrlKey) && !e.shiftKey && !e.altKey) {
    e.preventDefault()
    document.getElementById('language-menu-trigger')?.click()
  }
})

// Download shortcuts
onKeyStroke('1', (e) => {
  if ((e.metaKey || e.ctrlKey) && !e.shiftKey && !e.altKey) {
    e.preventDefault()
    if (isTranslationComplete.value && monoPdfUrl.value) {
      downloadMono()
    }
  }
})

onKeyStroke('2', (e) => {
  if ((e.metaKey || e.ctrlKey) && !e.shiftKey && !e.altKey) {
    e.preventDefault()
    if (isTranslationComplete.value && dualPdfUrl.value) {
      downloadDual()
    }
  }
})

// Recent Files Functions
const loadRecentFiles = () => {
  const stored = localStorage.getItem('recentTranslations')
  if (stored) {
    try {
      return JSON.parse(stored)
    } catch (e) {
      console.error('Failed to parse recent translations:', e)
    }
  }
  return []
}

// Validate recent files - check if they still exist on the server
// Files without server availability are kept but marked, so we can still show their cached preview
const validateRecentFiles = async (files) => {
  if (!files || files.length === 0) return []
  
  const validationPromises = files.map(async (file) => {
    try {
      await api.checkTaskExists(file.taskId)
      return { ...file, serverAvailable: true }
    } catch (error) {
      // Task no longer exists on server, but we keep the cached data
      console.log(`Recent file ${file.filename} (${file.taskId}) no longer on server`)
      return { ...file, serverAvailable: false }
    }
  })
  
  const results = await Promise.all(validationPromises)
  
  // Filter out files that have no thumbnail AND no server availability (completely unusable)
  const usableFiles = results.filter(f => f.serverAvailable || f.thumbnail)
  
  // Update localStorage with availability status
  localStorage.setItem('recentTranslations', JSON.stringify(usableFiles))
  
  return usableFiles
}

// Constants for localStorage management
const MAX_RECENT_FILES = 5
const THUMBNAIL_WIDTH = 160 // px - small enough to save space
const THUMBNAIL_QUALITY = 0.7 // JPEG quality (0-1)
const MAX_STORAGE_SIZE = 4 * 1024 * 1024 // 4MB safety limit for localStorage

// Capture PDF first page as base64 thumbnail
const capturePdfThumbnail = async (pdfUrl) => {
  try {
    // Dynamically import pdfjs-dist (used by vue-pdf-embed)
    const pdfjsLib = await import('pdfjs-dist')
    
    // Set worker source
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`
    
    // Fetch PDF and get first page
    const loadingTask = pdfjsLib.getDocument(pdfUrl)
    const pdf = await loadingTask.promise
    const page = await pdf.getPage(1)
    
    // Calculate scale to fit thumbnail width
    const viewport = page.getViewport({ scale: 1 })
    const scale = THUMBNAIL_WIDTH / viewport.width
    const scaledViewport = page.getViewport({ scale })
    
    // Create canvas and render
    const canvas = document.createElement('canvas')
    canvas.width = scaledViewport.width
    canvas.height = scaledViewport.height
    const context = canvas.getContext('2d')
    
    await page.render({
      canvasContext: context,
      viewport: scaledViewport
    }).promise
    
    // Convert to compressed JPEG base64
    const thumbnail = canvas.toDataURL('image/jpeg', THUMBNAIL_QUALITY)
    
    // Cleanup
    pdf.destroy()
    
    return thumbnail
  } catch (error) {
    console.error('Failed to capture PDF thumbnail:', error)
    return null
  }
}

// Check localStorage usage
const getStorageSize = () => {
  let total = 0
  for (const key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      total += localStorage[key].length * 2 // UTF-16 = 2 bytes per char
    }
  }
  return total
}

// Compress stored data if exceeding limit
const compressRecentFilesIfNeeded = (files) => {
  let data = JSON.stringify(files)
  
  // If data is too large, remove thumbnails from oldest files first
  while (data.length * 2 > MAX_STORAGE_SIZE && files.length > 0) {
    // Find file with thumbnail and remove it (starting from oldest)
    for (let i = files.length - 1; i >= 0; i--) {
      if (files[i].thumbnail) {
        console.log(`Removing thumbnail from ${files[i].filename} to save space`)
        files[i].thumbnail = null
        data = JSON.stringify(files)
        break
      }
    }
    // If no thumbnails left and still too big, remove oldest file
    if (data.length * 2 > MAX_STORAGE_SIZE) {
      files.pop()
      data = JSON.stringify(files)
    }
  }
  
  return files
}

const saveToRecentFiles = async (taskIdValue, filename, langFrom, langTo, hasMonoPdf, hasDualPdf) => {
  const recent = loadRecentFiles()
  // Remove existing entry with same taskId if exists
  const filtered = recent.filter(f => f.taskId !== taskIdValue)
  
  // Capture thumbnail from the mono PDF
  let thumbnail = null
  if (hasMonoPdf) {
    thumbnail = await capturePdfThumbnail(`/api/download_task/${taskIdValue}/mono`)
  }
  
  // Add new entry at the beginning
  filtered.unshift({
    taskId: taskIdValue,
    filename,
    timestamp: Date.now(),
    langFrom,
    langTo,
    hasMonoPdf,
    hasDualPdf,
    thumbnail, // base64 preview image
    serverAvailable: true // Track if files are still on server
  })
  
  // Keep only the last MAX_RECENT_FILES
  let trimmed = filtered.slice(0, MAX_RECENT_FILES)
  
  // Compress if needed to stay within storage limits
  trimmed = compressRecentFilesIfNeeded(trimmed)
  
  try {
    localStorage.setItem('recentTranslations', JSON.stringify(trimmed))
    recentFiles.value = trimmed
  } catch (e) {
    console.error('Failed to save recent files to localStorage:', e)
    // If quota exceeded, try removing thumbnails
    trimmed.forEach(f => f.thumbnail = null)
    try {
      localStorage.setItem('recentTranslations', JSON.stringify(trimmed))
      recentFiles.value = trimmed
    } catch (e2) {
      console.error('Still failed after removing thumbnails:', e2)
    }
  }
}

const clearRecentFiles = () => {
  localStorage.removeItem('recentTranslations')
  recentFiles.value = []
}

// Download functions for recent files (by taskId)
const handleRecentDownload = async (downloadFn, recentTaskId) => {
  try {
    const response = await downloadFn(recentTaskId)
    const blob = new Blob([response.data], { type: response.headers['content-type'] })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    let filename = 'download.pdf'
    const disposition = response.headers['content-disposition']
    if (disposition) {
      const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/)
      if (utf8Match) {
        filename = decodeURIComponent(utf8Match[1])
      } else {
        const filenameMatch = disposition.match(/filename="?([^"]+)"?/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }
    }
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    
    setTimeout(() => {
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }, 100)
  } catch (error) {
    console.error('Download failed:', error)
    // If file not found (404), remove from recent files
    if (error.response && error.response.status === 404) {
      const recent = recentFiles.value.filter(f => f.taskId !== recentTaskId)
      localStorage.setItem('recentTranslations', JSON.stringify(recent))
      recentFiles.value = recent
    }
  }
}

const downloadRecentMono = async (recentTaskId) => {
  await handleRecentDownload(api.downloadTaskMono, recentTaskId)
}

const downloadRecentDual = async (recentTaskId) => {
  await handleRecentDownload(api.downloadTaskDual, recentTaskId)
}

// Load recent files on component initialization
// First load from localStorage for immediate display
recentFiles.value = loadRecentFiles()

// Then validate asynchronously and remove missing files
const initRecentFiles = async () => {
  const stored = loadRecentFiles()
  if (stored.length > 0) {
    const validFiles = await validateRecentFiles(stored)
    recentFiles.value = validFiles
  }
}
initRecentFiles()
</script>

<template>
  <div 
    class="min-h-screen bg-background font-sans antialiased overflow-x-hidden transition-opacity duration-200 flex flex-col"
    :class="{ 'opacity-0': isLanguageSwitching, 'opacity-100': !isLanguageSwitching }"
  >
    <Header 
      :show-settings="showSettings" 
      :is-wco="isWco" 
      :dev-mode="devMode"
      :is-translating="isTranslating"
      @toggle-settings="showSettings = !showSettings" 
      @change-language="handleLanguageChange"
      @toggle-dev-mode="toggleDevMode"
      @go-home="handleGoHome"
    />
    
    <main class="container py-10 mx-auto px-6 flex-1" :class="{ 'my-6': isWco }">
      <Transition name="fade" mode="out-in">
        <div
          v-if="!showSettings"
          key="main"
          class="max-w-4xl mx-auto space-y-8"
          :class="{ 'home-text-unselectable': isOnIndex }"
        >
          <div class="space-y-2">
            <!-- Batch Progress Card -->
            <BatchProgressCard 
              v-if="isBatchMode"
              :tasks="batchQueue"
              :current-index="currentBatchIndex"
              :completed-count="completedBatchCount"
              :total-count="batchQueue.length"
              :is-batch-complete="isBatchComplete"
              @reset="resetBatch"
              @retry="retryBatch"
            />

            <!-- Translation Options - Hidden when translation starts or is in progress -->
            <Card v-if="!isTranslating && overallProgress === null && !isTranslationComplete && taskStatus !== 'failed' && !isBatchMode" class="relative z-20">
              <CardHeader class="flex flex-row items-start justify-between pb-2 space-y-0">

                <div class="space-y-1.5 z-100">
                  <CardTitle>{{ t('translation.options') }}</CardTitle>
                  <CardDescription>{{ t('translation.optionsDescription') }}</CardDescription>
                </div>
                <div class="flex gap-1 bg-muted/30 p-1 rounded-lg transition-colors duration-300">
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    @click="translationParams.source = 'File'" 
                    class="transition-all duration-300 rounded-md hover:bg-background/50"
                    :class="translationParams.source === 'File' 
                      ? 'bg-background shadow-sm text-primary' 
                      : 'text-muted-foreground hover:text-primary'"
                    :title="t('translation.file')"
                  >
                    <FileText 
                      class="w-4 h-4 transition-colors duration-300" 
                    />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    @click="translationParams.source = 'Link'" 
                    class="transition-all duration-300 rounded-md hover:bg-background/50"
                    :class="translationParams.source === 'Link' 
                      ? 'bg-background shadow-sm text-primary' 
                      : 'text-muted-foreground hover:text-primary'"
                    :title="t('translation.link')"
                  >
                    <LinkIcon 
                      class="w-4 h-4 transition-colors duration-300" 
                    />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <TranslationOptions 
                  v-model="translationParams" 
                  :config="config" 
                  @file-selected="handleFileSelected" 
                  @files-selected="handleFileSelected"
                  @open-service-settings="handleOpenServiceSettings" 
                />
              </CardContent>
            </Card>

            <!-- Service Changer Card -->
            <ServiceChangerCard 
              v-if="!isTranslating && overallProgress === null && !isTranslationComplete && taskStatus !== 'failed' && !isBatchMode"
              v-model="translationParams" 
              :config="config"
            />
          </div>
          
          <!-- Progress Box - Show during translation or failure -->
          <Card v-if="isTranslating || (overallProgress !== null && !isTranslationComplete) || taskStatus === 'failed'">
            <CardHeader>
              <CardTitle class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <Loader2 v-if="isTranslating" class="h-5 w-5 animate-spin" />
                  {{ overallProgress === null || overallProgress === 0 
                    ? t('translation.starting') 
                    : `${t('translation.processing') || 'Processing'} (${overallProgress.toFixed(1)}%)` }}
                </div>
                <TooltipProvider v-if="isTranslating">
                  <Tooltip>
                    <TooltipTrigger as-child>
                      <Button 
                        variant="destructive" 
                        size="sm" 
                        class="h-8 text-white hover:bg-destructive/90"
                        @click="stopTranslation"
                      >
                        <Square class="w-4 h-4 mr-2" fill="currentColor" />
                        {{ t('translation.cancel') || 'Cancel' }}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{{ t('shortcuts.stop') }} (⌘/Ctrl + N / R)</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div v-if="taskStatus === 'failed'" class="flex flex-col sm:flex-row items-center gap-4 p-4 border border-destructive/50 rounded-lg bg-destructive/10 text-destructive transition-colors duration-300">
                 <div class="flex-1 font-medium flex items-center gap-2">
                   <AlertCircle class="h-5 w-5" />
                   {{ t('translation.failed') || 'Translation Failed' }}
                 </div>
                 <div class="flex gap-2 w-full sm:w-auto">
                    <Button variant="default" size="sm" @click="startTranslation" class="flex-1 sm:flex-none">
                      <RefreshCw class="w-4 h-4 mr-2" />
                      {{ t('translation.retry') || 'Retry' }}
                    </Button>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger as-child>
                          <Button variant="outline" size="sm" @click="resetTranslation" class="flex-1 sm:flex-none bg-background hover:bg-accent text-foreground border-input">
                            {{ t('translation.startNew') || 'Start New' }}
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>{{ t('shortcuts.new') }} (⌘/Ctrl + N / R)</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                 </div>
              </div>

              <!-- Progress bar - commented out for simplified UI -->
              <!-- <div v-if="taskStatus !== 'failed'" class="space-y-2">
                  <Progress :value="overallProgress !== null ? overallProgress : 0" class="w-full" />
              </div> -->
              
              <!-- Stages List -->
              <div v-if="stages.length > 0 && taskStatus !== 'failed'" class="mt-4 h-9 overflow-hidden relative">
                <div 
                  class="transition-transform duration-500 ease-in-out absolute h-full top-0 left-0 flex gap-2"
                  :style="{ transform: `translateX(-${activeStageIndex * 12.5}rem)` }"
                >
                  <div 
                    v-for="(stage, index) in stages" 
                    :key="index" 
                    class="flex items-center gap-2 text-sm px-3 rounded-md transition-colors w-48 flex-shrink-0 border"
                    :class="{
                      'bg-green-100 border-green-200 text-green-700 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400': stage.status === 'completed',
                      'bg-background border-primary text-foreground ring-1 ring-primary/20': stage.status === 'active',
                      'bg-muted/50 border-transparent text-muted-foreground': stage.status === 'pending'
                    }"
                  >
                     <div class="flex-shrink-0 w-4 h-4 flex items-center justify-center">
                       <Check v-if="stage.status === 'completed'" class="h-3.5 w-3.5" />
                       <Loader2 v-else-if="stage.status === 'active'" class="h-3.5 w-3.5 animate-spin text-primary" />
                       <div v-else class="h-1.5 w-1.5 rounded-full bg-muted-foreground/30"></div>
                     </div>
                     <span class="truncate font-medium">{{ stage.name }}</span>
                  </div>
                </div>
              </div>

              <!-- Original File Preview -->
              <div v-if="selectedFilePreviewUrl && taskStatus !== 'failed'" class="space-y-2">
                  <!-- <p class="text-sm text-muted-foreground">{{ t('translation.originalFilePreview') }}</p> -->
                  <div class="border rounded-lg overflow-hidden p-4 pdf-preview-container">
                      <VuePdfEmbed 
                          :source="selectedFilePreviewUrl"
                          class="w-full"
                      />
                  </div>
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
          <Card v-if="isTranslationComplete && !isBatchComplete">
            <CardHeader>
              <CardTitle>{{ t('translation.result') }}</CardTitle>
              <CardDescription>{{ t('translation.resultDescription') }}</CardDescription>
            </CardHeader>
            <CardContent class="space-y-6">
              <!-- Download Buttons -->
              <div class="flex flex-wrap gap-4">
                <TooltipProvider v-if="monoPdfUrl">
                  <Tooltip>
                    <TooltipTrigger as-child>
                      <Button 
                        variant="default" 
                        @click="downloadMono"
                        class="flex items-center gap-2"
                      >
                        <Download class="h-4 w-4" />
                        {{ t('translation.downloadMono') }}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{{ t('shortcuts.downloadMono') || 'Download Mono' }} (⌘/Ctrl + 1)</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <TooltipProvider v-if="dualPdfUrl">
                  <Tooltip>
                    <TooltipTrigger as-child>
                      <Button 
                        variant="outline" 
                        @click="downloadDual"
                        class="flex items-center gap-2"
                      >
                        <Download class="h-4 w-4" />
                        {{ t('translation.downloadDual') }}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{{ t('shortcuts.downloadDual') || 'Download Dual' }} (⌘/Ctrl + 2)</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
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
                
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger as-child>
                      <Button 
                        variant="secondary" 
                        @click="resetTranslation"
                        class="flex items-center gap-2"
                      >
                        <RefreshCw class="h-4 w-4" />
                        {{ t('translation.restart') || 'Start New Translation' }}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{{ t('shortcuts.new') }} (⌘/Ctrl + N / R)</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>

              <!-- PDF Preview - Show first page of mono PDF -->
              <div v-if="monoPdfUrl" class="space-y-4">
                <div class="border rounded-lg overflow-hidden p-4 pdf-preview-container">
                  <VuePdfEmbed 
                    :source="monoPdfUrl"
                    class="w-full"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Recent Files Section -->
          <Card v-if="recentFiles.length > 0">
            <CardHeader class="flex flex-row items-center justify-between pb-4 space-y-0">
              <div class="space-y-1.5">
                <CardTitle>{{ t('recentFiles.title') }}</CardTitle>
                <CardDescription>{{ t('recentFiles.description') }}</CardDescription>
              </div>
              <Button variant="ghost" size="sm" @click="clearRecentFiles" class="text-muted-foreground hover:text-destructive">
                <Trash2 class="h-4 w-4 mr-2" />
                {{ t('recentFiles.clear') }}
              </Button>
            </CardHeader>
            <CardContent>
              <div class="flex flex-wrap justify-start gap-4">
                <div 
                  v-for="file in recentFiles" 
                  :key="file.taskId" 
                  class="recent-file-card flex flex-col items-center w-40 p-3 border rounded-lg transition-colors"
                  :class="file.serverAvailable !== false ? 'bg-muted/30 hover:bg-muted/50' : 'bg-muted/10 opacity-75'"
                >
                  <!-- Preview thumbnail - use cached thumbnail or live PDF -->
                  <div class="recent-preview-container w-full h-28 mb-2 border rounded overflow-hidden bg-background relative">
                    <!-- Use cached thumbnail if available -->
                    <img 
                      v-if="file.thumbnail" 
                      :src="file.thumbnail" 
                      :alt="file.filename"
                      class="w-full h-full object-cover object-top"
                    />
                    <!-- Fallback to live PDF if server available and no thumbnail -->
                    <VuePdfEmbed 
                      v-else-if="file.serverAvailable !== false"
                      :source="`/api/download_task/${file.taskId}/mono`"
                      class="w-full h-full object-cover"
                    />
                    <!-- Placeholder when no thumbnail and server unavailable -->
                    <div 
                      v-else 
                      class="w-full h-full flex items-center justify-center text-muted-foreground"
                    >
                      <FileText class="h-8 w-8 opacity-30" />
                    </div>
                    <!-- Unavailable overlay badge -->
                    <div 
                      v-if="file.serverAvailable === false" 
                      class="absolute bottom-1 right-1 px-1.5 py-0.5 text-[10px] font-medium rounded bg-muted/80 text-muted-foreground backdrop-blur-sm transition-colors duration-300"
                    >
                      {{ t('recentFiles.cached') }}
                    </div>
                  </div>
                  <!-- File info -->
                  <p class="text-xs font-medium text-center truncate w-full mb-0.5" :title="file.filename">
                    {{ file.filename }}
                  </p>
                  <p class="text-xs text-muted-foreground mb-2">
                    {{ file.langFrom }} → {{ file.langTo }}
                  </p>
                  <!-- Download buttons - disabled when server unavailable -->
                  <div class="flex gap-1.5 w-full">
                    <Button 
                      v-if="file.hasMonoPdf" 
                      size="sm" 
                      variant="default"
                      class="flex-1 text-xs h-7 px-2"
                      :disabled="file.serverAvailable === false"
                      @click="downloadRecentMono(file.taskId)"
                    >
                      <Download class="h-3 w-3 mr-1" />
                      {{ t('recentFiles.mono') }}
                    </Button>
                    <Button 
                      v-if="file.hasDualPdf" 
                      size="sm" 
                      variant="outline"
                      class="flex-1 text-xs h-7 px-2"
                      :disabled="file.serverAvailable === false"
                      @click="downloadRecentDual(file.taskId)"
                    >
                      <Download class="h-3 w-3 mr-1" />
                      {{ t('recentFiles.dual') }}
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Dev Mode Stats Card -->
          <DevStatsCard 
            v-if="devMode" 
            :health="healthInfo" 
            :config="config"
            class="mt-8"
          />
        </div>

        <div v-else key="settings" class="max-w-3xl mx-auto space-y-6">
          <Card class="h-full">
            <CardHeader class="relative">
              <CardTitle class="flex items-center gap-2">
                {{ t('settings.title') }}
                <Transition name="fade">
                  <Check v-if="isSaved" class="h-4 w-4 text-green-500" />
                </Transition>
                <span v-if="devMode" class="ml-2 px-2 py-0.5 text-xs font-medium rounded-full bg-amber-500/20 text-amber-600 dark:text-amber-400 flex items-center gap-1">
                  <Zap class="h-3 w-3" />
                  {{ t('devMode.badge') }}
                </span>
              </CardTitle>
              <Button
                v-if="isPWA"
                variant="ghost"
                size="icon"
                class="absolute top-6 right-6"
                @click="handleGoHome"
              >
                <X class="h-4 w-4" />
                <span class="sr-only">{{ t('common.close') }}</span>
              </Button>
            </CardHeader>
            <CardContent>
              <ApplicationSettings v-model="translationParams" :config="config" :open-accordion="openAccordionItem" />
            </CardContent>
          </Card>

          <!-- Dev Mode Advanced Settings -->
          <DevSettings 
            v-if="devMode && config?.all_params" 
            v-model="translationParams" 
            :config="config"
          />
        </div>
      </Transition>
    </main>

    <ProjectInfo :status="serviceStatus" :health="healthInfo" />
  </div>
</template>

<style scoped>
/* Dark mode: darken the PDF content only */
:global(.dark) .pdf-preview-container :deep(.vue-pdf-embed) {
  filter: brightness(0.7);
}

/* Hide all PDF pages except the first one in the preview */
.pdf-preview-container :deep(.vue-pdf-embed > div:not(:first-child)) {
  display: none;
}

.pdf-preview-container :deep(.vue-pdf-embed canvas:not(:first-of-type)) {
  display: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Recent Files Preview Styles */
.recent-preview-container :deep(.vue-pdf-embed) {
  width: 100%;
  height: 100%;
}

.recent-preview-container :deep(.vue-pdf-embed > div:not(:first-child)) {
  display: none;
}

.recent-preview-container :deep(.vue-pdf-embed canvas:not(:first-of-type)) {
  display: none;
}

.recent-preview-container :deep(.vue-pdf-embed canvas) {
  width: 100% !important;
  height: auto !important;
  max-height: 100%;
  object-fit: contain;
}

:global(.dark) .recent-preview-container :deep(.vue-pdf-embed) {
  filter: brightness(0.7);
}

/* Elegant non-linear floating for recent file cards */
.recent-file-card {
  --float-delay: 0s;
  --entrance-delay: 0s;
  animation: 
    card-entrance 0.8s cubic-bezier(0.22, 1, 0.36, 1) var(--entrance-delay) both;
  animation-delay: var(--entrance-delay);
  transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1), 
              box-shadow 0.6s cubic-bezier(0.22, 1, 0.36, 1),
              background-color 0.3s ease;
  will-change: transform;
}

/* Staggered animation delays for each card */
.recent-file-card:nth-child(1) { --float-delay: 0s; --entrance-delay: 0s; }
.recent-file-card:nth-child(2) { --float-delay: 0.8s; --entrance-delay: 0.08s; }
.recent-file-card:nth-child(3) { --float-delay: 1.6s; --entrance-delay: 0.16s; }
.recent-file-card:nth-child(4) { --float-delay: 2.4s; --entrance-delay: 0.24s; }
.recent-file-card:nth-child(5) { --float-delay: 3.2s; --entrance-delay: 0.32s; }

/* Entrance animation - fade in with upward motion */
@keyframes card-entrance {
  0% {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.recent-file-card:hover {
  animation: card-hover 2.5s cubic-bezier(0.37, 0, 0.63, 1) infinite;
  transform: translateY(-2px);
  box-shadow: 0 16px 32px -8px rgba(0, 0, 0, 0.12), 
              0 6px 12px -4px rgba(0, 0, 0, 0.06),
              0 0 0 1px rgba(0, 0, 0, 0.02);
}

:global(.dark) .recent-file-card:hover {
  box-shadow: 0 16px 32px -8px rgba(0, 0, 0, 0.45), 
              0 6px 12px -4px rgba(0, 0, 0, 0.25),
              0 0 0 1px rgba(255, 255, 255, 0.03);
}

/* Subtle resting animation - organic breathing */
@keyframes card-idle {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  25% {
    transform: translateY(-2px) scale(1.003);
  }
  50% {
    transform: translateY(-4px) scale(1.006);
  }
  75% {
    transform: translateY(-2px) scale(1.003);
  }
}

/* Hover state - subtle floating */
@keyframes card-hover {
  0% {
    transform: translateY(-2px);
  }
  25% {
    transform: translateY(-3px);
  }
  50% {
    transform: translateY(-2px);
  }
  75% {
    transform: translateY(-3px);
  }
  100% {
    transform: translateY(-2px);
  }
}

/* Preview image subtle motion on hover */
.recent-file-card:hover .recent-preview-container img,
.recent-file-card:hover .recent-preview-container :deep(.vue-pdf-embed) {
  transition: transform 0.8s cubic-bezier(0.22, 1, 0.36, 1);
  transform: scale(1.05);
}

/* Reduce motion for users who prefer it */
@media (prefers-reduced-motion: reduce) {
  .recent-file-card {
    animation: none;
  }
  .recent-file-card:hover {
    animation: none;
    transform: translateY(-2px);
  }
}

.home-text-unselectable :deep(button),
.home-text-unselectable :deep(button *) {
  user-select: none;
  -webkit-user-select: none;
}

.home-text-unselectable :deep([data-card-title]),
.home-text-unselectable :deep([data-card-title] *),
.home-text-unselectable :deep([data-card-description]),
.home-text-unselectable :deep([data-card-description] *) {
  user-select: none;
  -webkit-user-select: none;
}
</style>
