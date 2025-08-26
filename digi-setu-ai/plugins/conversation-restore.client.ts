/**
 * Auto-restore current conversation on page refresh
 * Only runs on client-side to avoid SSR issues
 */
export default defineNuxtPlugin(async () => {
  // Wait for auth to be initialized
  const authStore = useAuthStore()
  await authStore.initialize()
  
  // Only restore if user is authenticated
  if (authStore.isAuthenticated) {
    const conversationStore = useConversationStore()
    const chatStore = useChatStore()
    
    try {
      // Fetch conversations and restore current one
      await conversationStore.fetchConversations()
      
      if (conversationStore.currentConversation) {

        
        // Load conversation history into chat
        await conversationStore.loadConversationHistory(conversationStore.currentConversation.id)
        
        // Set conversation state in chat store
        chatStore.setConversationState(
          conversationStore.currentConversation.id,
          conversationStore.currentConversation.title
        )
        
        // Load messages into chat interface
        if (conversationStore.conversationMessages.length > 0) {
          chatStore.clearMessages()
          for (const msg of conversationStore.conversationMessages) {
            chatStore.addMessage({
              id: msg.id,
              content: msg.content,
              role: msg.role as 'user' | 'assistant',
              timestamp: new Date(msg.created_at),
              isLoading: false,
              isStreaming: false,
              reasoningSteps: msg.reasoning_steps?.steps ? msg.reasoning_steps.steps.map(step => ({
                id: step.id,
                type: step.type as 'thinking' | 'tool_call',
                content: step.content,
                status: step.status as 'pending' | 'active' | 'completed' | 'error',
                timestamp: new Date(step.timestamp),
                tool_name: step.tool_name,
                result: step.result,
                inputJson: step.inputJson
              })) : []
            })
          }
        }
      }
    } catch (error) {
      console.error('Failed to auto-restore conversation:', error)
    }
  }
})
