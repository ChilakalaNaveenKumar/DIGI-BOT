import { ref, computed } from 'vue'

export interface Conversation {
  id: number
  title: string
  summary?: string
  status: string
  is_pinned: boolean
  message_count: number
  created_at: string
  updated_at: string
  last_message_at?: string
}

export const useConversations = () => {
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Use enhanced auth system with secure cookies
  const { authenticatedFetch, isAuthenticated } = useEnhancedAuth()

  // Fetch all conversations
  const fetchConversations = async () => {
    if (!isAuthenticated.value) {
      error.value = 'Not authenticated'
      return
    }

    try {
      isLoading.value = true
      error.value = null

      const response = await authenticatedFetch('http://localhost:8000/api/conversations/')

      if (!response.ok) {
        throw new Error(`Failed to fetch conversations: ${response.status}`)
      }

      const data = await response.json()
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
    if (!isAuthenticated.value) {
      throw new Error('Not authenticated')
    }

    try {
      isLoading.value = true
      error.value = null

      const response = await authenticatedFetch('http://localhost:8000/api/conversations/', {
        method: 'POST',
        body: JSON.stringify({
          title,
          ai_provider: 'anthropic'
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to create conversation: ${response.status}`)
      }

      const newConversation = await response.json()
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
      const response = await authenticatedFetch(`http://localhost:8000/api/conversations/${conversationId}`, {
        method: 'PUT',
        body: JSON.stringify(updates)
      })

      if (!response.ok) {
        throw new Error(`Failed to update conversation: ${response.status}`)
      }

      const updatedConversation = await response.json()
      
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
      const response = await authenticatedFetch(`http://localhost:8000/api/conversations/${conversationId}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error(`Failed to delete conversation: ${response.status}`)
      }

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
      // Pinned conversations first
      if (a.is_pinned && !b.is_pinned) return -1
      if (!a.is_pinned && b.is_pinned) return 1
      
      // Then by last message time or updated time
      const aTime = a.last_message_at || a.updated_at
      const bTime = b.last_message_at || b.updated_at
      
      return new Date(bTime).getTime() - new Date(aTime).getTime()
    })
  })

  return {
    conversations: sortedConversations,
    currentConversation: readonly(currentConversation),
    isLoading: readonly(isLoading),
    error: readonly(error),
    fetchConversations,
    createConversation,
    updateConversation,
    deleteConversation,
    setCurrentConversation,
    generateTitle
  }
}
