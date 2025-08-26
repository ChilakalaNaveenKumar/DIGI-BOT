import { ref, computed } from 'vue'
import type { Conversation, ConversationMessage } from '~/types/conversation'

export const useConversations = () => {
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const conversationMessages = ref<ConversationMessage[]>([])
  const isLoading = ref(false)
  const isLoadingMessages = ref(false)
  const error = ref<string | null>(null)

  // Use Pinia auth store and smart fetch
  const authStore = useAuthStore()
  const { get, post, put, delete: del } = useAuthenticatedFetch()

  // Persistent current conversation ID using Nuxt's useCookie
  const currentConversationId = useCookie<number | null>('digi-setu-current-conversation', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 30, // 30 days
    sameSite: 'lax',
    secure: true,
    watch: true
  })

  // Fetch all conversations
  const fetchConversations = async () => {
    if (!authStore.isAuthenticated) {
      error.value = 'Not authenticated'
      return
    }

    try {
      isLoading.value = true
      error.value = null

      const data = await get<Conversation[]>('http://localhost:8000/api/conversations/')

      conversations.value = data
      
      console.log('Conversations fetched:', data.length)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching conversations:', err)
    } finally {
      isLoading.value = false
    }
  }

  // Create a new conversation
  const createConversation = async (title: string = 'Untitled') => {
    if (!authStore.isAuthenticated) {
      throw new Error('Not authenticated')
    }

    try {
      isLoading.value = true
      error.value = null

      const newConversation = await post<Conversation>('http://localhost:8000/api/conversations/', {
        title
      })

      conversations.value.unshift(newConversation)
      currentConversation.value = newConversation
      
      console.log('Conversation created:', newConversation.id)
      return newConversation
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating conversation:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Update conversation (mainly for title updates)
  const updateConversation = async (conversationId: number, updates: Partial<Conversation>) => {
    try {
      const updatedConversation = await $fetch<Conversation>(`http://localhost:8000/api/conversations/${conversationId}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      })
      
      // Update in local state
      const index = conversations.value.findIndex(c => c.id === conversationId)
      if (index !== -1) {
        conversations.value[index] = updatedConversation
      }
      
      if (currentConversation.value?.id === conversationId) {
        currentConversation.value = updatedConversation
      }
      
      console.log('Conversation updated:', conversationId)
      return updatedConversation
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating conversation:', err)
      throw err
    }
  }

  // Delete conversation
  const deleteConversation = async (conversationId: number) => {
    try {
      await $fetch(`http://localhost:8000/api/conversations/${conversationId}`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      // Remove from local state
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      
      if (currentConversation.value?.id === conversationId) {
        currentConversation.value = null
      }
      
      console.log('Conversation deleted:', conversationId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error deleting conversation:', err)
      throw err
    }
  }

  // Set current conversation
  const setCurrentConversation = (conversation: Conversation | null) => {
    currentConversation.value = conversation
  }

  // Generate title from AI response
  const generateTitle = (aiResponse: string): string => {
    if (!aiResponse || aiResponse.length < 10) {
      return 'Untitled'
    }

    // Extract first meaningful sentence or phrase
    const sentences = aiResponse.split(/[.!?]+/)
    const firstSentence = sentences[0]?.trim()
    
    if (firstSentence && firstSentence.length > 5) {
      // Limit title length and clean it up
      let title = firstSentence.substring(0, 50)
      
      // Remove markdown formatting
      title = title.replace(/[*_`#]/g, '')
      
      // Remove common AI response prefixes
      title = title.replace(/^(I'll|I can|Let me|Here's|This is|I'm|I'd be happy to|Sure,?)/i, '')
      
      // Clean up whitespace
      title = title.trim()
      
      if (title.length > 5) {
        return title + (title.length === 50 ? '...' : '')
      }
    }
    
    return 'Untitled'
  }

  // Computed properties
  const sortedConversations = computed(() => {
    return [...conversations.value].sort((a, b) => {
      // Sort by last message time or updated time (most recent first)
      const aTime = a.last_message_at || a.updated_at
      const bTime = b.last_message_at || b.updated_at
      
      return new Date(bTime).getTime() - new Date(aTime).getTime()
    })
  })

  // Load conversation history (messages)
  const loadConversationHistory = async (conversationId: number) => {
    if (!authStore.isAuthenticated) {
      error.value = 'Not authenticated'
      return []
    }

    try {
      isLoadingMessages.value = true
      error.value = null

      const messages = await get<ConversationMessage[]>(`http://localhost:8000/api/conversations/${conversationId}/messages`)

      conversationMessages.value = messages
      
      // Set current conversation
      const conversation = conversations.value.find(c => c.id === conversationId)
      if (conversation) {
        currentConversation.value = conversation
      }
      
      console.log('Conversation history loaded:', conversationId, messages.length, 'messages')
      return messages
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error loading conversation history:', err)
      return []
    } finally {
      isLoadingMessages.value = false
    }
  }

  // Switch to a conversation and load its history
  const switchToConversation = async (conversationId: number) => {
    const messages = await loadConversationHistory(conversationId)
    // Persist the current conversation ID using reactive cookie
    currentConversationId.value = conversationId
    
    // Also update the streaming chat state to sync conversation ID and title
    const conversation = conversations.value.find(c => c.id === conversationId)
    if (conversation) {
      // We need to import and use the streaming chat composable here
      // This will be handled by the caller (Sidebar.vue) instead
    }
    
    return messages
  }

  // Auto-restore conversation on app start
  const restoreCurrentConversation = async () => {
    const savedId = currentConversationId.value
    if (savedId && authStore.isAuthenticated) {
      console.log('Restoring conversation:', savedId)
      try {
        // Check if conversation exists in our list
        await fetchConversations()
        const conversation = conversations.value.find(c => c.id === savedId)
        if (conversation) {
          const messages = await loadConversationHistory(savedId)
          return { conversation, messages }
        } else {
          // Conversation doesn't exist anymore, clear saved ID
          currentConversationId.value = null
        }
      } catch (error) {
        console.error('Failed to restore conversation:', error)
        currentConversationId.value = null
      }
    }
    return null
  }

  // Clear current conversation (for new chat)
  const clearCurrentConversation = () => {
    currentConversation.value = null
    conversationMessages.value = []
    currentConversationId.value = null
  }

  return {
    conversations: sortedConversations,
    currentConversation: readonly(currentConversation),
    conversationMessages: readonly(conversationMessages),
    currentConversationId: readonly(currentConversationId),
    isLoading: readonly(isLoading),
    isLoadingMessages: readonly(isLoadingMessages),
    error: readonly(error),
    fetchConversations,
    createConversation,
    updateConversation,
    deleteConversation,
    loadConversationHistory,
    switchToConversation,
    restoreCurrentConversation,
    clearCurrentConversation,
    setCurrentConversation,
    generateTitle
  }
}
