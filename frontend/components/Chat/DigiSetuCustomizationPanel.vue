<template>
  <div class="ds-customization-panel" :class="{ 'ds-panel-open': isOpen }">
    <!-- Toggle Button -->
    <button 
      @click="togglePanel"
      class="ds-panel-toggle"
      :title="isOpen ? 'Close Customization' : 'Open Customization'"
    >
      <Settings class="w-5 h-5" />
    </button>

    <!-- Panel Content -->
    <div v-if="isOpen" class="ds-panel-content">
      <div class="ds-panel-header">
        <h3 class="ds-panel-title">
          <Palette class="w-4 h-4" />
          Customization
        </h3>
        <button @click="closePanel" class="ds-close-btn">
          <X class="w-4 h-4" />
        </button>
      </div>

      <div class="ds-panel-body">
        <!-- Quick Presets -->
        <div class="ds-section">
          <h4 class="ds-section-title">Quick Presets</h4>
          <div class="ds-preset-grid">
            <button
              v-for="(preset, key) in presets"
              :key="key"
              @click="applyPreset(key)"
              class="ds-preset-btn"
            >
              <component :is="getPresetIcon(key)" class="w-4 h-4" />
              {{ formatPresetName(key) }}
            </button>
          </div>
        </div>

        <!-- Theme Settings -->
        <div class="ds-section">
          <h4 class="ds-section-title">Theme</h4>
          <div class="ds-control-group">
            <label class="ds-label">Color Theme</label>
            <select v-model="settings.colorTheme" class="ds-select">
              <option v-for="(theme, key) in themes" :key="key" :value="key">
                {{ theme.name }}
              </option>
            </select>
          </div>
          
          <div class="ds-control-group">
            <label class="ds-label">Font Family</label>
            <select v-model="settings.fontFamily" class="ds-select">
              <option value="system">System</option>
              <option value="mono">Monospace</option>
              <option value="serif">Serif</option>
            </select>
          </div>
          
          <div class="ds-control-group">
            <label class="ds-label">Font Size</label>
            <select v-model="settings.fontSize" class="ds-select">
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
            </select>
          </div>
        </div>

        <!-- Animation Settings -->
        <div class="ds-section">
          <h4 class="ds-section-title">Animations</h4>
          <div class="ds-control-group">
            <label class="ds-checkbox-label">
              <input
                type="checkbox"
                v-model="settings.animationsEnabled"
                class="ds-checkbox"
              />
              <span class="ds-checkbox-text">Enable Animations</span>
            </label>
          </div>
          
          <div v-if="settings.animationsEnabled" class="ds-control-group">
            <label class="ds-label">Animation Speed</label>
            <select v-model="settings.animationSpeed" class="ds-select">
              <option value="slow">Slow</option>
              <option value="normal">Normal</option>
              <option value="fast">Fast</option>
            </select>
          </div>
          
          <div class="ds-control-group">
            <label class="ds-checkbox-label">
              <input
                type="checkbox"
                v-model="settings.showTypingCursor"
                class="ds-checkbox"
              />
              <span class="ds-checkbox-text">Show Typing Cursor</span>
            </label>
          </div>
        </div>

        <!-- Progressive Rendering Settings -->
        <div class="ds-section">
          <h4 class="ds-section-title">Progressive Rendering</h4>
          <div class="ds-control-group">
            <label class="ds-label">
              Chunk Size: {{ settings.chunkSize }}
            </label>
            <input
              type="range"
              v-model.number="settings.chunkSize"
              min="1"
              max="10"
              class="ds-slider"
            />
          </div>
          
          <div class="ds-control-group">
            <label class="ds-label">
              Render Delay: {{ settings.renderDelay }}ms
            </label>
            <input
              type="range"
              v-model.number="settings.renderDelay"
              min="0"
              max="500"
              step="10"
              class="ds-slider"
            />
          </div>
          
          <div class="ds-control-group">
            <label class="ds-checkbox-label">
              <input
                type="checkbox"
                v-model="settings.enableProgressBars"
                class="ds-checkbox"
              />
              <span class="ds-checkbox-text">Show Progress Bars</span>
            </label>
          </div>
        </div>

        <!-- Layout Settings -->
        <div class="ds-section">
          <h4 class="ds-section-title">Layout</h4>
          <div class="ds-control-group">
            <label class="ds-checkbox-label">
              <input
                type="checkbox"
                v-model="settings.compactMode"
                class="ds-checkbox"
              />
              <span class="ds-checkbox-text">Compact Mode</span>
            </label>
          </div>
          
          <div class="ds-control-group">
            <label class="ds-checkbox-label">
              <input
                type="checkbox"
                v-model="settings.showControls"
                class="ds-checkbox"
              />
              <span class="ds-checkbox-text">Show Component Controls</span>
            </label>
          </div>
          
          <div class="ds-control-group">
            <label class="ds-checkbox-label">
              <input
                type="checkbox"
                v-model="settings.showStats"
                class="ds-checkbox"
              />
              <span class="ds-checkbox-text">Show Statistics</span>
            </label>
          </div>
        </div>

        <!-- Accessibility Settings -->
        <div class="ds-section">
          <h4 class="ds-section-title">Accessibility</h4>
          <div class="ds-control-group">
            <label class="ds-checkbox-label">
              <input
                type="checkbox"
                v-model="settings.highContrast"
                class="ds-checkbox"
              />
              <span class="ds-checkbox-text">High Contrast</span>
            </label>
          </div>
          
          <div class="ds-control-group">
            <label class="ds-checkbox-label">
              <input
                type="checkbox"
                v-model="settings.reducedMotion"
                class="ds-checkbox"
              />
              <span class="ds-checkbox-text">Reduced Motion</span>
            </label>
          </div>
          
          <div class="ds-control-group">
            <label class="ds-checkbox-label">
              <input
                type="checkbox"
                v-model="settings.screenReaderMode"
                class="ds-checkbox"
              />
              <span class="ds-checkbox-text">Screen Reader Mode</span>
            </label>
          </div>
        </div>

        <!-- Export/Import Settings -->
        <div class="ds-section">
          <h4 class="ds-section-title">Settings Management</h4>
          <div class="ds-button-group">
            <button @click="exportSettings" class="ds-action-btn">
              <Download class="w-4 h-4" />
              Export Settings
            </button>
            <button @click="importSettings" class="ds-action-btn">
              <Upload class="w-4 h-4" />
              Import Settings
            </button>
            <button @click="resetSettings" class="ds-action-btn ds-danger">
              <RotateCcw class="w-4 h-4" />
              Reset to Defaults
            </button>
          </div>
        </div>

        <!-- Developer Settings -->
        <div v-if="showDeveloperSettings" class="ds-section">
          <h4 class="ds-section-title">Developer</h4>
          <div class="ds-control-group">
            <label class="ds-checkbox-label">
              <input
                type="checkbox"
                v-model="settings.showDebugInfo"
                class="ds-checkbox"
              />
              <span class="ds-checkbox-text">Show Debug Information</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Hidden file input for import -->
    <input
      ref="fileInput"
      type="file"
      accept=".json"
      @change="handleFileImport"
      style="display: none"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import {
  Settings,
  Palette,
  X,
  Download,
  Upload,
  RotateCcw,
  Zap,
  Eye,
  Monitor,
  Code
} from 'lucide-vue-next'
import { useComponentCustomization } from '@/composables/useComponentCustomization'

const props = defineProps({
  showDeveloperSettings: {
    type: Boolean,
    default: false
  }
})

// Component customization composable
const {
  globalSettings,
  themes,
  presets,
  applyPreset,
  updateGlobalSettings,
  exportSettings: exportSettingsData,
  importSettings: importSettingsData,
  resetToDefaults,
  initialize
} = useComponentCustomization()

// Initialize customization system
initialize()

// Local state
const isOpen = ref(false)
const fileInput = ref(null)

// Reactive settings (writable copy)
const settings = ref({ ...globalSettings.value })

// Watch for changes and sync with global settings
watch(settings, (newSettings) => {
  updateGlobalSettings(newSettings)
}, { deep: true })

// Watch global settings and sync back to local
watch(globalSettings, (newGlobalSettings) => {
  settings.value = { ...newGlobalSettings }
}, { deep: true })

// Methods
const togglePanel = () => {
  isOpen.value = !isOpen.value
}

const closePanel = () => {
  isOpen.value = false
}

const formatPresetName = (key) => {
  return key.split('-').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const getPresetIcon = (presetKey) => {
  const iconMap = {
    'performance-optimized': Zap,
    'accessibility-focused': Eye,
    'presentation-mode': Monitor,
    'developer-mode': Code
  }
  return iconMap[presetKey] || Settings
}

const exportSettings = () => {
  try {
    const settingsData = exportSettingsData()
    const blob = new Blob([JSON.stringify(settingsData, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `digi-setu-settings-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export settings:', error)
  }
}

const importSettings = () => {
  fileInput.value?.click()
}

const handleFileImport = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const settingsData = JSON.parse(e.target.result)
      const success = importSettingsData(settingsData)
      
      if (success) {
        console.log('Settings imported successfully')
      } else {
        console.error('Failed to import settings')
      }
    } catch (error) {
      console.error('Invalid settings file:', error)
    }
  }
  reader.readAsText(file)
  
  // Reset file input
  event.target.value = ''
}

const resetSettings = () => {
  if (confirm('Are you sure you want to reset all settings to defaults?')) {
    resetToDefaults()
  }
}

// Close panel when clicking outside
const handleClickOutside = (event) => {
  if (isOpen.value && !event.target.closest('.ds-customization-panel')) {
    closePanel()
  }
}

// Add event listener for outside clicks
if (typeof window !== 'undefined') {
  window.addEventListener('click', handleClickOutside)
}

// Cleanup
import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('click', handleClickOutside)
  }
})
</script>

<style scoped>
.ds-customization-panel {
  position: fixed;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  z-index: 1000;
  font-family: var(--ds-font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif);
}

.ds-panel-toggle {
  position: absolute;
  left: -48px;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  background: var(--ds-primary, #2563eb);
  color: white;
  border: none;
  border-radius: 8px 0 0 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
}

.ds-panel-toggle:hover {
  background: var(--ds-primary-hover, #1d4ed8);
  transform: translateY(-50%) translateX(-2px);
}

.ds-panel-content {
  width: 320px;
  max-height: 80vh;
  background: var(--ds-surface, #ffffff);
  border: 1px solid var(--ds-border, #e2e8f0);
  border-radius: 12px 0 0 12px;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.ds-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--ds-surface-secondary, #f8fafc);
  border-bottom: 1px solid var(--ds-border, #e2e8f0);
}

.ds-panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--ds-text, #1e293b);
}

.ds-close-btn {
  background: none;
  border: none;
  color: var(--ds-text-muted, #64748b);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.ds-close-btn:hover {
  background: var(--ds-surface-hover, #f1f5f9);
  color: var(--ds-text, #1e293b);
}

.ds-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.ds-section {
  padding: 16px 20px;
  border-bottom: 1px solid var(--ds-border-secondary, #f1f5f9);
}

.ds-section:last-child {
  border-bottom: none;
}

.ds-section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--ds-text, #1e293b);
}

.ds-control-group {
  margin-bottom: 12px;
}

.ds-control-group:last-child {
  margin-bottom: 0;
}

.ds-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--ds-text, #1e293b);
  margin-bottom: 4px;
}

.ds-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--ds-border, #e2e8f0);
  border-radius: 6px;
  background: var(--ds-surface, #ffffff);
  color: var(--ds-text, #1e293b);
  font-size: 13px;
  transition: border-color 0.2s ease;
}

.ds-select:focus {
  outline: none;
  border-color: var(--ds-primary, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.ds-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
}

.ds-checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--ds-primary, #2563eb);
}

.ds-checkbox-text {
  color: var(--ds-text, #1e293b);
  font-weight: 500;
}

.ds-slider {
  width: 100%;
  height: 4px;
  background: var(--ds-border, #e2e8f0);
  border-radius: 2px;
  outline: none;
  appearance: none;
}

.ds-slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: var(--ds-primary, #2563eb);
  border-radius: 50%;
  cursor: pointer;
}

.ds-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: var(--ds-primary, #2563eb);
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

.ds-preset-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.ds-preset-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--ds-surface, #ffffff);
  border: 1px solid var(--ds-border, #e2e8f0);
  border-radius: 6px;
  color: var(--ds-text, #1e293b);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ds-preset-btn:hover {
  background: var(--ds-surface-hover, #f8fafc);
  border-color: var(--ds-primary, #2563eb);
}

.ds-button-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ds-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--ds-surface, #ffffff);
  border: 1px solid var(--ds-border, #e2e8f0);
  border-radius: 6px;
  color: var(--ds-text, #1e293b);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ds-action-btn:hover {
  background: var(--ds-surface-hover, #f8fafc);
}

.ds-action-btn.ds-danger {
  color: var(--ds-danger, #dc2626);
  border-color: var(--ds-danger-light, #fecaca);
}

.ds-action-btn.ds-danger:hover {
  background: var(--ds-danger-light, #fef2f2);
}

/* Scrollbar styling */
.ds-panel-body::-webkit-scrollbar {
  width: 6px;
}

.ds-panel-body::-webkit-scrollbar-track {
  background: var(--ds-surface, #ffffff);
}

.ds-panel-body::-webkit-scrollbar-thumb {
  background: var(--ds-border, #e2e8f0);
  border-radius: 3px;
}

.ds-panel-body::-webkit-scrollbar-thumb:hover {
  background: var(--ds-text-muted, #64748b);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .ds-panel-content {
    width: 280px;
    max-height: 70vh;
  }
  
  .ds-panel-toggle {
    left: -44px;
    width: 36px;
    height: 36px;
  }
  
  .ds-preset-grid {
    grid-template-columns: 1fr;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .ds-panel-content {
    border-width: 2px;
  }
  
  .ds-select,
  .ds-preset-btn,
  .ds-action-btn {
    border-width: 2px;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .ds-panel-toggle,
  .ds-close-btn,
  .ds-select,
  .ds-preset-btn,
  .ds-action-btn {
    transition: none;
  }
}
</style>
