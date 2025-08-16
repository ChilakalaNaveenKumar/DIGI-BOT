<template>
  <div class="digi-setu-app" :class="{ 'dark': isDark }">
    <!-- Sidebar -->
    <aside class="ds-sidebar" :class="{ 'collapsed': sidebarCollapsed }">
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
    </aside>

    <!-- Main Content -->
    <main class="ds-main">
      <!-- Header -->
      <header class="ds-header">
        <DigiSetuHeader 
          :current-project="currentProject"
          :current-conversation="currentConversation"
          :theme="theme"
          @toggle-theme="toggleTheme"
          @new-conversation="createNewConversation"
          @toggle-sidebar="toggleSidebar"
        />
      </header>

      <!-- Chat Area -->
      <div class="ds-chat-container">
        <DigiSetuChatContainer 
          :conversation="currentConversation"
          :messages="messages"
          :is-loading="isLoading"
          :current-activity="currentActivity"
          @send-message="handleSendMessage"
          @regenerate-message="handleRegenerateMessage"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useDigiSetuTheme } from '~/composables/useDigiSetuTheme'
import { useDigiSetuProjects } from '~/composables/useDigiSetuProjects'
import { useDigiSetuConversations } from '~/composables/useDigiSetuConversations'
import { useDigiSetuAI } from '~/composables/useDigiSetuAI'

// Theme management
const { theme, isDark, toggleTheme } = useDigiSetuTheme()

// Projects management
const { 
  projects, 
  currentProject, 
  currentProjectId,
  selectProject,
  createProject 
} = useDigiSetuProjects()

// Conversations management
const { 
  conversations, 
  currentConversation, 
  currentConversationId,
  selectConversation,
  createNewConversation 
} = useDigiSetuConversations()

// AI orchestration
const { 
  messages, 
  isLoading, 
  currentActivity,
  sendMessage,
  regenerateMessage 
} = useDigiSetuAI()

// UI state
const sidebarCollapsed = ref(false)

// Methods
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleSendMessage = async (content) => {
  try {
    await sendMessage(content, {
      conversationId: currentConversationId.value,
      projectId: currentProjectId.value
    })
  } catch (error) {
    console.error('Failed to send message:', error)
  }
}

const handleRegenerateMessage = async (messageId) => {
  try {
    await regenerateMessage(messageId)
  } catch (error) {
    console.error('Failed to regenerate message:', error)
  }
}

// Initialize
onMounted(() => {
  // Load saved theme preference
  const savedTheme = localStorage.getItem('digi-setu-theme')
  if (savedTheme) {
    theme.value = savedTheme
  }
  
  // Load projects and conversations
  // This would typically come from an API
  console.log('🚀 Digi Setu AI initialized')
})

// Watch theme changes and save to localStorage
watch(theme, (newTheme) => {
  localStorage.setItem('digi-setu-theme', newTheme)
  document.documentElement.classList.toggle('dark', newTheme === 'dark')
}, { immediate: true })

// Responsive sidebar handling
const handleResize = () => {
  if (window.innerWidth < 768) {
    sidebarCollapsed.value = true
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  handleResize() // Check initial size
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.digi-setu-app {
  display: grid;
  grid-template-columns: var(--ds-sidebar-width) 1fr;
  height: 100vh;
  background: var(--ds-bg-primary);
  color: var(--ds-text-primary);
  font-family: var(--ds-font-primary);
  transition: all var(--ds-transition-normal);
}

.digi-setu-app.dark {
  background: var(--ds-bg-primary);
  color: var(--ds-text-primary);
}

/* Collapsed sidebar */
.ds-sidebar.collapsed {
  width: var(--ds-sidebar-collapsed);
}

.digi-setu-app:has(.ds-sidebar.collapsed) {
  grid-template-columns: var(--ds-sidebar-collapsed) 1fr;
}

.ds-sidebar {
  background: var(--ds-surface-primary);
  border-right: 1px solid var(--ds-border-primary);
  transition: width var(--ds-transition-normal);
  overflow: hidden;
}

.ds-main {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0; /* Prevent flex item from overflowing */
}

.ds-header {
  height: var(--ds-header-height);
  border-bottom: 1px solid var(--ds-border-primary);
  background: var(--ds-surface-primary);
  flex-shrink: 0;
}

.ds-chat-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .digi-setu-app {
    grid-template-columns: 1fr;
    position: relative;
  }
  
  .ds-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: var(--ds-sidebar-width);
    z-index: var(--ds-z-fixed);
    transform: translateX(-100%);
    transition: transform var(--ds-transition-normal);
  }
  
  .ds-sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .ds-sidebar.collapsed {
    transform: translateX(-100%);
  }
  
  /* Overlay for mobile sidebar */
  .digi-setu-app::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: calc(var(--ds-z-fixed) - 1);
    opacity: 0;
    visibility: hidden;
    transition: all var(--ds-transition-normal);
  }
  
  .digi-setu-app:has(.ds-sidebar:not(.collapsed))::before {
    opacity: 1;
    visibility: visible;
  }
}

/* Tablet responsive */
@media (max-width: 1024px) and (min-width: 769px) {
  .digi-setu-app {
    grid-template-columns: 240px 1fr;
  }
  
  :root {
    --ds-sidebar-width: 240px;
  }
}

/* Animation for layout changes */
.ds-sidebar,
.ds-main {
  transition: all var(--ds-transition-normal);
}

/* Focus management for accessibility */
.digi-setu-app:focus-within .ds-sidebar {
  border-right-color: var(--ds-border-focus);
}

/* High contrast mode adjustments */
@media (prefers-contrast: high) {
  .ds-sidebar {
    border-right-width: 2px;
  }
  
  .ds-header {
    border-bottom-width: 2px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .digi-setu-app,
  .ds-sidebar,
  .ds-main {
    transition: none;
  }
}
</style>
