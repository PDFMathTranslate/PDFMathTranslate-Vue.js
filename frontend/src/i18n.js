import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import zh from './locales/zh.json'
import zhTW from './locales/zh-TW.json'
import ja from './locales/ja.json'
import ko from './locales/ko.json'
import fr from './locales/fr.json'
import de from './locales/de.json'
import es from './locales/es.json'
import ru from './locales/ru.json'
import it from './locales/it.json'
import pt from './locales/pt.json'

// Get saved language from localStorage or default to browser language
const getDefaultLocale = () => {
  const saved = localStorage.getItem('locale')
  if (saved) return saved
  
  const browserLang = navigator.language.split('-')[0]
  const supportedLocales = ['en', 'zh', 'zh-TW', 'ja', 'ko', 'fr', 'de', 'es', 'ru', 'it', 'pt']
  
  // Check if browser language is supported
  if (supportedLocales.includes(browserLang)) {
    return browserLang
  }
  
  // Check for zh variants
  const fullLang = navigator.language.toLowerCase()
  if (fullLang === 'zh-tw' || fullLang === 'zh-hk' || fullLang === 'zh-mo') {
    return 'zh-TW'
  }
  if (fullLang === 'zh-cn' || fullLang === 'zh') {
    return 'zh'
  }
  
  return 'en' // default
}

const i18n = createI18n({
  locale: getDefaultLocale(),
  fallbackLocale: 'en',
  messages: {
    en,
    zh,
    'zh-TW': zhTW,
    ja,
    ko,
    fr,
    de,
    es,
    ru,
    it,
    pt
  },
  legacy: false
})

export default i18n

