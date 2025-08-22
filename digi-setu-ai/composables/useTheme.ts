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
  
  // Update document theme
  const updateDocumentTheme = (themeValue: 'light' | 'dark' | 'auto') => {
    if (!process.client) return
    
    let actualTheme = themeValue
    if (themeValue === 'auto') {
      actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    
    document.documentElement.setAttribute('data-theme', actualTheme)
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
    setTheme
  }
}