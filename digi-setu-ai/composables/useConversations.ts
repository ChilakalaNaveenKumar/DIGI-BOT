import { ref, computed } from 'vue'

export interface Conversation {
  id: number
  title: string
  status: string
  message_count: number
  created_at: string
  updated_at: string
  last_message_at?: string
  storage_type?: string  // 'active' | 'archived'
}

export const useConversations = () => {
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Use Pinia auth store
  const authStore = useAuthStore()

  // Fetch all conversations
  const fetchConversations = async () => {
    if (!authStore.isAuthenticated) {
      error.value = 'Not authenticated'
      return
    }

    try {
      isLoading.value = true
      error.value = null

      const data = await $fetch<Conversation[]>('http://localhost:8000/api/conversations/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      })

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

      const newConversation = await $fetch<Conversation>('http://localhost:8000/api/conversations/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title
        })
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
