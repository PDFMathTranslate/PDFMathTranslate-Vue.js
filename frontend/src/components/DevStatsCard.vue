<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { 
  Cpu, 
  HardDrive, 
  Activity, 
  Clock, 
  Layers, 
  Server,
  Zap,
  Database,
  MemoryStick,
  Gauge
} from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  health: {
    type: Object,
    default: () => ({})
  },
  config: {
    type: Object,
    default: () => ({})
  }
})

// Performance metrics
const performanceMetrics = ref({
  fps: 0,
  domNodes: 0,
  jsHeapSize: 0,
  jsHeapLimit: 0,
  renderTime: 0
})

let rafId = null
let lastTime = performance.now()
let frameCount = 0

const updatePerformanceMetrics = () => {
  const now = performance.now()
  frameCount++
  
  if (now - lastTime >= 1000) {
    performanceMetrics.value.fps = Math.round(frameCount * 1000 / (now - lastTime))
    frameCount = 0
    lastTime = now
    
    // DOM node count
    performanceMetrics.value.domNodes = document.querySelectorAll('*').length
    
    // JS heap size (if available)
    if (performance.memory) {
      performanceMetrics.value.jsHeapSize = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024)
      performanceMetrics.value.jsHeapLimit = Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
    }
  }
  
  rafId = requestAnimationFrame(updatePerformanceMetrics)
}

onMounted(() => {
  rafId = requestAnimationFrame(updatePerformanceMetrics)
})

onUnmounted(() => {
  if (rafId) {
    cancelAnimationFrame(rafId)
  }
})

const cpuPercent = computed(() => props.health?.cpu_percent ?? 0)
const memoryPercent = computed(() => props.health?.memory_percent ?? 0)
const memoryUsed = computed(() => props.health?.memory_used_gb ?? 0)
const memoryTotal = computed(() => props.health?.memory_total_gb ?? 0)
const activeTasks = computed(() => props.health?.active_tasks ?? 0)
const pendingTasks = computed(() => props.health?.pending_tasks ?? 0)
const totalTasks = computed(() => props.health?.total_tasks ?? 0)
const serverStatus = computed(() => props.health?.status ?? 'unknown')

const cpuBarColor = computed(() => {
  if (cpuPercent.value > 80) return 'bg-red-500'
  if (cpuPercent.value > 50) return 'bg-yellow-500'
  return 'bg-green-500'
})

const memoryBarColor = computed(() => {
  if (memoryPercent.value > 80) return 'bg-red-500'
  if (memoryPercent.value > 50) return 'bg-yellow-500'
  return 'bg-green-500'
})

const servicesCount = computed(() => props.config?.services?.length ?? 0)
const languagesCount = computed(() => Object.keys(props.config?.languages ?? {}).length)
const paramsCount = computed(() => Object.keys(props.config?.all_params ?? {}).length)
</script>

<template>
  <Card class="dev-stats-card border-dashed border-amber-500/50 bg-amber-500/5">
    <CardHeader class="pb-3">
      <CardTitle class="flex items-center gap-2 text-amber-600 dark:text-amber-400">
        <Zap class="h-5 w-5" />
        {{ t('devMode.statsTitle') }}
      </CardTitle>
      <CardDescription class="text-amber-600/70 dark:text-amber-400/70">
        {{ t('devMode.statsDescription') }}
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <!-- Server Metrics Grid -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <!-- CPU Usage -->
        <div class="space-y-2 p-3 rounded-lg bg-background/50 border">
          <div class="flex items-center gap-2 text-sm font-medium">
            <Cpu class="h-4 w-4 text-muted-foreground" />
            CPU
          </div>
          <div class="text-2xl font-bold">{{ cpuPercent.toFixed(1) }}%</div>
          <div class="h-1.5 rounded-full bg-muted overflow-hidden">
            <div 
              class="h-full transition-all duration-300" 
              :class="cpuBarColor"
              :style="{ width: `${cpuPercent}%` }"
            />
          </div>
        </div>

        <!-- Memory Usage -->
        <div class="space-y-2 p-3 rounded-lg bg-background/50 border">
          <div class="flex items-center gap-2 text-sm font-medium">
            <MemoryStick class="h-4 w-4 text-muted-foreground" />
            Memory
          </div>
          <div class="text-2xl font-bold">{{ memoryPercent.toFixed(1) }}%</div>
          <div class="text-xs text-muted-foreground">
            {{ memoryUsed.toFixed(1) }}GB / {{ memoryTotal.toFixed(1) }}GB
          </div>
          <div class="h-1.5 rounded-full bg-muted overflow-hidden">
            <div 
              class="h-full transition-all duration-300" 
              :class="memoryBarColor"
              :style="{ width: `${memoryPercent}%` }"
            />
          </div>
        </div>

        <!-- Task Status -->
        <div class="space-y-2 p-3 rounded-lg bg-background/50 border">
          <div class="flex items-center gap-2 text-sm font-medium">
            <Activity class="h-4 w-4 text-muted-foreground" />
            Tasks
          </div>
          <div class="text-2xl font-bold">{{ activeTasks }}</div>
          <div class="text-xs text-muted-foreground">
            {{ pendingTasks }} pending / {{ totalTasks }} total
          </div>
        </div>

        <!-- Server Status -->
        <div class="space-y-2 p-3 rounded-lg bg-background/50 border">
          <div class="flex items-center gap-2 text-sm font-medium">
            <Server class="h-4 w-4 text-muted-foreground" />
            Status
          </div>
          <div class="text-2xl font-bold capitalize" :class="{
            'text-green-500': serverStatus === 'ready',
            'text-yellow-500': serverStatus === 'busy',
            'text-red-500': serverStatus === 'error'
          }">
            {{ serverStatus }}
          </div>
        </div>
      </div>

      <!-- Frontend Metrics -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2 border-t">
        <!-- FPS -->
        <div class="space-y-1 p-3 rounded-lg bg-background/50 border">
          <div class="flex items-center gap-2 text-sm font-medium">
            <Gauge class="h-4 w-4 text-muted-foreground" />
            FPS
          </div>
          <div class="text-xl font-bold" :class="{
            'text-green-500': performanceMetrics.fps >= 55,
            'text-yellow-500': performanceMetrics.fps >= 30 && performanceMetrics.fps < 55,
            'text-red-500': performanceMetrics.fps < 30
          }">
            {{ performanceMetrics.fps }}
          </div>
        </div>

        <!-- DOM Nodes -->
        <div class="space-y-1 p-3 rounded-lg bg-background/50 border">
          <div class="flex items-center gap-2 text-sm font-medium">
            <Layers class="h-4 w-4 text-muted-foreground" />
            DOM Nodes
          </div>
          <div class="text-xl font-bold">{{ performanceMetrics.domNodes }}</div>
        </div>

        <!-- JS Heap -->
        <div class="space-y-1 p-3 rounded-lg bg-background/50 border">
          <div class="flex items-center gap-2 text-sm font-medium">
            <Database class="h-4 w-4 text-muted-foreground" />
            JS Heap
          </div>
          <div class="text-xl font-bold">{{ performanceMetrics.jsHeapSize }}MB</div>
          <div class="text-xs text-muted-foreground">/ {{ performanceMetrics.jsHeapLimit }}MB</div>
        </div>

        <!-- Config Stats -->
        <div class="space-y-1 p-3 rounded-lg bg-background/50 border">
          <div class="flex items-center gap-2 text-sm font-medium">
            <HardDrive class="h-4 w-4 text-muted-foreground" />
            Config
          </div>
          <div class="text-sm">
            <span class="font-bold">{{ servicesCount }}</span> services
          </div>
          <div class="text-sm">
            <span class="font-bold">{{ languagesCount }}</span> languages
          </div>
          <div class="text-sm">
            <span class="font-bold">{{ paramsCount }}</span> params
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

<style scoped>
.dev-stats-card {
  animation: pulse-border 2s ease-in-out infinite;
}

@keyframes pulse-border {
  0%, 100% {
    border-color: rgba(245, 158, 11, 0.3);
  }
  50% {
    border-color: rgba(245, 158, 11, 0.6);
  }
}
</style>

