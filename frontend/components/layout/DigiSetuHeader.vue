<template>
  <div class="ds-header-content">
    <!-- Left Section -->
    <div class="ds-header-left">
      <!-- Mobile Sidebar Toggle -->
      <button class="ds-mobile-toggle" @click="$emit('toggle-sidebar')" :class="{ 'hidden': !isMobile }">
        <Menu class="w-5 h-5" />
      </button>

      <!-- Current Context -->
      <div class="ds-current-context">
        <div v-if="currentProject" class="ds-context-project">
          <Folder class="w-4 h-4" />
          <span class="ds-project-name">{{ currentProject.name }}</span>
        </div>
        <div v-if="currentConversation" class="ds-context-conversation">
          <ChevronRight class="w-3 h-3 ds-separator" />
          <MessageSquare class="w-4 h-4" />
          <span class="ds-conversation-title">{{ currentConversation.title }}</span>
        </div>
      </div>
    </div>

    <!-- Center Section -->
    <div class="ds-header-center">
      <!-- AI Status Indicator -->
      <div class="ds-ai-status" :class="aiStatusClass">
        <div class="ds-status-indicator"></div>
        <span class="ds-status-text">{{ aiStatusText }}</span>
      </div>
    </div>

    <!-- Right Section -->
    <div class="ds-header-right">
      <!-- AI Orchestrator Status -->
      <div class="ds-orchestrator-status">
        <button class="ds-orchestrator-btn" @click="toggleOrchestratorInfo" title="AI Orchestrator Status">
          <component :is="selectedModelIcon" class="w-4 h-4" />
          <span class="ds-orchestrator-text">{{ selectedModelName }}</span>
          <div class="ds-orchestrator-indicator" :class="orchestratorStatusClass"></div>
        </button>
        
        <!-- Orchestrator Info Panel -->
        <div v-if="showOrchestratorInfo" class="ds-orchestrator-panel" @click.stop>
          <div class="ds-orchestrator-header">
            <Brain class="w-4 h-4" />
            <span class="ds-orchestrator-title">AI Orchestrator</span>
          </div>
          
          <div class="ds-orchestrator-content">
            <div class="ds-current-selection">
              <div class="ds-selection-info">
                <component :is="selectedModelIcon" class="w-5 h-5" />
                <div class="ds-selection-details">
                  <span class="ds-selection-model">{{ selectedModelName }}</span>
                  <span class="ds-selection-reason">{{ selectionReason }}</span>
                </div>
              </div>
            </div>
            
            <div class="ds-orchestrator-divider"></div>
            
            <div class="ds-available-models">
              <div class="ds-models-header">Available Models</div>
              <div 
                v-for="model in availableModels" 
                :key="model.id"
                class="ds-model-item"
                :class="{ 'active': model.id === selectedModel }"
              >
                <component :is="model.icon" class="w-4 h-4" />
                <div class="ds-model-info">
                  <span class="ds-model-name">{{ model.name }}</span>
                  <span class="ds-model-capability">{{ model.capability }}</span>
                </div>
                <div v-if="model.id === selectedModel" class="ds-model-status">
                  <div class="ds-active-indicator"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="ds-header-actions">
        <!-- New Conversation -->
        <button class="ds-action-btn" @click="$emit('new-conversation')" title="New Conversation">
          <Plus class="w-4 h-4" />
        </button>

        <!-- Theme Toggle -->
        <button class="ds-action-btn" @click="$emit('toggle-theme')" :title="themeToggleTitle">
          <Sun v-if="theme === 'dark'" class="w-4 h-4" />
          <Moon v-else class="w-4 h-4" />
        </button>

        <!-- More Options -->
        <button class="ds-action-btn" @click="toggleOptionsMenu" title="More Options">
          <MoreVertical class="w-4 h-4" />
        </button>

        <!-- Options Dropdown -->
        <div v-if="showOptionsMenu" class="ds-options-menu" @click.stop>
          <button class="ds-option-item" @click="exportConversation">
            <Download class="w-4 h-4" />
            <span>Export Chat</span>
          </button>
          <button class="ds-option-item" @click="clearConversation">
            <Trash2 class="w-4 h-4" />
            <span>Clear Chat</span>
          </button>
          <div class="ds-option-divider"></div>
          <button class="ds-option-item" @click="openSettings">
            <Settings class="w-4 h-4" />
            <span>Settings</span>
          </button>
          <button class="ds-option-item" @click="openHelp">
            <HelpCircle class="w-4 h-4" />
            <span>Help</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  Menu, Folder, MessageSquare, ChevronRight, ChevronDown, 
  Plus, Sun, Moon, MoreVertical, Check, Download, Trash2, 
  Settings, HelpCircle, Brain, Zap, Globe 
} from 'lucide-vue-next'

const props = defineProps({
  currentProject: {
    type: Object,
    default: null
  },
  currentConversation: {
    type: Object,
    default: null
  },
  theme: {
    type: String,
    default: 'light'
  },
  aiStatus: {
    type: String,
    default: 'ready' // ready, thinking, processing, error
  },
  selectedModel: {
    type: String,
    default: 'gpt-5'
  },
  selectionReason: {
    type: String,
    default: 'Best for general reasoning tasks'
  },
  orchestratorStatus: {
    type: String,
    default: 'active' // active, selecting, error
  }
})

const emit = defineEmits([
  'toggle-sidebar',
  'new-conversation', 
  'toggle-theme'
])

// Reactive state
const showOrchestratorInfo = ref(false)
const showOptionsMenu = ref(false)
const isMobile = ref(false)

// Available AI models for orchestrator
const availableModels = ref([
  {
    id: 'gpt-5',
    name: 'GPT-5',
    capability: 'Advanced reasoning & analysis',
    icon: Brain
  },
  {
    id: 'claude-4', 
    name: 'Claude-4',
    capability: 'Long context & writing',
    icon: Zap
  },
  {
    id: 'grok-4',
    name: 'Grok-4',
    capability: 'Real-time data & search',
    icon: Globe
  }
])

// Computed properties
const selectedModelData = computed(() => {
  return availableModels.value.find(m => m.id === props.selectedModel) || availableModels.value[0]
})

const selectedModelName = computed(() => selectedModelData.value.name)
const selectedModelIcon = computed(() => selectedModelData.value.icon)

const orchestratorStatusClass = computed(() => {
  return `ds-orchestrator-${props.orchestratorStatus}`
})

const themeToggleTitle = computed(() => {
  return props.theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
})

const aiStatusClass = computed(() => {
  return `ds-status-${props.aiStatus}`
})

const aiStatusText = computed(() => {
  const statusMap = {
    ready: 'Ready',
    thinking: 'Thinking...',
    processing: 'Processing...',
    error: 'Error'
  }
  return statusMap[props.aiStatus] || 'Ready'
})

// Methods
const toggleOrchestratorInfo = () => {
  showOrchestratorInfo.value = !showOrchestratorInfo.value
  showOptionsMenu.value = false
}

const toggleOptionsMenu = () => {
  showOptionsMenu.value = !showOptionsMenu.value
  showOrchestratorInfo.value = false
}

const exportConversation = () => {
  console.log('Export conversation')
  showOptionsMenu.value = false
}

const clearConversation = () => {
  if (confirm('Are you sure you want to clear this conversation?')) {
    console.log('Clear conversation')
  }
  showOptionsMenu.value = false
}

const openSettings = () => {
  console.log('Open settings')
  showOptionsMenu.value = false
}

const openHelp = () => {
  console.log('Open help')
  showOptionsMenu.value = false
}

// Handle clicks outside dropdowns
const handleClickOutside = (event) => {
  if (!event.target.closest('.ds-orchestrator-status')) {
    showOrchestratorInfo.value = false
  }
  if (!event.target.closest('.ds-header-actions')) {
    showOptionsMenu.value = false
  }
}

// Handle responsive behavior
const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('resize', handleResize)
  handleResize()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.ds-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 var(--ds-space-6);
  background: var(--ds-surface-primary);
  border-bottom: 1px solid var(--ds-border-primary);
}

/* === LEFT SECTION === */
.ds-header-left {
  display: flex;
  align-items: center;
  gap: var(--ds-space-4);
  flex: 1;
  min-width: 0;
}

.ds-mobile-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-2);
  background: none;
  border: none;
  color: var(--ds-text-secondary);
  cursor: pointer;
  border-radius: var(--ds-radius-md);
  transition: all var(--ds-transition-fast);
}

.ds-mobile-toggle:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-text-primary);
}

.ds-mobile-toggle.hidden {
  display: none;
}

.ds-current-context {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  min-width: 0;
}

.ds-context-project,
.ds-context-conversation {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  min-width: 0;
}

.ds-project-name,
.ds-conversation-title {
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
  truncate: true;
  font-size: var(--ds-text-sm);
}

.ds-separator {
  color: var(--ds-text-muted);
  flex-shrink: 0;
}

/* === CENTER SECTION === */
.ds-header-center {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}

.ds-ai-status {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  border-radius: var(--ds-radius-full);
  font-size: var(--ds-text-xs);
  font-weight: var(--ds-font-medium);
  transition: all var(--ds-transition-fast);
}

.ds-status-indicator {
  width: 6px;
  height: 6px;
  border-radius: var(--ds-radius-full);
  transition: all var(--ds-transition-fast);
}

.ds-status-ready {
  background: color-mix(in srgb, var(--ds-secondary) 10%, transparent);
  color: var(--ds-secondary);
}

.ds-status-ready .ds-status-indicator {
  background: var(--ds-secondary);
}

.ds-status-thinking {
  background: color-mix(in srgb, var(--ds-primary) 10%, transparent);
  color: var(--ds-primary);
}

.ds-status-thinking .ds-status-indicator {
  background: var(--ds-primary);
  animation: ds-thinking-pulse 1.5s ease-in-out infinite;
}

.ds-status-processing {
  background: color-mix(in srgb, var(--ds-accent) 10%, transparent);
  color: var(--ds-accent);
}

.ds-status-processing .ds-status-indicator {
  background: var(--ds-accent);
  animation: ds-thinking-pulse 1s ease-in-out infinite;
}

.ds-status-error {
  background: color-mix(in srgb, var(--ds-danger) 10%, transparent);
  color: var(--ds-danger);
}

.ds-status-error .ds-status-indicator {
  background: var(--ds-danger);
}

@keyframes ds-thinking-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

/* === RIGHT SECTION === */
.ds-header-right {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  flex: 1;
  justify-content: flex-end;
}

/* === AI ORCHESTRATOR STATUS === */
.ds-orchestrator-status {
  position: relative;
}

.ds-orchestrator-btn {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
  font-weight: var(--ds-font-medium);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
}

.ds-orchestrator-btn:hover {
  background: var(--ds-surface-hover);
  border-color: var(--ds-border-secondary);
}

.ds-orchestrator-text {
  font-size: var(--ds-text-sm);
}

.ds-orchestrator-indicator {
  width: 6px;
  height: 6px;
  border-radius: var(--ds-radius-full);
  transition: all var(--ds-transition-fast);
}

.ds-orchestrator-active .ds-orchestrator-indicator {
  background: var(--ds-secondary);
}

.ds-orchestrator-selecting .ds-orchestrator-indicator {
  background: var(--ds-primary);
  animation: ds-thinking-pulse 1s ease-in-out infinite;
}

.ds-orchestrator-error .ds-orchestrator-indicator {
  background: var(--ds-danger);
}

.ds-orchestrator-panel {
  position: absolute;
  top: calc(100% + var(--ds-space-2));
  right: 0;
  min-width: 320px;
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-xl);
  box-shadow: var(--ds-shadow-lg);
  z-index: var(--ds-z-dropdown);
  animation: ds-scale-in 0.15s ease-out;
  overflow: hidden;
}

.ds-orchestrator-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border-bottom: 1px solid var(--ds-border-primary);
}

.ds-orchestrator-title {
  font-weight: var(--ds-font-semibold);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-primary);
}

.ds-orchestrator-content {
  padding: var(--ds-space-4);
}

.ds-current-selection {
  margin-bottom: var(--ds-space-4);
}

.ds-selection-info {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  padding: var(--ds-space-3);
  background: color-mix(in srgb, var(--ds-primary) 5%, transparent);
  border-radius: var(--ds-radius-lg);
  border: 1px solid color-mix(in srgb, var(--ds-primary) 20%, transparent);
}

.ds-selection-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ds-selection-model {
  font-weight: var(--ds-font-semibold);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-primary);
}

.ds-selection-reason {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
}

.ds-orchestrator-divider {
  height: 1px;
  background: var(--ds-border-primary);
  margin: var(--ds-space-4) 0;
}

.ds-models-header {
  font-size: var(--ds-text-xs);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--ds-space-3);
}

.ds-model-item {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  padding: var(--ds-space-2) var(--ds-space-3);
  border-radius: var(--ds-radius-md);
  transition: all var(--ds-transition-fast);
  margin-bottom: var(--ds-space-1);
}

.ds-model-item:hover {
  background: var(--ds-surface-hover);
}

.ds-model-item.active {
  background: color-mix(in srgb, var(--ds-secondary) 10%, transparent);
}

.ds-model-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ds-model-name {
  font-weight: var(--ds-font-medium);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-primary);
}

.ds-model-capability {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
}

.ds-model-status {
  display: flex;
  align-items: center;
}

.ds-active-indicator {
  width: 6px;
  height: 6px;
  background: var(--ds-secondary);
  border-radius: var(--ds-radius-full);
}

/* === ACTION BUTTONS === */
.ds-header-actions {
  display: flex;
  align-items: center;
  gap: var(--ds-space-1);
  position: relative;
}

.ds-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-2);
  background: none;
  border: none;
  color: var(--ds-text-secondary);
  cursor: pointer;
  border-radius: var(--ds-radius-md);
  transition: all var(--ds-transition-fast);
}

.ds-action-btn:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-text-primary);
}

/* === OPTIONS MENU === */
.ds-options-menu {
  position: absolute;
  top: calc(100% + var(--ds-space-2));
  right: 0;
  min-width: 180px;
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-xl);
  box-shadow: var(--ds-shadow-lg);
  z-index: var(--ds-z-dropdown);
  animation: ds-scale-in 0.15s ease-out;
  padding: var(--ds-space-2);
}

.ds-option-item {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  width: 100%;
  padding: var(--ds-space-2) var(--ds-space-3);
  background: none;
  border: none;
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
  cursor: pointer;
  border-radius: var(--ds-radius-md);
  transition: all var(--ds-transition-fast);
  text-align: left;
}

.ds-option-item:hover {
  background: var(--ds-surface-hover);
}

.ds-option-divider {
  height: 1px;
  background: var(--ds-border-primary);
  margin: var(--ds-space-2) 0;
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-header-content {
    padding: 0 var(--ds-space-4);
  }
  
  .ds-mobile-toggle {
    display: flex;
  }
  
  .ds-current-context {
    display: none;
  }
  
  .ds-header-center {
    flex: 1;
  }
  
  .ds-orchestrator-text {
    display: none;
  }
  
  .ds-orchestrator-panel {
    right: auto;
    left: 0;
  }
}

@media (max-width: 480px) {
  .ds-header-actions {
    gap: 0;
  }
  
  .ds-orchestrator-status {
    display: none;
  }
}

/* === ACCESSIBILITY === */
.ds-action-btn:focus-visible,
.ds-orchestrator-btn:focus-visible,
.ds-option-item:focus-visible {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
}

/* === ANIMATIONS === */
.ds-orchestrator-panel,
.ds-options-menu {
  transform-origin: top right;
}

@keyframes ds-scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
