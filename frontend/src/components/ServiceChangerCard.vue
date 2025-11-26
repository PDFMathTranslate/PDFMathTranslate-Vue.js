<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ChevronDown, ChevronUp, Settings, Heart } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import ServiceComparisonCard from './ServiceComparisonCard.vue'
import { serviceFields } from '@/constants/services'

const { t } = useI18n()

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  config: {
    type: Object,
    default: () => ({ services: [] })
  }
})

const emit = defineEmits(['update:modelValue'])

const isExpanded = ref(false)

const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const services = computed(() => {
  return props.config?.services || []
})

const service = computed({
  get: () => model.value?.service,
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.service = val
  }
})

const currentServiceFields = computed(() => {
  return serviceFields[service.value] || []
})

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<template>
  <div class="w-full flex justify-center px-6 mb-0  py-0 ">
    <Card 
      class="overflow-hidden shadow-sm w-full cursor-pointer -mt-4"
      @click="toggleExpand"
    >
      <CardContent class="px-4  z-10 pt-6 pb-4">
        <!-- Collapsed Header -->
        <div 
          class="flex items-center justify-between py-0 transition-colors"
        >
          <div class="flex items-center gap-3 text-sm text-muted-foreground flex-1 justify-center  py-0 ">
            <template v-if="!isExpanded">
              <div class="flex items-center gap-1">
                <span>{{ t('fileSelector.currentService') }}</span>
                <span class="font-medium text-foreground">{{ service }}</span>
                <span >{{ t('fileSelector.toTranslate') }}</span>
              </div>
              
              <!-- <span class="text-muted-foreground/50">•</span> -->
              
              <!-- <div class="flex items-center gap-1">
                <Heart class="w-3 h-3 text-rose-500" />
                <span>{{ t('fileSelector.devSponsor') }}</span>
                <a href="https://go.warp.dev/PDFMathTranslate" target="_blank" rel="noopener noreferrer" class="text-primary hover:underline font-medium" @click.stop>Warp.dev</a>
              </div> -->
            </template>
            <template v-else>
              <span class="font-medium text-foreground">{{ t('settings.serviceSettings') }}</span>
            </template>
          </div>
          
          <Button variant="ghost" size="icon" class="h-6 w-6 rounded-full ml-2" @click.stop="toggleExpand">
            <ChevronDown v-if="!isExpanded" class="h-4 w-4" />
            <ChevronUp v-else class="h-4 w-4" />
          </Button>
        </div>

        <!-- Expanded Content -->
        <div 
          class="grid transition-[grid-template-rows] duration-500 ease-[cubic-bezier(0.4,0,0.2,1)]"
          :class="isExpanded ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'"
          @click.stop
        >
          <div class="overflow-hidden">
            <div class="p-6 space-y-6">
              <!-- Service Selector -->
              <div class="space-y-2">
                <Label>{{ t('translation.selectService') }}</Label>
                <Select v-model="service">
                  <SelectTrigger>
                    <SelectValue :placeholder="t('translation.selectService')">
                      <span v-if="service">{{ service }}</span>
                      <span v-else class="text-muted-foreground">{{ t('translation.selectService') }}</span>
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem 
                      v-for="srv in services" 
                      :key="`service-${srv}`" 
                      :value="srv"
                    >
                      {{ srv }}
                    </SelectItem>
                    <div v-if="services.length === 0" class="px-2 py-1.5 text-sm text-muted-foreground">
                      {{ t('translation.noServicesAvailable') }}
                    </div>
                  </SelectContent>
                </Select>
              </div>

              <!-- Dynamic Service Fields -->
              <div v-if="currentServiceFields.length > 0" class="space-y-4 pt-2 border-t">
                <div v-for="field in currentServiceFields" :key="field.name" class="space-y-2">
                  <Label :for="field.name">{{ t(field.label) }}</Label>
                  <Input 
                    :id="field.name" 
                    v-model="model[field.name]" 
                    :type="field.type" 
                    :placeholder="field.placeholder"
                  />
                </div>
              </div>

              <!-- Service Comparison -->
              <ServiceComparisonCard 
                :current-service="service" 
                :services="services"
                @update:current-service="service = $event"
              />
              
              <!-- Sponsor Footer in Expanded State -->
              <div class="pt-4 border-t text-center text-xs text-muted-foreground">
                <p>
                  {{ t('fileSelector.devSponsor') }} <a href="https://go.warp.dev/PDFMathTranslate" target="_blank" rel="noopener noreferrer" class="text-primary hover:underline font-medium">Warp.dev</a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<style scoped>
/* Smooth height transition */
.grid {
  transition-property: grid-template-rows;
}
</style>
