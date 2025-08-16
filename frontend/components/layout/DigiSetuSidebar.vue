<template>
  <div class="ds-sidebar-content">
    <!-- Digi Setu Logo & New Chat -->
    <div class="ds-sidebar-header">
      <!-- Logo -->
      <div class="ds-logo" :class="{ 'collapsed': collapsed }">
        <div class="ds-logo-icon">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" :fill="collapsed ? 'var(--ds-primary)' : 'var(--ds-primary)'"/>
            <path d="M8 12h16v2H8v-2zm0 4h16v2H8v-2zm0 4h12v2H8v-2z" fill="white"/>
            <circle cx="20" cy="20" r="3" fill="var(--ds-secondary)"/>
          </svg>
        </div>
        <div v-if="!collapsed" class="ds-logo-text">
          <h1 class="ds-logo-title">Digi Setu</h1>
          <p class="ds-logo-subtitle">AI Assistant</p>
        </div>
      </div>

      <!-- New Chat Button -->
      <button class="ds-new-chat-btn" @click="$emit('new-conversation')" :title="collapsed ? 'New Chat' : ''">
        <Plus class="w-4 h-4" />
        <span v-if="!collapsed">New Chat</span>
      </button>
    </div>

    <!-- Projects Section -->
    <div class="ds-sidebar-section" v-if="projects.length > 0">
      <h3 v-if="!collapsed" class="ds-section-title">Projects</h3>
      
      <div class="ds-project-list">
        <div 
          v-for="project in projects" 
          :key="project.id"
          class="ds-project-item"
          :class="{ 'active': project.id === currentProjectId }"
          @click="$emit('select-project', project)"
          :title="collapsed ? project.name : ''"
        >
          <Folder class="w-4 h-4 ds-project-icon" />
          <div v-if="!collapsed" class="ds-project-info">
            <span class="ds-project-name">{{ project.name }}</span>
            <span class="ds-conversation-count">{{ project.conversationCount || 0 }} chats</span>
          </div>
          <div v-if="!collapsed && project.id === currentProjectId" class="ds-active-indicator"></div>
        </div>
      </div>
    </div>

    <!-- Recent Conversations -->
    <div class="ds-sidebar-section ds-conversations-section">
      <h3 v-if="!collapsed" class="ds-section-title">Recent Conversations</h3>
      
      <div class="ds-conversation-list">
        <div 
          v-for="conversation in recentConversations" 
          :key="conversation.id"
          class="ds-conversation-item"
          :class="{ 'active': conversation.id === currentConversationId }"
          @click="$emit('select-conversation', conversation)"
          :title="collapsed ? conversation.title : ''"
        >
          <MessageSquare class="w-4 h-4 ds-conversation-icon" />
          <div v-if="!collapsed" class="ds-conversation-info">
            <span class="ds-conversation-title">{{ conversation.title }}</span>
            <div class="ds-conversation-meta">
              <span class="ds-conversation-time">{{ formatTime(conversation.updatedAt) }}</span>
              <span class="ds-conversation-provider" v-if="conversation.provider">{{ conversation.provider }}</span>
            </div>
          </div>
          <div v-if="!collapsed && conversation.id === currentConversationId" class="ds-active-indicator"></div>
        </div>
      </div>
    </div>

    <!-- Sidebar Footer -->
    <div class="ds-sidebar-footer">
      <!-- Settings Button -->
      <button class="ds-footer-btn" @click="openSettings" :title="collapsed ? 'Settings' : ''">
        <Settings class="w-4 h-4" />
        <span v-if="!collapsed">Settings</span>
      </button>
      
      <!-- Help Button -->
      <button class="ds-footer-btn" @click="openHelp" :title="collapsed ? 'Help' : ''">
        <HelpCircle class="w-4 h-4" />
        <span v-if="!collapsed">Help</span>
      </button>

      <!-- Sidebar Toggle -->
      <button class="ds-sidebar-toggle" @click="$emit('toggle')" :title="collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'">
        <ChevronLeft v-if="!collapsed" class="w-4 h-4" />
        <ChevronRight v-else class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Plus, Folder, MessageSquare, Settings, HelpCircle, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  projects: {
    type: Array,
    default: () => []
  },
  conversations: {
    type: Array,
    default: () => []
  },
  collapsed: {
    type: Boolean,
    default: false
  },
  currentProjectId: {
    type: String,
    default: null
  },
  currentConversationId: {
    type: String,
    default: null
  }
})

const emit = defineEmits([
  'toggle',
  'select-project', 
  'select-conversation',
  'new-conversation'
])

// Computed properties
const recentConversations = computed(() => {
  return [...props.conversations]
    .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
    .slice(0, 10) // Show last 10 conversations
})

// Methods
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diffInHours = (now - date) / (1000 * 60 * 60)
  
  if (diffInHours < 1) {
    return 'Just now'
  } else if (diffInHours < 24) {
    return `${Math.floor(diffInHours)}h ago`
  } else if (diffInHours < 168) { // 7 days
    return `${Math.floor(diffInHours / 24)}d ago`
  } else {
    return date.toLocaleDateString()
  }
}

const openSettings = () => {
  // Emit event or navigate to settings
  console.log('Open settings')
}

const openHelp = () => {
  // Emit event or navigate to help
  console.log('Open help')
}
</script>

<style scoped>
.ds-sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--ds-surface-primary);
}

/* === SIDEBAR HEADER === */
.ds-sidebar-header {
  padding: var(--ds-space-4);
  border-bottom: 1px solid var(--ds-border-primary);
  flex-shrink: 0;
}

.ds-logo {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  margin-bottom: var(--ds-space-4);
  transition: all var(--ds-transition-normal);
}

.ds-logo.collapsed {
  justify-content: center;
}

.ds-logo-icon {
  flex-shrink: 0;
  transition: all var(--ds-transition-normal);
}

.ds-logo-text {
  min-width: 0;
}

.ds-logo-title {
  font-size: var(--ds-text-lg);
  font-weight: var(--ds-font-bold);
  color: var(--ds-text-primary);
  margin: 0;
  line-height: 1.2;
}

.ds-logo-subtitle {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
  margin: 0;
  line-height: 1;
}

.ds-new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--ds-space-2);
  width: 100%;
  padding: var(--ds-space-3) var(--ds-space-4);
  background: var(--ds-primary);
  color: white;
  border: none;
  border-radius: var(--ds-radius-lg);
  font-weight: var(--ds-font-medium);
  font-size: var(--ds-text-sm);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
}

.ds-new-chat-btn:hover {
  background: var(--ds-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--ds-shadow-md);
}

.ds-new-chat-btn:active {
  transform: translateY(0);
}

/* === SIDEBAR SECTIONS === */
.ds-sidebar-section {
  padding: var(--ds-space-4);
  flex-shrink: 0;
}

.ds-conversations-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.ds-section-title {
  font-size: var(--ds-text-xs);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-muted);
  margin: 0 0 var(--ds-space-3) 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* === PROJECT LIST === */
.ds-project-list {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-1);
}

.ds-project-item {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  padding: var(--ds-space-3) var(--ds-space-3);
  border-radius: var(--ds-radius-md);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
  position: relative;
}

.ds-project-item:hover {
  background: var(--ds-surface-hover);
}

.ds-project-item.active {
  background: color-mix(in srgb, var(--ds-primary) 10%, transparent);
  color: var(--ds-primary);
}

.ds-project-item.active .ds-project-icon {
  color: var(--ds-primary);
}

.ds-project-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ds-project-name {
  font-weight: var(--ds-font-medium);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-primary);
  truncate: true;
}

.ds-conversation-count {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
}

/* === CONVERSATION LIST === */
.ds-conversation-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-1);
  padding-right: var(--ds-space-1); /* Space for scrollbar */
}

.ds-conversation-item {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  padding: var(--ds-space-3);
  border-radius: var(--ds-radius-md);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
  position: relative;
}

.ds-conversation-item:hover {
  background: var(--ds-surface-hover);
}

.ds-conversation-item.active {
  background: color-mix(in srgb, var(--ds-primary) 10%, transparent);
  color: var(--ds-primary);
}

.ds-conversation-item.active .ds-conversation-icon {
  color: var(--ds-primary);
}

.ds-conversation-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ds-conversation-title {
  font-weight: var(--ds-font-medium);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-primary);
  truncate: true;
  line-height: 1.3;
}

.ds-conversation-meta {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
}

.ds-conversation-time {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
}

.ds-conversation-provider {
  font-size: var(--ds-text-xs);
  color: var(--ds-secondary);
  background: color-mix(in srgb, var(--ds-secondary) 10%, transparent);
  padding: 1px var(--ds-space-1);
  border-radius: var(--ds-radius-sm);
  text-transform: uppercase;
  font-weight: var(--ds-font-medium);
  letter-spacing: 0.02em;
}

/* === ACTIVE INDICATOR === */
.ds-active-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--ds-primary);
  border-radius: 0 var(--ds-radius-sm) var(--ds-radius-sm) 0;
}

/* === SIDEBAR FOOTER === */
.ds-sidebar-footer {
  padding: var(--ds-space-4);
  border-top: 1px solid var(--ds-border-primary);
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-2);
  flex-shrink: 0;
}

.ds-footer-btn {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: none;
  border: none;
  color: var(--ds-text-secondary);
  font-size: var(--ds-text-sm);
  cursor: pointer;
  border-radius: var(--ds-radius-md);
  transition: all var(--ds-transition-fast);
  justify-content: flex-start;
}

.ds-footer-btn:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-text-primary);
}

.ds-sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-2);
  background: none;
  border: none;
  color: var(--ds-text-muted);
  cursor: pointer;
  border-radius: var(--ds-radius-md);
  transition: all var(--ds-transition-fast);
  margin-top: var(--ds-space-2);
}

.ds-sidebar-toggle:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-text-primary);
}

/* === SCROLLBAR STYLING === */
.ds-conversation-list::-webkit-scrollbar {
  width: 4px;
}

.ds-conversation-list::-webkit-scrollbar-track {
  background: transparent;
}

.ds-conversation-list::-webkit-scrollbar-thumb {
  background: var(--ds-border-secondary);
  border-radius: var(--ds-radius-full);
}

.ds-conversation-list::-webkit-scrollbar-thumb:hover {
  background: var(--ds-text-muted);
}

/* === COLLAPSED STATE === */
.ds-sidebar-content:has(.ds-logo.collapsed) .ds-footer-btn {
  justify-content: center;
}

.ds-sidebar-content:has(.ds-logo.collapsed) .ds-project-item,
.ds-sidebar-content:has(.ds-logo.collapsed) .ds-conversation-item {
  justify-content: center;
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-sidebar-content {
    width: var(--ds-sidebar-width);
  }
}

/* === ACCESSIBILITY === */
.ds-project-item:focus-visible,
.ds-conversation-item:focus-visible,
.ds-footer-btn:focus-visible,
.ds-new-chat-btn:focus-visible,
.ds-sidebar-toggle:focus-visible {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
}

/* === ANIMATIONS === */
.ds-project-item,
.ds-conversation-item {
  animation: ds-fade-in 0.2s ease-out;
}

.ds-active-indicator {
  animation: ds-scale-in 0.2s ease-out;
}

/* === HIGH CONTRAST MODE === */
@media (prefers-contrast: high) {
  .ds-project-item.active,
  .ds-conversation-item.active {
    border: 2px solid var(--ds-primary);
  }
  
  .ds-active-indicator {
    width: 4px;
  }
}
</style>
