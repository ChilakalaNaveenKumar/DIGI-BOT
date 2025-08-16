import { ref, computed, watch } from 'vue'

// Global theme state
const theme = ref('light')
const systemPreference = ref('light')

// Detect system theme preference
const detectSystemTheme = () => {
  if (typeof window !== 'undefined') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  return 'light'
}

// Initialize system preference
if (typeof window !== 'undefined') {
  systemPreference.value = detectSystemTheme()
  
  // Listen for system theme changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e) => {
    systemPreference.value = e.matches ? 'dark' : 'light'
    if (theme.value === 'system') {
      applyTheme(systemPreference.value)
    }
  })
}

// Apply theme to document
const applyTheme = (themeValue) => {
  if (typeof document !== 'undefined') {
    const root = document.documentElement
    
    // Remove existing theme classes
    root.classList.remove('light', 'dark')
    
    // Apply new theme
    if (themeValue === 'system') {
      root.classList.add(systemPreference.value)
    } else {
      root.classList.add(themeValue)
    }
    
    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]')
    if (metaThemeColor) {
      const isDark = themeValue === 'dark' || (themeValue === 'system' && systemPreference.value === 'dark')
      metaThemeColor.setAttribute('content', isDark ? '#0f172a' : '#ffffff')
    }
  }
}

// Load saved theme from localStorage
const loadSavedTheme = () => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('digi-setu-theme')
    if (saved && ['light', 'dark', 'system'].includes(saved)) {
      theme.value = saved
    } else {
      // Default to system preference
      theme.value = 'system'
    }
    applyTheme(theme.value)
  }
}

// Save theme to localStorage
const saveTheme = (themeValue) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('digi-setu-theme', themeValue)
  }
}

export const useDigiSetuTheme = () => {
  // Computed properties
  const isDark = computed(() => {
    if (theme.value === 'system') {
      return systemPreference.value === 'dark'
    }
    return theme.value === 'dark'
  })
  
  const isLight = computed(() => !isDark.value)
  
  const currentTheme = computed(() => {
    if (theme.value === 'system') {
      return systemPreference.value
    }
    return theme.value
  })
  
  // Methods
  const setTheme = (newTheme) => {
    if (['light', 'dark', 'system'].includes(newTheme)) {
      theme.value = newTheme
      applyTheme(newTheme)
      saveTheme(newTheme)
    }
  }
  
  const toggleTheme = () => {
    const themes = ['light', 'dark', 'system']
    const currentIndex = themes.indexOf(theme.value)
    const nextIndex = (currentIndex + 1) % themes.length
    setTheme(themes[nextIndex])
  }
  
  const toggleLightDark = () => {
    if (theme.value === 'light') {
      setTheme('dark')
    } else if (theme.value === 'dark') {
      setTheme('light')
    } else {
      // If system, toggle to opposite of current system preference
      setTheme(systemPreference.value === 'dark' ? 'light' : 'dark')
    }
  }
  
  // Initialize theme on first use
  if (typeof window !== 'undefined' && !theme.value) {
    loadSavedTheme()
  }
  
  // Watch for theme changes and apply them
  watch(theme, (newTheme) => {
    applyTheme(newTheme)
    saveTheme(newTheme)
  }, { immediate: true })
  
  return {
    // State
    theme: readonly(theme),
    systemPreference: readonly(systemPreference),
    
    // Computed
    isDark,
    isLight,
    currentTheme,
    
    // Methods
    setTheme,
    toggleTheme,
    toggleLightDark,
    
    // Utilities
    applyTheme,
    loadSavedTheme
  }
}

// Theme configuration
export const digiSetuThemeConfig = {
  themes: [
    {
      id: 'light',
      name: 'Light',
      description: 'Clean and bright interface'
    },
    {
      id: 'dark', 
      name: 'Dark',
      description: 'Easy on the eyes in low light'
    },
    {
      id: 'system',
      name: 'System',
      description: 'Follows your system preference'
    }
  ],
  
  // CSS custom properties for each theme
  cssVariables: {
    light: {
      '--ds-bg-primary': '#ffffff',
      '--ds-bg-secondary': '#f8fafc',
      '--ds-text-primary': '#0f172a',
      '--ds-text-secondary': '#475569',
      '--ds-surface-primary': '#ffffff',
      '--ds-border-primary': '#e2e8f0'
    },
    dark: {
      '--ds-bg-primary': '#0f172a',
      '--ds-bg-secondary': '#1e293b', 
      '--ds-text-primary': '#f8fafc',
      '--ds-text-secondary': '#cbd5e1',
      '--ds-surface-primary': '#1e293b',
      '--ds-border-primary': '#334155'
    }
  }
}

// Helper function to get theme-aware colors
export const getThemeColor = (colorName, fallback = '#000000') => {
  if (typeof window === 'undefined') return fallback
  
  const root = document.documentElement
  const computedStyle = getComputedStyle(root)
  const cssVar = `--ds-${colorName}`
  
  return computedStyle.getPropertyValue(cssVar).trim() || fallback
}

// Helper function to create theme-aware CSS
export const createThemeCSS = (lightValue, darkValue) => {
  return {
    light: lightValue,
    dark: darkValue
  }
}

// Export composable as default
export { useDigiSetuTheme as default }
