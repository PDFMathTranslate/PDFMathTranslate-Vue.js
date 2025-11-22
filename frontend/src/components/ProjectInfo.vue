<script setup>
import { Github } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
</script>

<template>
  <footer class="py-6 border-t mt-6 ml-6 mr-6">
    <div class="container flex flex-col items-center justify-between gap-4 md:h-6 md:flex-row">
      <span class="text-xs text-muted-foreground">{{ t('app.subtitle') }}</span>
       <p class="text-sm leading-loose text-center text-muted-foreground/50 md:text-left">
        Built by <a href="#" class="font-medium underline underline-offset-4">Rongxin, Hellofinch, and Awwaawwa </a>.
      </p>
      <div class="flex items-right gap-4">
        <Button variant="ghost" size="sm" as-child>
          <a href="https://github.com/PDFMathTranslate/PDFMathTranslate" target="_blank" rel="noreferrer">
            <Github class="w-4 h-4 mr-2" />
            GitHub
          </a>
        </Button>
      </div>
    </div>
  </footer>
</template>
