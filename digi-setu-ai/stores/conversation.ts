/**
 * Conversation Store using Pinia
 * Manages conversation list, current conversation, and conversation operations
 */

import { defineStore } from 'pinia'
import { useAuthenticatedFetch } from '~/composables/useAuthenticatedFetch'
import type { Conversation, ConversationMessage } from '~/types/conversation'

export interface ConversationState {
  conversations: Conversation[]
  currentConversation: Conversation | null
  conversationMessages: ConversationMessage[]
  isLoading: boolean
  isLoadingMessages: boolean
  error: string | null
}

export const useConversationStore = defineStore('conversation', {
  state: (): ConversationState => ({
    conversations: [],
    currentConversation: null,
    conversationMessages: [],
    isLoading: false,
    isLoadingMessages: false,
    error: null,
  }),

  getters: {
    hasConversations: (state) => state.conversations.length > 0,
    activeConversations: (state) => state.conversations.filter(c => c.status === 'active'),
    archivedConversations: (state) => state.conversations.filter(c => c.status === 'archived'),
  },

  actions: {
    // Fetch all conversations
    async fetchConversations() {
      try {
        this.isLoading = true
        this.error = null
        
        const { get } = useAuthenticatedFetch()
        const conversations = await get<Conversation[]>('http://localhost:8000/api/conversations')
        
        this.conversations = conversations

        
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Conversation Store: Error fetching conversations:', err)
      } finally {
        this.isLoading = false
      }
    },

    // Create new conversation
    async createConversation(title: string = 'Untitled') {
      try {
        const { post } = useAuthenticatedFetch()
        const newConversation = await post<Conversation>('http://localhost:8000/api/conversations', {
          title,
          ai_provider: 'anthropic'
        })
        
        this.conversations.unshift(newConversation)
        this.currentConversation = newConversation
        

        return newConversation
        
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Conversation Store: Error creating conversation:', err)
        throw err
      }
    },

    // Update conversation
    async updateConversation(conversationId: number, updates: { title?: string }) {
      try {
        const { put } = useAuthenticatedFetch()
        const updatedConversation = await put<Conversation>(
          `http://localhost:8000/api/conversations/${conversationId}`,
          updates
        )
        
        const index = this.conversations.findIndex(c => c.id === conversationId)
        if (index !== -1) {
          this.conversations[index] = updatedConversation
        }
        
        if (this.currentConversation?.id === conversationId) {
          this.currentConversation = updatedConversation
        }
        

        return updatedConversation
        
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Conversation Store: Error updating conversation:', err)
        throw err
      }
    },

    // Delete conversation
    async deleteConversation(conversationId: number) {
      try {
        const { delete: del } = useAuthenticatedFetch()
        await del(`http://localhost:8000/api/conversations/${conversationId}`)
        
        this.conversations = this.conversations.filter(c => c.id !== conversationId)
        
        if (this.currentConversation?.id === conversationId) {
          this.currentConversation = null
        }
        

        
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Conversation Store: Error deleting conversation:', err)
        throw err
      }
    },

    // Load conversation history
    async loadConversationHistory(conversationId: number) {
      try {
        this.isLoadingMessages = true
        this.error = null

        const { get } = useAuthenticatedFetch()
        const messages = await get<ConversationMessage[]>(`http://localhost:8000/api/conversations/${conversationId}/messages`)

        this.conversationMessages = messages
        
        // Set current conversation
        const conversation = this.conversations.find(c => c.id === conversationId)
        if (conversation) {
          this.currentConversation = conversation
        }
        

        return messages
        
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Conversation Store: Error loading history:', err)
        return []
      } finally {
        this.isLoadingMessages = false
      }
    },

    // Switch to a conversation and load its history
    async switchToConversation(conversationId: number) {
      const messages = await this.loadConversationHistory(conversationId)
      return messages
    },

    // Set current conversation
    setCurrentConversation(conversation: Conversation | null) {
      this.currentConversation = conversation
    },

    // Clear current conversation
    clearCurrentConversation() {
      this.currentConversation = null
      this.conversationMessages = []
    },

    // Clear error
    clearError() {
      this.error = null
    },


  },

  // Persist state on refresh
  persist: {
    key: 'digi-setu-conversations',
    pick: ['currentConversation'] // Only persist current conversation, not the full list
  }
})
