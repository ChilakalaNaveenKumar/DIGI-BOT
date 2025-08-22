import { ref, computed, readonly, onMounted } from 'vue'

export const useTheme = () => {
  const theme = ref<'light' | 'dark' | 'auto'>('auto')
  
  // Initialize theme from localStorage or system preference
  const initializeTheme = () => {
    if (process.client) {
      const stored = localStorage.getItem('theme') as 'light' | 'dark' | 'auto'
      if (stored) {
        theme.value = stored
      } else {
        theme.value = 'auto'
      }
    }
  }
  
  // Set theme
  const setTheme = (newTheme: 'light' | 'dark' | 'auto') => {
    theme.value = newTheme
    if (process.client) {
      localStorage.setItem('theme', newTheme)
      updateDocumentTheme(newTheme)
    }
  }
  
  // Toggle between light and dark (skip auto for simple toggle)
  const toggleTheme = () => {
    // If currently auto, determine what it resolves to and toggle to opposite
    if (theme.value === 'auto') {
      const currentResolved = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      const newTheme = currentResolved === 'light' ? 'dark' : 'light'
      setTheme(newTheme)
    } else {
      // Simple toggle between light and dark
      const newTheme = theme.value === 'light' ? 'dark' : 'light'
      setTheme(newTheme)
    }
    console.log('Theme toggled:', theme.value) // Debug log
  }
  
  // Get current effective theme (resolves 'auto' to actual theme)
  const currentTheme = computed(() => {
    if (!process.client) return theme.value
    
    if (theme.value === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return theme.value
  })
  
  // Update document theme
  const updateDocumentTheme = (themeValue: 'light' | 'dark' | 'auto') => {
    if (!process.client) return
    
    let actualTheme = themeValue
    if (themeValue === 'auto') {
      actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    
    // Apply to both html and body elements to ensure it works
    document.documentElement.setAttribute('data-theme', actualTheme)
    document.body.setAttribute('data-theme', actualTheme)
    
    // Also apply as a class for additional CSS targeting options
    document.documentElement.className = document.documentElement.className.replace(/theme-\w+/g, '') + ` theme-${actualTheme}`
    
    console.log('Document theme updated to:', actualTheme) // Debug log
  }
  
  // Initialize on mount
  onMounted(() => {
    initializeTheme()
    updateDocumentTheme(theme.value)
    
    // Listen for system theme changes
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      mediaQuery.addEventListener('change', () => {
        if (theme.value === 'auto') {
          updateDocumentTheme('auto')
        }
      })
    }
  })
  
  return {
    theme: readonly(theme),
    currentTheme: readonly(currentTheme),
    setTheme,
    toggleTheme
  }
}