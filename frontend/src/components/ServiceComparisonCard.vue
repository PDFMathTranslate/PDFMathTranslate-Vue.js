<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import * as Diff from 'diff'
import { Button } from '@/components/ui/button'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Check, ArrowRight } from 'lucide-vue-next'
import translatorData from '../../misc/translator.json'

const props = defineProps({
  currentService: {
    type: String,
    required: true
  },
  services: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:currentService'])

const { t } = useI18n()

const keyMapping = {
  'glm-4-flash': ['Zhipu'],
  'microsoft': ['Bing', 'Azure'],
  'google': ['Google'],
  'siliconflow': ['SiliconFlow', 'SiliconFlowFree'],
  'deepl': ['DeepL']
}



const disciplines = ['cs', 'biology', 'econ', 'communication']

const selectedDiscipline = ref('cs')

const currentDisciplineData = computed(() => {
  return translatorData[selectedDiscipline.value] || {}
})

const rawText = computed(() => {
  return currentDisciplineData.value.raw || ''
})

const getServiceTranslation = (serviceName) => {
  // 1. Try direct match
  if (currentDisciplineData.value[serviceName]) return currentDisciplineData.value[serviceName]
  
  // 2. Try lowercase match
  const lower = serviceName.toLowerCase()
  if (currentDisciplineData.value[lower]) return currentDisciplineData.value[lower]

  // 3. Try mapping (Service Name -> JSON Key)
  const mappedKey = Object.keys(keyMapping).find(key => {
    const names = keyMapping[key]
    return names.some(n => n.toLowerCase() === serviceName.toLowerCase())
  })
  if (mappedKey && currentDisciplineData.value[mappedKey]) return currentDisciplineData.value[mappedKey]

  return ''
}

const currentServiceText = computed(() => {
  const text = getServiceTranslation(props.currentService)
  if (text) return text
  
  // Fallback to Google
  return getServiceTranslation('Google')
})

const usingFallback = computed(() => {
  return !getServiceTranslation(props.currentService) && !!getServiceTranslation('Google')
})

const computeDiff = (targetText) => {
  if (!currentServiceText.value || !targetText) return []
  return Diff.diffChars(currentServiceText.value, targetText)
}

const availableServicesForComparison = computed(() => {
  const keys = Object.keys(currentDisciplineData.value).filter(k => k !== 'raw')
  return keys.map(key => {
    // Get possible service names for this key
    const possibleNames = keyMapping[key] || [key]
    
    // Find which one is actually available in props.services
    // We do case-insensitive check against props.services
    let serviceName = possibleNames.find(name => 
      props.services.some(s => s.toLowerCase() === name.toLowerCase())
    )
    
    // If none found in props.services, just take the first possible name
    if (!serviceName) serviceName = possibleNames[0]

    return {
      id: key,
      name: serviceName,
      text: currentDisciplineData.value[key]
    }
  })
})

const selectService = (serviceName) => {
  emit('update:currentService', serviceName)
}
</script>

<template>
  <div class="w-full mt-6 pt-6 border-t">
    <div class="flex flex-col gap-4 mb-6">
      <div class="flex items-center justify-between">
        <div class="space-y-1">
          <h3 class="font-medium leading-none">{{ t('settings.serviceComparison') }}</h3>
          <p class="text-sm text-muted-foreground">
            {{ t('settings.serviceComparisonDescription') }}
          </p>
        </div>
        <Tabs v-model="selectedDiscipline" class="w-auto">
          <TabsList>
            <TabsTrigger v-for="id in disciplines" :key="id" :value="id">
              {{ t(`settings.disciplines.${id}`) }}
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
    </div>

    <div class="space-y-6">
      <!-- Fallback Warning -->
      <div v-if="usingFallback" class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3 text-sm text-amber-800 dark:text-amber-200 flex items-start gap-2 transition-colors duration-300">
        <div class="mt-0.5">⚠️</div>
        <div>
          {{ t('settings.serviceComparisonFallback', { service: currentService }) }}
        </div>
      </div>

      <!-- Source Text -->
      <div class="p-4 bg-muted/50 rounded-lg space-y-2 transition-colors duration-300">
        <h4 class="text-sm font-medium text-muted-foreground uppercase tracking-wider">{{ t('settings.sourceEnglish') }}</h4>
        <p class="text-sm leading-relaxed font-serif">{{ rawText }}</p>
      </div>

      <!-- Comparison Cards -->
      <div class="grid gap-4">
        <div 
          v-for="item in availableServicesForComparison" 
          :key="item.id"
          class="border rounded-lg overflow-hidden transition-all hover:shadow-md"
          :class="{ 'ring-2 ring-primary border-primary': item.name === currentService }"
        >
          <div class="bg-muted/30 px-4 py-3 flex items-center justify-between border-b transition-colors duration-300">
            <div class="flex items-center gap-2">
              <span class="font-semibold">{{ item.name }}</span>
              <Badge v-if="item.name === currentService" variant="default" class="text-xs">
                {{ t('settings.current') }}
              </Badge>
            </div>
            <Button 
              v-if="item.name !== currentService" 
              size="sm" 
              variant="secondary"
              class="h-7 text-xs gap-1"
              @click="selectService(item.name)"
            >
              {{ t('settings.useService') }}
              <ArrowRight class="w-3 h-3" />
            </Button>
          </div>
          
          <div class="p-4 text-sm leading-relaxed text-justify">
            <template v-if="item.name === currentService">
              {{ item.text }}
            </template>
            <template v-else>
              <!-- Diff View -->
              <span v-for="(part, index) in computeDiff(item.text)" :key="index"
                :class="{
                  'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 transition-colors duration-300': part.added,
                  'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 line-through decoration-red-500/50 transition-colors duration-300': part.removed
                }"
              >{{ part.value }}</span>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
