import { ref, computed, watch, readonly } from 'vue'

/**
 * Component Customization System
 * 
 * Provides unified customization controls for all progressive components
 * including themes, animations, export options, and user preferences.
 */
export const useComponentCustomization = () => {
  
  // Global customization state
  const globalSettings = ref({
    // Animation settings
    animationsEnabled: true,
    animationSpeed: 'normal', // 'slow', 'normal', 'fast'
    animationStyle: 'smooth', // 'smooth', 'bouncy', 'minimal'
    
    // Theme settings
    colorTheme: 'professional', // 'professional', 'vibrant', 'minimal', 'dark'
    fontFamily: 'system', // 'system', 'mono', 'serif'
    fontSize: 'medium', // 'small', 'medium', 'large'
    
    // Layout settings
    compactMode: false,
    showControls: true,
    showStats: true,
    showDebugInfo: false,
    
    // Progressive rendering settings
    chunkSize: 3,
    renderDelay: 100,
    enableProgressBars: true,
    showTypingCursor: true,
    
    // Export settings
    exportFormat: 'svg', // 'svg', 'png', 'pdf', 'html'
    exportQuality: 'high', // 'low', 'medium', 'high'
    includeMetadata: true,
    
    // Accessibility settings
    highContrast: false,
    reducedMotion: false,
    screenReaderMode: false,
    keyboardNavigation: true
  })
  
  // Component-specific overrides
  const componentOverrides = ref({})
  
  // Theme definitions
  const themes = {
    professional: {
      name: 'Professional',
      colors: {
        primary: '#2563eb',
        secondary: '#7c3aed',
        accent: '#059669',
        background: '#ffffff',
        surface: '#f8fafc',
        text: '#1e293b',
        border: '#e2e8f0'
      },
      shadows: true,
      rounded: 'medium'
    },
    vibrant: {
      name: 'Vibrant',
      colors: {
        primary: '#ec4899',
        secondary: '#8b5cf6',
        accent: '#f59e0b',
        background: '#fefefe',
        surface: '#fef7ff',
        text: '#374151',
        border: '#d1d5db'
      },
      shadows: true,
      rounded: 'large'
    },
    minimal: {
      name: 'Minimal',
      colors: {
        primary: '#374151',
        secondary: '#6b7280',
        accent: '#9ca3af',
        background: '#ffffff',
        surface: '#f9fafb',
        text: '#111827',
        border: '#e5e7eb'
      },
      shadows: false,
      rounded: 'small'
    },
    dark: {
      name: 'Dark',
      colors: {
        primary: '#3b82f6',
        secondary: '#8b5cf6',
        accent: '#10b981',
        background: '#0f172a',
        surface: '#1e293b',
        text: '#f1f5f9',
        border: '#334155'
      },
      shadows: true,
      rounded: 'medium'
    }
  }
  
  // Animation speed mappings
  const animationSpeeds = {
    slow: { delay: 200, duration: 600 },
    normal: { delay: 100, duration: 300 },
    fast: { delay: 50, duration: 150 }
  }
  
  // Font family mappings
  const fontFamilies = {
    system: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    mono: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace',
    serif: '"Georgia", "Times New Roman", serif'
  }
  
  // Computed properties
  const currentTheme = computed(() => {
    return themes[globalSettings.value.colorTheme] || themes.professional
  })
  
  const currentAnimationSpeed = computed(() => {
    return animationSpeeds[globalSettings.value.animationSpeed] || animationSpeeds.normal
  })
  
  const currentFontFamily = computed(() => {
    return fontFamilies[globalSettings.value.fontFamily] || fontFamilies.system
  })
  
  const cssVariables = computed(() => {
    const theme = currentTheme.value
    const settings = globalSettings.value
    
    return {
      // Theme colors
      '--ds-primary': theme.colors.primary,
      '--ds-secondary': theme.colors.secondary,
      '--ds-accent': theme.colors.accent,
      '--ds-background': theme.colors.background,
      '--ds-surface': theme.colors.surface,
      '--ds-text': theme.colors.text,
      '--ds-border': theme.colors.border,
      
      // Typography
      '--ds-font-family': currentFontFamily.value,
      '--ds-font-size-base': settings.fontSize === 'small' ? '14px' : 
                             settings.fontSize === 'large' ? '18px' : '16px',
      
      // Animation
      '--ds-animation-duration': `${currentAnimationSpeed.value.duration}ms`,
      '--ds-animation-delay': `${currentAnimationSpeed.value.delay}ms`,
      
      // Layout
      '--ds-border-radius': theme.rounded === 'small' ? '4px' : 
                           theme.rounded === 'large' ? '12px' : '8px',
      '--ds-shadow': theme.shadows ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
      
      // Progressive rendering
      '--ds-chunk-size': settings.chunkSize,
      '--ds-render-delay': `${settings.renderDelay}ms`,
      
      // Accessibility
      '--ds-high-contrast': settings.highContrast ? '1' : '0',
      '--ds-reduced-motion': settings.reducedMotion ? '1' : '0'
    }
  })
  
  // Component customization methods
  const getComponentSettings = (componentId) => {
    const override = componentOverrides.value[componentId] || {}
    return {
      ...globalSettings.value,
      ...override
    }
  }
  
  const setComponentOverride = (componentId, settings) => {
    componentOverrides.value[componentId] = {
      ...componentOverrides.value[componentId],
      ...settings
    }
  }
  
  const removeComponentOverride = (componentId) => {
    delete componentOverrides.value[componentId]
  }
  
  const updateGlobalSettings = (newSettings) => {
    globalSettings.value = {
      ...globalSettings.value,
      ...newSettings
    }
  }
  
  // Preset configurations
  const presets = {
    'performance-optimized': {
      animationsEnabled: false,
      chunkSize: 10,
      renderDelay: 0,
      showControls: false,
      showStats: false,
      compactMode: true
    },
    'accessibility-focused': {
      highContrast: true,
      reducedMotion: true,
      screenReaderMode: true,
      fontSize: 'large',
      animationsEnabled: false,
      showControls: true
    },
    'presentation-mode': {
      colorTheme: 'vibrant',
      animationSpeed: 'slow',
      animationStyle: 'bouncy',
      fontSize: 'large',
      showControls: false,
      showStats: false
    },
    'developer-mode': {
      showDebugInfo: true,
      showControls: true,
      showStats: true,
      colorTheme: 'minimal',
      fontFamily: 'mono'
    }
  }
  
  const applyPreset = (presetName) => {
    const preset = presets[presetName]
    if (preset) {
      updateGlobalSettings(preset)
    }
  }
  
  // Export/Import settings
  const exportSettings = () => {
    return {
      globalSettings: globalSettings.value,
      componentOverrides: componentOverrides.value,
      timestamp: new Date().toISOString(),
      version: '1.0'
    }
  }
  
  const importSettings = (settingsData) => {
    try {
      if (settingsData.globalSettings) {
        globalSettings.value = {
          ...globalSettings.value,
          ...settingsData.globalSettings
        }
      }
      
      if (settingsData.componentOverrides) {
        componentOverrides.value = {
          ...componentOverrides.value,
          ...settingsData.componentOverrides
        }
      }
      
      return true
    } catch (error) {
      console.error('Failed to import settings:', error)
      return false
    }
  }
  
  const resetToDefaults = () => {
    globalSettings.value = {
      animationsEnabled: true,
      animationSpeed: 'normal',
      animationStyle: 'smooth',
      colorTheme: 'professional',
      fontFamily: 'system',
      fontSize: 'medium',
      compactMode: false,
      showControls: true,
      showStats: true,
      showDebugInfo: false,
      chunkSize: 3,
      renderDelay: 100,
      enableProgressBars: true,
      showTypingCursor: true,
      exportFormat: 'svg',
      exportQuality: 'high',
      includeMetadata: true,
      highContrast: false,
      reducedMotion: false,
      screenReaderMode: false,
      keyboardNavigation: true
    }
    componentOverrides.value = {}
  }
  
  // Auto-save settings to localStorage
  const saveToStorage = () => {
    try {
      const settings = exportSettings()
      localStorage.setItem('digi-setu-component-settings', JSON.stringify(settings))
    } catch (error) {
      console.warn('Failed to save settings to localStorage:', error)
    }
  }
  
  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem('digi-setu-component-settings')
      if (stored) {
        const settings = JSON.parse(stored)
        importSettings(settings)
        return true
      }
    } catch (error) {
      console.warn('Failed to load settings from localStorage:', error)
    }
    return false
  }
  
  // Watch for changes and auto-save
  watch(globalSettings, saveToStorage, { deep: true })
  watch(componentOverrides, saveToStorage, { deep: true })
  
  // Component-specific helpers
  const getTableSettings = (componentId = 'default-table') => {
    const settings = getComponentSettings(componentId)
    return {
      showControls: settings.showControls,
      showStats: settings.showStats,
      animationsEnabled: settings.animationsEnabled,
      chunkSize: settings.chunkSize,
      renderDelay: settings.renderDelay,
      compactMode: settings.compactMode,
      theme: currentTheme.value,
      animationSpeed: currentAnimationSpeed.value
    }
  }
  
  const getCodeSettings = (componentId = 'default-code') => {
    const settings = getComponentSettings(componentId)
    return {
      showControls: settings.showControls,
      showStats: settings.showStats,
      animationsEnabled: settings.animationsEnabled,
      chunkSize: settings.chunkSize,
      renderDelay: settings.renderDelay,
      fontFamily: currentFontFamily.value,
      fontSize: settings.fontSize,
      theme: currentTheme.value,
      showTypingCursor: settings.showTypingCursor
    }
  }
  
  const getJsonSettings = (componentId = 'default-json') => {
    const settings = getComponentSettings(componentId)
    return {
      showControls: settings.showControls,
      showStats: settings.showStats,
      animationsEnabled: settings.animationsEnabled,
      chunkSize: settings.chunkSize,
      renderDelay: settings.renderDelay,
      compactMode: settings.compactMode,
      theme: currentTheme.value,
      fontFamily: currentFontFamily.value
    }
  }
  
  const getDiagramSettings = (componentId = 'default-diagram') => {
    const settings = getComponentSettings(componentId)
    return {
      showControls: settings.showControls,
      showStats: settings.showStats,
      animationsEnabled: settings.animationsEnabled,
      chunkSize: settings.chunkSize,
      renderDelay: settings.renderDelay,
      theme: currentTheme.value,
      exportFormat: settings.exportFormat,
      exportQuality: settings.exportQuality
    }
  }
  
  // Accessibility helpers
  const getAccessibilityProps = () => {
    const settings = globalSettings.value
    return {
      'aria-live': settings.screenReaderMode ? 'polite' : 'off',
      'data-high-contrast': settings.highContrast,
      'data-reduced-motion': settings.reducedMotion,
      'tabindex': settings.keyboardNavigation ? '0' : '-1'
    }
  }
  
  // Initialize on first use
  let initialized = false
  const initialize = () => {
    if (!initialized) {
      loadFromStorage()
      initialized = true
    }
  }
  
  return {
    // State
    globalSettings: readonly(globalSettings),
    componentOverrides: readonly(componentOverrides),
    
    // Computed
    currentTheme,
    currentAnimationSpeed,
    currentFontFamily,
    cssVariables,
    
    // Methods
    getComponentSettings,
    setComponentOverride,
    removeComponentOverride,
    updateGlobalSettings,
    
    // Presets
    presets: readonly(presets),
    applyPreset,
    
    // Import/Export
    exportSettings,
    importSettings,
    resetToDefaults,
    
    // Storage
    saveToStorage,
    loadFromStorage,
    
    // Component helpers
    getTableSettings,
    getCodeSettings,
    getJsonSettings,
    getDiagramSettings,
    getAccessibilityProps,
    
    // Themes and options
    themes: readonly(themes),
    animationSpeeds: readonly(animationSpeeds),
    fontFamilies: readonly(fontFamilies),
    
    // Initialization
    initialize
  }
}
