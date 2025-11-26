<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Check, X, Loader2, Clock, FileText } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  tasks: {
    type: Array,
    required: true,
    default: () => []
  },
  currentIndex: {
    type: Number,
    default: 0
  },
  completedCount: {
    type: Number,
    default: 0
  },
  totalCount: {
    type: Number,
    default: 0
  },
  isBatchComplete: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['reset', 'retry'])

const hasFailedTasks = computed(() => {
  return props.tasks.some(t => t.status === 'failed')
})

const getTaskColor = (task) => {
  if (task.status === 'completed') return 'bg-green-500 hover:bg-green-600 border-green-600/20'
  if (task.status === 'failed') return 'bg-destructive hover:bg-destructive/90 border-destructive/20'
  if (task.status === 'processing') return 'bg-primary hover:bg-primary/90 border-primary/20'
  return 'bg-muted hover:bg-muted/80 border-transparent'
}

const progressPercentage = computed(() => {
  if (props.totalCount === 0) return 0
  return Math.round((props.completedCount / props.totalCount) * 100)
})
</script>

<template>
  <Card class="w-full">
    <CardHeader class="pb-3">
      <div class="flex items-center justify-between">
        <CardTitle class="text-lg font-medium flex items-center gap-2">
          <FileText class="w-5 h-5" />
          {{ t('batch.tasksQueue') }}
        </CardTitle>
        <span class="text-sm text-muted-foreground">
          {{ completedCount }} / {{ totalCount }} ({{ progressPercentage }}%)
        </span>
      </div>
    </CardHeader>
    <CardContent>
      <div class="flex flex-wrap gap-2">
        <TooltipProvider v-for="(task, index) in tasks" :key="task.id">
          <Tooltip :delay-duration="0">
            <TooltipTrigger as-child>
              <div 
                class="w-9 h-9 rounded-md border shadow-sm transition-all duration-200 cursor-default"
                :class="getTaskColor(task)"
              >
              </div>
            </TooltipTrigger>
            <TooltipContent side="top" class="max-w-[300px]">
              <div class="space-y-1">
                <p class="font-medium text-sm truncate">{{ task.file.name }}</p>
                <div class="flex items-center justify-between text-xs text-muted-foreground">
                  <span class="capitalize">{{ t(`batch.${task.status}`) }}</span>
                  <span v-if="task.progress > 0">{{ task.progress.toFixed(0) }}%</span>
                </div>
                <p v-if="task.error" class="text-xs text-red-500 mt-1">{{ task.error }}</p>
              </div>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
      
      <!-- Batch Completion Controls -->
      <div v-if="isBatchComplete" class="mt-6 flex justify-end gap-2 pt-4 border-t">
        <Button 
          v-if="hasFailedTasks" 
          variant="default" 
          size="sm"
          @click="emit('retry')"
        >
          {{ t('batch.retryFailed') }}
        </Button>
        <Button 
          variant="outline" 
          size="sm"
          @click="emit('reset')"
        >
          {{ t('translation.startNew') }}
        </Button>
      </div>
    </CardContent>
  </Card>
</template>
