/**
 * Digi Setu Conversations Composable
 * 
 * Manages conversation state, history, and message handling.
 */

import { ref, computed, watch } from 'vue'

// Global conversation state
const conversations = ref([])
const currentConversation = ref(null)
const currentConversationId = ref(null)
const isLoading = ref(false)
const error = ref(null)

// Mock data for development
const mockConversations = [
  {
    id: 1,
    title: "AI Model Comparison Analysis",
    summary: "Detailed comparison of GPT-5, Claude-4, and Grok-4 capabilities",
    status: "active",
    is_pinned: true,
    ai_provider: "openai",
    ai_model: "gpt-5",
    tags: ["analysis", "ai-models", "comparison"],
    message_count: 12,
    total_tokens: 8500,
    created_at: "2024-01-20T10:30:00Z",
    updated_at: "2024-01-20T15:45:00Z",
    last_message_at: "2024-01-20T15:45:00Z",
    user_id: 1,
    project_id: 1
  },
  {
    id: 2,
    title: "Code Review: React Components",
    summary: "AI-assisted review of React component architecture",
    status: "active",
    is_pinned: false,
    ai_provider: "anthropic",
    ai_model: "claude-4",
    tags: ["code-review", "react", "frontend"],
    message_count: 8,
    total_tokens: 6200,
    created_at: "2024-01-19T14:20:00Z",
    updated_at: "2024-01-19T16:30:00Z",
    last_message_at: "2024-01-19T16:30:00Z",
    user_id: 1,
    project_id: 3
  },
  {
    id: 3,
    title: "Content Strategy Planning",
    summary: "AI-powered content strategy and optimization",
    status: "active",
    is_pinned: false,
    ai_provider: "grok",
    ai_model: "grok-4",
    tags: ["content", "strategy", "marketing"],
    message_count: 15,
    total_tokens: 11200,
    created_at: "2024-01-18T09:15:00Z",
    updated_at: "2024-01-18T17:20:00Z",
    last_message_at: "2024-01-18T17:20:00Z",
    user_id: 1,
    project_id: 2
  },
  {
    id: 4,
    title: "Python Script Optimization",
    summary: "Performance optimization for data processing scripts",
    status: "archived",
    is_pinned: false,
    ai_provider: "openai",
    ai_model: "gpt-5",
    tags: ["python", "optimization", "performance"],
    message_count: 6,
    total_tokens: 4100,
    created_at: "2024-01-15T11:00:00Z",
    updated_at: "2024-01-15T13:45:00Z",
    last_message_at: "2024-01-15T13:45:00Z",
    user_id: 1,
    project_id: 3
  }
]

export const useDigiSetuConversations = () => {
  // Computed properties
  const activeConversations = computed(() => {
    return conversations.value.filter(conv => conv.status === 'active')
  })
  
  const pinnedConversations = computed(() => {
    return activeConversations.value.filter(conv => conv.is_pinned)
  })
  
  const recentConversations = computed(() => {
    return [...activeConversations.value]
      .sort((a, b) => new Date(b.last_message_at) - new Date(a.last_message_at))
      .slice(0, 10)
  })
  
  const conversationsByProject = computed(() => {
    const grouped = {}
    
    activeConversations.value.forEach(conv => {
      const projectId = conv.project_id || 'no-project'
      if (!grouped[projectId]) {
        grouped[projectId] = []
      }
      grouped[projectId].push(conv)
    })
    
    return grouped
  })
  
  const conversationsByProvider = computed(() => {
    const grouped = {
      openai: [],
      anthropic: [],
      grok: []
    }
    
    activeConversations.value.forEach(conv => {
      if (grouped[conv.ai_provider]) {
        grouped[conv.ai_provider].push(conv)
      }
    })
    
    return grouped
  })
  
  // Methods
  const loadConversations = async (projectId = null) => {
    isLoading.value = true
    error.value = null
    
    try {
      // TODO: Replace with actual API call
      // const url = projectId ? `/api/v1/conversations?project_id=${projectId}` : '/api/v1/conversations'
      // const response = await $fetch(url)
      // conversations.value = response.data
      
      // Mock implementation
      await new Promise(resolve => setTimeout(resolve, 300))
      
      let filteredConversations = [...mockConversations]
      if (projectId) {
        filteredConversations = filteredConversations.filter(conv => conv.project_id === projectId)
      }
      
      conversations.value = filteredConversations
      
      console.log('💬 Conversations loaded successfully', conversations.value.length)
    } catch (err) {
      error.value = err.message || 'Failed to load conversations'
      console.error('Failed to load conversations:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  const createNewConversation = async (options = {}) => {
    isLoading.value = true
    error.value = null
    
    try {
      // TODO: Replace with actual API call
      // const response = await $fetch('/api/v1/conversations', {
      //   method: 'POST',
      //   body: {
      //     title: options.title || 'New Conversation',
      //     project_id: options.projectId,
      //     ai_provider: options.provider || 'openai',
      //     ai_model: options.model || 'gpt-5'
      //   }
      // })
      
      // Mock implementation
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const newConversation = {
        id: Date.now(),
        title: options.title || 'New Conversation',
        summary: null,
        status: 'active',
        is_pinned: false,
        ai_provider: options.provider || 'openai',
        ai_model: options.model || 'gpt-5',
        tags: options.tags || [],
        message_count: 0,
        total_tokens: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_message_at: new Date().toISOString(),
        user_id: 1,
        project_id: options.projectId || null
      }
      
      conversations.value.unshift(newConversation)
      selectConversation(newConversation)
      
      console.log('✅ New conversation created:', newConversation.title)
      return newConversation
    } catch (err) {
      error.value = err.message || 'Failed to create conversation'
      console.error('Failed to create conversation:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const updateConversation = async (conversationId, updates) => {
    try {
      // TODO: Replace with actual API call
      // const response = await $fetch(`/api/v1/conversations/${conversationId}`, {
      //   method: 'PUT',
      //   body: updates
      // })
      
      // Mock implementation
      const convIndex = conversations.value.findIndex(c => c.id === conversationId)
      if (convIndex !== -1) {
        conversations.value[convIndex] = {
          ...conversations.value[convIndex],
          ...updates,
          updated_at: new Date().toISOString()
        }
        
        // Update current conversation if it's the one being updated
        if (currentConversation.value?.id === conversationId) {
          currentConversation.value = conversations.value[convIndex]
        }
      }
      
      console.log('✅ Conversation updated:', conversationId)
    } catch (err) {
      error.value = err.message || 'Failed to update conversation'
      console.error('Failed to update conversation:', err)
      throw err
    }
  }
  
  const deleteConversation = async (conversationId) => {
    try {
      // TODO: Replace with actual API call
      // await $fetch(`/api/v1/conversations/${conversationId}`, {
      //   method: 'DELETE'
      // })
      
      // Mock implementation
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      
      // Clear current conversation if it was deleted
      if (currentConversation.value?.id === conversationId) {
        currentConversation.value = null
        currentConversationId.value = null
      }
      
      console.log('🗑️ Conversation deleted:', conversationId)
    } catch (err) {
      error.value = err.message || 'Failed to delete conversation'
      console.error('Failed to delete conversation:', err)
      throw err
    }
  }
  
  const archiveConversation = async (conversationId) => {
    await updateConversation(conversationId, { status: 'archived' })
  }
  
  const pinConversation = async (conversationId, pinned = true) => {
    await updateConversation(conversationId, { is_pinned: pinned })
  }
  
  const selectConversation = (conversation) => {
    if (conversation && typeof conversation === 'object') {
      currentConversation.value = conversation
      currentConversationId.value = conversation.id
      
      // Save to localStorage
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('digi-setu-current-conversation', JSON.stringify({
          id: conversation.id,
          title: conversation.title,
          project_id: conversation.project_id
        }))
      }
      
      console.log('💬 Conversation selected:', conversation.title)
    } else {
      currentConversation.value = null
      currentConversationId.value = null
      
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem('digi-setu-current-conversation')
      }
    }
  }
  
  const getConversationById = (conversationId) => {
    return conversations.value.find(c => c.id === conversationId)
  }
  
  const searchConversations = (query) => {
    if (!query || query.trim() === '') {
      return activeConversations.value
    }
    
    const searchTerm = query.toLowerCase().trim()
    return activeConversations.value.filter(conv => 
      conv.title.toLowerCase().includes(searchTerm) ||
      conv.summary?.toLowerCase().includes(searchTerm) ||
      conv.tags?.some(tag => tag.toLowerCase().includes(searchTerm))
    )
  }
  
  const getConversationsByTag = (tag) => {
    return activeConversations.value.filter(conv => 
      conv.tags?.includes(tag)
    )
  }
  
  const getConversationStats = (conversationId) => {
    const conversation = getConversationById(conversationId)
    if (!conversation) return null
    
    return {
      messages: conversation.message_count || 0,
      tokens: conversation.total_tokens || 0,
      provider: conversation.ai_provider,
      model: conversation.ai_model,
      created: conversation.created_at,
      lastActivity: conversation.last_message_at
    }
  }
  
  const getAllTags = () => {
    const tagSet = new Set()
    conversations.value.forEach(conv => {
      if (conv.tags) {
        conv.tags.forEach(tag => tagSet.add(tag))
      }
    })
    return Array.from(tagSet).sort()
  }
  
  // Load saved conversation on initialization
  const loadSavedConversation = () => {
    if (typeof localStorage !== 'undefined') {
      try {
        const saved = localStorage.getItem('digi-setu-current-conversation')
        if (saved) {
          const convData = JSON.parse(saved)
          const conversation = getConversationById(convData.id)
          if (conversation) {
            selectConversation(conversation)
          }
        }
      } catch (err) {
        console.warn('Failed to load saved conversation:', err)
      }
    }
  }
  
  // Watch for conversation changes
  watch(currentConversationId, (newId) => {
    if (newId) {
      const conversation = getConversationById(newId)
      if (conversation && conversation !== currentConversation.value) {
        currentConversation.value = conversation
      }
    }
  })
  
  // Initialize conversations if empty
  if (conversations.value.length === 0) {
    loadConversations()
  }
  
  // Load saved conversation
  loadSavedConversation()
  
  return {
    // State
    conversations: readonly(conversations),
    currentConversation: readonly(currentConversation),
    currentConversationId: readonly(currentConversationId),
    isLoading: readonly(isLoading),
    error: readonly(error),
    
    // Computed
    activeConversations,
    pinnedConversations,
    recentConversations,
    conversationsByProject,
    conversationsByProvider,
    
    // Methods
    loadConversations,
    createNewConversation,
    updateConversation,
    deleteConversation,
    archiveConversation,
    pinConversation,
    selectConversation,
    getConversationById,
    searchConversations,
    getConversationsByTag,
    getConversationStats,
    getAllTags,
    loadSavedConversation
  }
}
