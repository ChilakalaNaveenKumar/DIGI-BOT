// Like Claude's smooth theme switching
export const useTheme = () => {
  const theme = ref<'light' | 'dark'>('dark') // Default to dark like Claude
  
  // Initialize theme from localStorage or system preference
  onMounted(() => {
    const saved = localStorage.getItem('digi-setu-theme')
    const system = window.matchMedia('(prefers-color-scheme: dark)').matches
    
    theme.value = saved as 'light' | 'dark' || (system ? 'dark' : 'light')
    applyTheme(theme.value)
    
    // Watch for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', (e) => {
        if (!saved) {
          theme.value = e.matches ? 'dark' : 'light'
          applyTheme(theme.value)
        }
      })
  })
  
  const applyTheme = (newTheme: 'light' | 'dark') => {
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('digi-setu-theme', newTheme)
  }
  
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    applyTheme(theme.value)
  }
  
  return {
    theme: readonly(theme),
    toggleTheme,
    isDark: computed(() => theme.value === 'dark'),
    isLight: computed(() => theme.value === 'light')
  }
}
