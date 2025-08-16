<template>
  <div class="digi-setu-app" :class="{ 'dark': isDark }">
    <!-- Sidebar -->
    <aside class="ds-sidebar" :class="{ 'collapsed': sidebarCollapsed }">
      <ClientOnly>
        <DigiSetuSidebar 
          :projects="projects"
          :conversations="conversations"
          :collapsed="sidebarCollapsed"
          :current-project-id="currentProjectId"
          :current-conversation-id="currentConversationId"
          @toggle="toggleSidebar"
          @select-project="selectProject"
          @select-conversation="selectConversation"
          @new-conversation="createNewConversation"
        />
        <template #fallback>
          <div class="ds-sidebar-loading">
            <div class="ds-logo">
              <div class="ds-logo-icon">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="32" height="32" rx="8" fill="var(--ds-primary)"/>
                  <path d="M8 12h16v2H8v-2zm0 4h16v2H8v-2zm0 4h12v2H8v-2z" fill="white"/>
                  <circle cx="20" cy="20" r="3" fill="var(--ds-secondary)"/>
                </svg>
              </div>
              <div class="ds-logo-text">
                <h1 class="ds-logo-title">Digi Setu</h1>
                <p class="ds-logo-subtitle">AI Assistant</p>
              </div>
            </div>
          </div>
        </template>
      </ClientOnly>
    </aside>

    <!-- Main Content -->
    <main class="ds-main">
      <!-- Header -->
      <header class="ds-header">
        <ClientOnly>
          <DigiSetuHeader 
            :current-project="currentProject"
            :current-conversation="currentConversation"
            :theme="theme"
            :selected-model="selectedModel"
            :selection-reason="selectionReason"
            :orchestrator-status="orchestratorStatus"
            @toggle-theme="toggleTheme"
            @new-conversation="createNewConversation"
            @toggle-sidebar="toggleSidebar"
          />
          <template #fallback>
            <div class="ds-header-loading">
              <div class="ds-header-left">
                <div class="ds-current-context">Loading...</div>
              </div>
              <div class="ds-header-center">
                <div class="ds-ai-status">
                  <span class="ds-status-text">Loading...</span>
                </div>
              </div>
              <div class="ds-header-right">
                <div class="ds-provider-selector">
                  <span>GPT-5</span>
                </div>
              </div>
            </div>
          </template>
        </ClientOnly>
      </header>

      <!-- Page Content -->
      <div class="ds-content">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useDigiSetuTheme } from '~/composables/useDigiSetuTheme'
import { useDigiSetuProjects } from '~/composables/useDigiSetuProjects'
import { useDigiSetuConversations } from '~/composables/useDigiSetuConversations'
import DigiSetuSidebar from '~/components/layout/DigiSetuSidebar.vue'
import DigiSetuHeader from '~/components/layout/DigiSetuHeader.vue'

// Theme management
const { isDark, theme, toggleTheme, loadSavedTheme } = useDigiSetuTheme()

// Projects management
const {
  projects,
  currentProjectId,
  currentProject,
  selectProject,
  createProject,
  loadProjects
} = useDigiSetuProjects()

// Conversations management
const {
  conversations,
  currentConversationId,
  currentConversation,
  messages,
  isLoading,
  currentActivity,
  selectConversation,
  createNewConversation,
  handleSendMessage,
  handleRegenerateMessage,
  loadConversations
} = useDigiSetuConversations()

// Sidebar state
const sidebarCollapsed = ref(false)

// AI Orchestrator state
const selectedModel = ref('gpt-5')
const selectionReason = ref('Best for general reasoning tasks')
const orchestratorStatus = ref('active')

// Methods
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// Initialize data
onMounted(async () => {
  // Load saved theme
  loadSavedTheme()
  
  // Load projects and conversations
  await loadProjects()
  await loadConversations()
  
  // Create default project if none exist
  if (projects.value.length === 0) {
    await createProject('Default Project', 'Your main workspace')
  }
  
  // Select first project if none selected
  if (!currentProjectId.value && projects.value.length > 0) {
    selectProject(projects.value[0].id)
  }
  
  console.log('🎨 Digi Setu Layout Initialized')
})

// Watch for project changes to load conversations
watch(currentProjectId, async (newProjectId) => {
  if (newProjectId) {
    await loadConversations(newProjectId)
  }
}, { immediate: true })
</script>

<style scoped>
.digi-setu-app {
  display: flex;
  height: 100vh;
  background: var(--ds-bg-primary);
  color: var(--ds-text-primary);
  font-family: var(--ds-font-primary);
}

.ds-sidebar {
  width: var(--ds-sidebar-width);
  min-width: var(--ds-sidebar-width);
  background: var(--ds-bg-secondary);
  border-right: 1px solid var(--ds-border-primary);
  transition: all var(--ds-transition-normal);
  z-index: 10;
}

.ds-sidebar.collapsed {
  width: var(--ds-sidebar-collapsed-width);
  min-width: var(--ds-sidebar-collapsed-width);
}

.ds-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ds-header {
  height: var(--ds-header-height);
  min-height: var(--ds-header-height);
  background: var(--ds-bg-primary);
  border-bottom: 1px solid var(--ds-border-primary);
  z-index: 5;
}

.ds-content {
  flex: 1;
  overflow: hidden;
  background: var(--ds-bg-primary);
}

/* Dark mode adjustments */
.dark .ds-sidebar {
  background: var(--ds-bg-secondary-dark);
  border-right-color: var(--ds-border-primary-dark);
}

.dark .ds-header {
  background: var(--ds-bg-primary-dark);
  border-bottom-color: var(--ds-border-primary-dark);
}

.dark .ds-content {
  background: var(--ds-bg-primary-dark);
}

/* Loading states */
.ds-sidebar-loading {
  padding: 1rem;
}

.ds-sidebar-loading .ds-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.ds-sidebar-loading .ds-logo-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: var(--ds-text-primary);
}

.ds-sidebar-loading .ds-logo-subtitle {
  font-size: 0.75rem;
  color: var(--ds-text-secondary);
  margin: 0;
}

.ds-header-loading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  height: 100%;
  color: var(--ds-text-secondary);
}

/* Responsive design */
@media (max-width: 768px) {
  .ds-sidebar {
    position: absolute;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 20;
    transform: translateX(-100%);
  }
  
  .ds-sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .ds-main {
    width: 100%;
  }
}
</style>
