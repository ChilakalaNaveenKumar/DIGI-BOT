<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo-section">
        <div class="logo-icon">
          <Icon name="lucide:cpu" :size="20" />
        </div>
        <h1 class="logo-text">Digi Setu</h1>
      </div>
      
      <button class="new-chat-btn" @click="handleNewChat">
        <Icon name="lucide:plus" :size="16" />
        New chat
      </button>
    </div>
    
    <nav class="sidebar-nav">
      <div class="nav-section">
        <h2 class="nav-title">Chats</h2>
        
        <!-- Loading state -->
        <div v-if="isLoading" class="loading-conversations">
          <div class="loading-item" v-for="i in 3" :key="i">
            <div class="loading-icon"></div>
            <div class="loading-text"></div>
          </div>
        </div>
        
        <!-- Conversations list -->
        <div v-else-if="conversations.length > 0" class="nav-items">
          <button
            v-for="conversation in conversations"
            :key="conversation.id"
            @click="handleSelectConversation(conversation)"
            :class="['nav-item', { active: currentConversation?.id === conversation.id }]"
          >
            <Icon name="lucide:messages-square" class="nav-icon" :size="16" />
            <span class="conversation-title">{{ conversation.title }}</span>
            <button
              v-if="conversation.id === currentConversation?.id"
              @click.stop="handleDeleteConversation(conversation.id)"
              class="delete-btn"
            >
              <Icon name="lucide:trash-2" :size="12" />
            </button>
          </button>
        </div>
        
        <!-- Empty state -->
        <div v-else class="empty-conversations">
          <Icon name="lucide:messages-square" :size="24" class="empty-icon" />
          <p class="empty-text">No conversations yet</p>
          <p class="empty-subtext">Start a new chat to begin</p>
        </div>
      </div>
    </nav>
    
    <div class="sidebar-footer">
      <LayoutThemeToggle />
      <LayoutUserMenu />
    </div>
  </aside>
</template>

<script setup lang="ts">
import { onMounted, computed, watch } from 'vue'

// Use Pinia stores
const authStore = useAuthStore()
const chatStore = useChatStore()
const conversationStore = useConversationStore()

// Reactive references to store state
const conversations = computed(() => conversationStore.conversations)
const currentConversation = computed(() => conversationStore.currentConversation)
const isLoading = computed(() => conversationStore.isLoading)

// Event handlers
const handleNewChat = async () => {
  try {
    // Clear current conversation and chat state
    conversationStore.clearCurrentConversation()
    chatStore.startNewConversation()
    
    console.log('Started new conversation (will be created on first message)')
    
    // Navigate to chat page if not already there
    await navigateTo('/chat')
  } catch (error) {
    console.error('Failed to start new conversation:', error)
  }
}

const handleSelectConversation = async (conversation: any) => {
  try {
    console.log('Switching to conversation:', conversation.id)
    
    // Load conversation history from API
    const messages = await conversationStore.switchToConversation(conversation.id)
    
    // Update chat store state
    chatStore.setConversationState(conversation.id, conversation.title)
    
    // Load messages into chat interface
    if (messages.length > 0) {
      chatStore.loadConversationMessages(messages)
      console.log('Loaded', messages.length, 'messages into chat')
    } else {
      // Clear chat if no messages
      chatStore.startNewConversation()
    }
    
    // Navigate to chat page
    await navigateTo('/chat')
  } catch (error) {
    console.error('Failed to switch conversation:', error)
  }
}

const handleDeleteConversation = async (conversationId: number) => {
  if (confirm('Are you sure you want to delete this conversation?')) {
    try {
      await conversationStore.deleteConversation(conversationId)
      console.log('Conversation deleted:', conversationId)
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    }
  }
}

// Load conversations when auth is ready
onMounted(async () => {
  // Wait for auth store to be initialized
  if (!authStore.isInitialized) {
    await authStore.initialize()
  }
  
  // Now fetch conversations if authenticated
  if (authStore.isAuthenticated) {
    conversationStore.fetchConversations()
  }
})

// Also watch for auth state changes (e.g., after login)
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated) {
    conversationStore.fetchConversations()
  }
}, { immediate: false })
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 260px;
  height: 100vh;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-primary);
  display: flex;
  flex-direction: column;
  z-index: 50;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-primary);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: var(--accent-primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.new-chat-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
}

.nav-section {
  padding: 5px;
}

.nav-title {
  font-size: 14px;
  font-weight: 400;
  color: var(--text-secondary);
  text-transform: none;
  letter-spacing: 0;
  margin: 0 0 12px 0;
}

.nav-items {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  color: var(--text-secondary);
  text-decoration: none;
  border: none;
  background: transparent;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
  text-align: left;
  cursor: pointer;
  position: relative;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item:hover:not(.active) {
  background: var(--bg-hover);
}

.nav-item.active {
  background: var(--bg-hover);
  color: var(--text-primary);
  font-weight: 400;
}

.nav-icon {
  opacity: 0.7;
  flex-shrink: 0;
}

.nav-item.active .nav-icon {
  opacity: 0.7;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-primary);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* User section styles moved to UserMenu component */

/* New conversation-related styles */
.conversation-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.delete-btn {
  opacity: 0;
  padding: 4px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.nav-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.loading-conversations {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.loading-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
}

.loading-icon {
  width: 16px;
  height: 16px;
  background: var(--bg-tertiary);
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.loading-text {
  flex: 1;
  height: 12px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  animation: pulse 1.5s ease-in-out infinite;
}

.empty-conversations {
  text-align: center;
  padding: 24px 12px;
}

.empty-icon {
  color: var(--text-muted);
  margin-bottom: 8px;
}

.empty-text {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 4px 0;
}

.empty-subtext {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>