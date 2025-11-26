<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Download } from 'lucide-vue-next'

const { t } = useI18n()

const deferredPrompt = ref(null)
const showInstallButton = ref(false)

onMounted(() => {
  // Listen for the beforeinstallprompt event
  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  
  // Check if already installed
  if (window.matchMedia('(display-mode: standalone)').matches) {
    showInstallButton.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
})

const handleBeforeInstallPrompt = (e) => {
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault()
  // Stash the event so it can be triggered later
  deferredPrompt.value = e
  // Update UI to show the install button
  showInstallButton.value = true
}

const installApp = async () => {
  if (!deferredPrompt.value) {
    return
  }

  // Show the install prompt
  deferredPrompt.value.prompt()

  // Wait for the user to respond to the prompt
  const { outcome } = await deferredPrompt.value.userChoice

  if (outcome === 'accepted') {
    console.log('User accepted the install prompt')
  } else {
    console.log('User dismissed the install prompt')
  }

  // Clear the deferredPrompt
  deferredPrompt.value = null
  showInstallButton.value = false
}
</script>

<template>
  <Button
    v-if="showInstallButton"
    size="sm"
    @click="installApp"
    class="gap-2 bg-accent text-accent-foreground hover:bg-accent/90 focus-visible:ring-accent"
  >
    <Download class="h-4 w-4" />
    {{ t('pwa.install') }}
  </Button>
</template>

