import type { Message, ReasoningStep } from '~/types'
import { nextTick } from 'vue'

// Singleton state - shared across all instances
const messages = ref<Message[]>([])
const isLoading = ref(false)
const isStreaming = ref(false)
const conversationId = ref<number | null>(null)
const conversationTitle = ref<string>('')
const currentReasoningSteps = ref<ReasoningStep[]>([])
const isReasoning = ref(false)
const isProcessingComponents = ref(false)

export const useStreamingChat = () => {

  // Build conversation history for API call
  const buildConversationHistory = (newUserMessage: string) => {
    const history: Array<{ role: 'user' | 'assistant', content: string }> = []
    
    // For existing conversations, only send recent context (last 10 messages) + new message
    // For new conversations, send just the new message
    if (conversationId.value) {
      // Existing conversation: Send recent context for better AI responses
      const recentMessages = messages.value.slice(-10) // Last 10 messages
      for (const msg of recentMessages) {
        if (msg.role === 'user' || msg.role === 'assistant') {
          history.push({
            role: msg.role,
            content: msg.content
          })
        }
      }
    }
    
    // Add the new user message
    history.push({
      role: 'user',
      content: newUserMessage
    })
    
    return history
  }

  // Save messages to conversation (new or existing)
  const saveMessagesToConversation = async (
    userMessage: string, 
    assistantMessage: string, 
    reasoningSteps: ReasoningStep[]
  ) => {
    try {
      const { post } = useAuthenticatedFetch()
      
      if (!conversationId.value) {
        // NEW CONVERSATION: Create conversation with both messages
        const title = userMessage.length > 50 
          ? userMessage.substring(0, 47) + "..." 
          : userMessage

        const response = await post<{id: number, title: string}>('http://localhost:8000/api/conversations/save-complete', {
          title: title.trim(),
          user_message: userMessage,
          assistant_message: assistantMessage,
          reasoning_steps: reasoningSteps.map(step => ({
            id: step.id,
            type: step.type,
            content: step.content,
            status: step.status,
            timestamp: step.timestamp?.toISOString() || new Date().toISOString(),
            tool_name: step.tool_name,
            result: step.result,
            inputJson: step.inputJson
          })),
          ai_provider: "anthropic",
          ai_model: "claude-sonnet-4-20250514"
        })

        // Update conversation state
        conversationId.value = response.id
        conversationTitle.value = response.title
        
        // Update the conversations composable with the new conversation
        const { setCurrentConversation } = useConversations()
        setCurrentConversation({
          id: response.id,
          title: response.title,
          status: 'active',
          message_count: 2,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_message_at: new Date().toISOString()
        })
        
        console.log('New conversation created and saved:', response.id, response.title)
        
      } else {
        // EXISTING CONVERSATION: Add messages to existing conversation
        
        // Save user message
        await post(`http://localhost:8000/api/conversations/${conversationId.value}/messages`, {
          role: 'user',
          content: userMessage,
          token_count: Math.ceil(userMessage.length / 4) // Rough estimate
        })
        
        // Save assistant message with reasoning steps
        await post(`http://localhost:8000/api/conversations/${conversationId.value}/messages`, {
          role: 'assistant',
          content: assistantMessage,
          ai_provider: "anthropic",
          ai_model: "claude-sonnet-4-20250514",
          reasoning_steps: {
            steps: reasoningSteps.map(step => ({
              id: step.id,
              type: step.type,
              content: step.content,
              status: step.status,
              timestamp: step.timestamp?.toISOString() || new Date().toISOString(),
              tool_name: step.tool_name,
              result: step.result,
              inputJson: step.inputJson
            }))
          },
          token_count: Math.ceil(assistantMessage.length / 4) // Rough estimate
        })
        
        console.log('Messages added to existing conversation:', conversationId.value)
      }
      
    } catch (error) {
      console.error('Failed to save messages to conversation:', error)
    }
  }
  
  // Note: All state variables are now defined as singletons above
  
  // Add request deduplication and cancellation
  const lastRequestContent = ref<string>('')
  const lastRequestTime = ref<number>(0)
  const currentAbortController = ref<AbortController | null>(null)

  // Component placement processing function
  const processComponentPlacements = (originalContent: string, matches: any[]) => {
    let processedContent = originalContent
    
    // Sort matches by their original position in the content (process from end to start)
    const sortedMatches = [...matches].sort((a, b) => {
      const aPos = originalContent.indexOf(a.placement.anchor_sentence)
      const bPos = originalContent.indexOf(b.placement.anchor_sentence)
      return bPos - aPos // Process from end to beginning to avoid position shifts
    })
    
    console.log('Processing components in order:', sortedMatches.map(m => ({
      anchor: m.placement.anchor_sentence.substring(0, 30) + '...',
      position: m.placement.position,
      originalPos: originalContent.indexOf(m.placement.anchor_sentence)
    })))
    
    for (const match of sortedMatches) {
      const { block_content, placement } = match
      const { anchor_sentence, position } = placement
      
      // Find the anchor sentence in the CURRENT processed content
      let anchorIndex = processedContent.indexOf(anchor_sentence)
      let actualAnchor = anchor_sentence
      
      if (anchorIndex === -1) {
        console.warn('Exact anchor not found:', anchor_sentence.substring(0, 50) + '...')
        
        // Try variations for markdown formatting issues
        const variations = [
          anchor_sentence.replace(/^\*\*/, '').replace(/\*\*$/, ''), // Remove bold
          anchor_sentence + '**', // Add closing bold
          anchor_sentence.replace(/\*\*/g, ''), // Remove all bold
          anchor_sentence.toLowerCase(),
          anchor_sentence.replace(/^\*\*/, '').replace(/\*\*$/, '').toLowerCase()
        ]
        
        for (const variation of variations) {
          const varIndex = processedContent.toLowerCase().indexOf(variation.toLowerCase())
          if (varIndex !== -1) {
            // Find the actual text in the content (preserve case)
            anchorIndex = varIndex
            // Get the actual text from the content
            actualAnchor = processedContent.substring(varIndex, varIndex + variation.length)
            console.log('Found anchor using variation:', variation, 'at index:', anchorIndex)
            break
          }
        }
        
        if (anchorIndex === -1) {
          console.warn('Skipping component - no anchor variation found for:', anchor_sentence.substring(0, 50) + '...')
          continue
        }
      }
      
      let insertIndex: number
      let componentWithNewlines: string
      
      if (position === 'after_sentence') {
        // For after_sentence, find the end of the complete line
        let endOfSentence = anchorIndex + actualAnchor.length
        const restOfContent = processedContent.substring(endOfSentence)
        
        // If the sentence continues with ** (bold formatting), include it
        if (restOfContent.startsWith('**')) {
          endOfSentence += 2
        }
        
        // Find the end of the line
        const nextNewline = processedContent.indexOf('\n', endOfSentence)
        if (nextNewline !== -1) {
          insertIndex = nextNewline
        } else {
          insertIndex = endOfSentence
        }
        
        componentWithNewlines = '\n\n' + block_content + '\n\n'
      } else if (position === 'before_sentence') {
        // Insert before the anchor sentence  
        insertIndex = anchorIndex
        componentWithNewlines = block_content + '\n\n'
      } else {
        console.warn('Unknown placement position:', position)
        continue
      }
      
      // Insert the component at the calculated position
      processedContent = processedContent.slice(0, insertIndex) + 
                       componentWithNewlines + 
                       processedContent.slice(insertIndex)
      
      console.log('✅ Inserted component:', {
        position,
        anchor: anchor_sentence.substring(0, 30) + '...',
        componentType: block_content.split('\n')[0],
        insertedAt: insertIndex
      })
      
      // Debug: Show a snippet of the content around the insertion
      const start = Math.max(0, insertIndex - 50)
      const end = Math.min(processedContent.length, insertIndex + 100)
      console.log('Content around insertion:', processedContent.substring(start, end))
    }
    
    return processedContent
  }

  // Track if we've already processed components for this response
  const processedResponses = new Set<string>()

  // Component matcher function
  const callComponentMatcher = async (aiResponse: string) => {
    // Create a hash of the response to avoid duplicate processing
    const responseHash = aiResponse.substring(0, 100) + aiResponse.length
    if (processedResponses.has(responseHash)) {
      console.log('Skipping duplicate component matcher call')
      return aiResponse
    }
    processedResponses.add(responseHash)
    
    try {
      console.log('Calling component matcher API with AI response:', aiResponse.substring(0, 100) + '...')
      
      const response = await fetch('http://localhost:8000/api/component-matcher/analyze-simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for authentication
        body: JSON.stringify({
          query: aiResponse
        })
      })

      if (!response.ok) {
        throw new Error(`Component matcher API error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('Component matcher response:', result)

      if (result.has_matches && result.data?.matches?.length > 0) {
        console.log('Found component matches:', result.data.matches)
        // Process component placements and return modified content
        return processComponentPlacements(aiResponse, result.data.matches)
      } else {
        console.log('No components found for AI response:', result.message || 'No matches')
        return aiResponse // Return original content if no matches
      }

    } catch (error) {
      console.error('Component matcher API error:', error)
      return aiResponse // Return original content on error
    }
  }

  const sendStreamingMessage = async (content: string) => {
    if (!content.trim() || isLoading.value || isStreaming.value) return
    
    // Prevent duplicate requests within 1 second
    const now = Date.now()
    if (content === lastRequestContent.value && now - lastRequestTime.value < 1000) {
      console.log('Duplicate request prevented:', content)
      return
    }
    
    lastRequestContent.value = content
    lastRequestTime.value = now
    console.log('Sending message:', content) // Debug log

    // Clear reasoning steps for new message to prevent mixing with previous questions
    currentReasoningSteps.value = []
    isReasoning.value = false

    // Add user message
    const userMessage: Message = {
      id: Date.now() + Math.random(),
      content: content.trim(),
      role: 'user',
      timestamp: new Date()
    }
    messages.value.push(userMessage)

    // Create assistant message placeholder
    const assistantMessage: Message = {
      id: Date.now() + Math.random() + 1,
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      isLoading: true,
      isStreaming: false
    }
    messages.value.push(assistantMessage)

    try {
      isLoading.value = true

      // Immediately show "thinking" state
      const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (messageIndex !== -1) {
        const currentMessage = messages.value[messageIndex]
        if (currentMessage) {
          messages.value[messageIndex] = {
            ...currentMessage,
            content: '', // Don't show placeholder, we have reasoning steps
            isLoading: true,
            isStreaming: false
          }
        }
      }

      // Cancel any existing request
      if (currentAbortController.value) {
        currentAbortController.value.abort()
      }
      
      // Create new AbortController for this request
      currentAbortController.value = new AbortController()

      console.log('Sending message to stream API:', content) // Debug log

      // Call the backend's stream API endpoint (cookies will be sent automatically)
      const response = await fetch('http://localhost:8000/api/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for authentication
        body: JSON.stringify({
          messages: buildConversationHistory(content), // Send full conversation history
          conversation_id: conversationId.value,
          model: "claude-sonnet-4-20250514",
          enable_thinking: true,
          thinking_budget: 5000,
          enable_web_search: true,
          temperature: 0.7
        }),
        signal: currentAbortController.value.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Check if response has a body and is readable
      if (!response.body) {
        throw new Error('No response body available for streaming')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      // Update message to start streaming
      const index = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (index !== -1) {
        const currentMessage = messages.value[index]
        if (currentMessage) {
          messages.value[index] = {
            ...currentMessage,
            isLoading: false,
            isStreaming: true
          }
        }
      }

      isLoading.value = false
      isStreaming.value = true

      let accumulatedContent = ''

      try {
        while (true) {
          const { done, value } = await reader.read()
          
          if (done) break

          // Decode the chunk
          const chunk = decoder.decode(value, { stream: true })
          
          // Parse SSE format (data: {...})
          const lines = chunk.split('\n')
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                
                // Handle different message types from Anthropic stream API
                if (data.type === 'thinking_start') {
                  // Start thinking mode
                  isReasoning.value = true
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        content: '', // Don't show placeholder, we have reasoning steps
                        isLoading: false,
                        isStreaming: true
                      }
                    }
                  }
                } else if (data.type === 'content_block_delta' && data.delta?.type === 'thinking_delta') {
                  // Handle thinking content - add to reasoning steps
                  if (data.delta.thinking) {
                    // Check if this is a continuation of existing reasoning or new step
                    const lastStep = currentReasoningSteps.value[currentReasoningSteps.value.length - 1]
                    
                    if (lastStep && lastStep.status === 'active') {
                      // Continue existing reasoning step
                      lastStep.content += data.delta.thinking
                      lastStep.timestamp = new Date()
                    } else {
                      // Create new reasoning step
                      const stepId = `thinking-${Date.now()}-${Math.random()}`
                      const reasoningStep: ReasoningStep = {
                        id: stepId,
                        type: 'thinking',
                        content: data.delta.thinking,
                        status: 'active',
                        timestamp: new Date()
                      }
                      currentReasoningSteps.value.push(reasoningStep)
                    }
                    
                    // Update the assistant message with reasoning steps
                    const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                    if (messageIndex !== -1) {
                      const currentMessage = messages.value[messageIndex]
                      if (currentMessage) {
                        messages.value[messageIndex] = {
                          ...currentMessage,
                          reasoningSteps: [...currentReasoningSteps.value],
                          isLoading: false,
                          isStreaming: true
                        }
                      }
                    }
                  }
                } else if (data.type === 'content_block_stop') {
                  if (data.index === 0) {
                    // Stop thinking mode and mark reasoning steps as completed (thinking block is index 0)
                    isReasoning.value = false
                    
                    // Mark all active thinking steps as completed
                    currentReasoningSteps.value.forEach(step => {
                      if (step.type === 'thinking' && step.status === 'active') {
                        step.status = 'completed'
                      }
                    })
                  } else {
                    // Handle tool completion
                    const lastStep = currentReasoningSteps.value[currentReasoningSteps.value.length - 1]
                    if (lastStep && lastStep.type === 'tool_call' && lastStep.status === 'active') {
                      lastStep.status = 'completed'
                    }
                  }
                  
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        reasoningSteps: [...currentReasoningSteps.value],
                        isLoading: false,
                        isStreaming: true
                      }
                    }
                  }
                } else if (data.type === 'content_block_start') {
                  // Content block started - handle tool calls
                  if (data.content_block?.type === 'server_tool_use') {
                    const toolStep: ReasoningStep = {
                      id: `tool-${data.content_block.id}`,
                      type: 'tool_call',
                      content: `Using ${data.content_block.name}...`,
                      tool_name: data.content_block.name,
                      status: 'active',
                      timestamp: new Date()
                    }
                    currentReasoningSteps.value.push(toolStep)
                    
                    // Update message with new tool step
                    const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                    if (messageIndex !== -1) {
                      const currentMessage = messages.value[messageIndex]
                      if (currentMessage) {
                        messages.value[messageIndex] = {
                          ...currentMessage,
                          reasoningSteps: [...currentReasoningSteps.value]
                        }
                      }
                    }
                  } else if (data.content_block?.type === 'web_search_tool_result') {
                    // Handle web search results
                    const toolStep: ReasoningStep = {
                      id: `web-result-${data.content_block.tool_use_id}`,
                      type: 'tool_call',
                      content: 'Web search results',
                      tool_name: 'web_search',
                      status: 'completed',
                      result: data.content_block.content,
                      timestamp: new Date()
                    }
                    
                    // Find and update the corresponding tool step
                    const existingStepIndex = currentReasoningSteps.value.findIndex(
                      step => step.id === `tool-${data.content_block.tool_use_id}`
                    )
                    
                    if (existingStepIndex !== -1) {
                      const existingStep = currentReasoningSteps.value[existingStepIndex]
                      if (existingStep) {
                        existingStep.result = data.content_block.content
                        existingStep.status = 'completed'
                      }
                    } else {
                      currentReasoningSteps.value.push(toolStep)
                    }
                    
                    // Update message with web search results
                    const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                    if (messageIndex !== -1) {
                      const currentMessage = messages.value[messageIndex]
                      if (currentMessage) {
                        messages.value[messageIndex] = {
                          ...currentMessage,
                          reasoningSteps: [...currentReasoningSteps.value]
                        }
                      }
                    }
                  }

                } else if (data.type === 'content_block_delta' && data.delta?.type === 'input_json_delta') {
                  // Handle tool input streaming
                  const lastStep = currentReasoningSteps.value[currentReasoningSteps.value.length - 1]
                  if (lastStep && lastStep.type === 'tool_call' && lastStep.status === 'active') {
                    if (!(lastStep as any).inputJson) (lastStep as any).inputJson = ''
                    ;(lastStep as any).inputJson += data.delta.partial_json || ''
                    
                    // Try to parse the JSON to extract query for web search
                    if (lastStep.tool_name === 'web_search') {
                      try {
                        const parsed = JSON.parse((lastStep as any).inputJson)
                        if (parsed.query) {
                          lastStep.content = `Searching: ${parsed.query}`
                        }
                      } catch {
                        // JSON not complete yet, keep building
                        lastStep.content = `Preparing search...`
                      }
                    } else {
                      lastStep.content = `Using ${lastStep.tool_name}...`
                    }
                    
                    // Update message with tool input
                    const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                    if (messageIndex !== -1) {
                      const currentMessage = messages.value[messageIndex]
                      if (currentMessage) {
                        messages.value[messageIndex] = {
                          ...currentMessage,
                          reasoningSteps: [...currentReasoningSteps.value]
                        }
                      }
                    }
                  }
                } else if (data.type === 'content_block_delta' && data.delta?.type === 'text_delta') {
                  // Handle actual content streaming (not thinking)
                  if (data.delta.text) {
                    accumulatedContent += data.delta.text
                    
                    // Update message content in real-time
                    const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                    if (messageIndex !== -1) {
                      const currentMessage = messages.value[messageIndex]
                      if (currentMessage) {
                        messages.value[messageIndex] = {
                          ...currentMessage,
                          content: accumulatedContent,
                          isLoading: false,
                          isStreaming: true
                        }
                      }
                    }
                  }
                } else if (data.type === 'message_stop') {
                  // Message completed
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        content: accumulatedContent,
                        isLoading: false,
                        isStreaming: false
                      }
                    }
                  }
                  isStreaming.value = false
                  
                  // Call component matcher API after streaming completes and update content
                  let processedContent = accumulatedContent // Initialize with original content
                  try {
                    isProcessingComponents.value = true
                    
                    // Show component processing indicator
                    const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                    if (messageIndex !== -1) {
                      messages.value[messageIndex] = {
                        ...messages.value[messageIndex],
                        content: accumulatedContent,
                        isStreaming: false,
                        isProcessingComponents: true
                      }
                    }
                    
                    processedContent = await callComponentMatcher(accumulatedContent)
                    if (processedContent && processedContent !== accumulatedContent) {
                      // Use nextTick to ensure Vue has finished current updates
                      await nextTick()
                      // Update the assistant message with processed content that includes components
                      const updatedMessageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                      if (updatedMessageIndex !== -1) {
                        // Create a new message object to trigger reactivity properly
                        messages.value[updatedMessageIndex] = {
                          ...messages.value[updatedMessageIndex],
                          content: processedContent,
                          isStreaming: false,
                          isProcessingComponents: false
                        }
                      }
                    } else {
                      // No components found, just remove processing indicator
                      const updatedMessageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                      if (updatedMessageIndex !== -1) {
                        messages.value[updatedMessageIndex] = {
                          ...messages.value[updatedMessageIndex],
                          isProcessingComponents: false
                        }
                      }
                    }
                  } catch (error) {
                    console.error('Error processing components:', error)
                    // Remove processing indicator on error
                    const errorMessageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                    if (errorMessageIndex !== -1) {
                      messages.value[errorMessageIndex] = {
                        ...messages.value[errorMessageIndex],
                        isProcessingComponents: false
                      }
                    }
                  } finally {
                    isProcessingComponents.value = false
                    
                    // NEW: Save conversation after component processing is complete
                    try {
                      await saveMessagesToConversation(content, processedContent, currentReasoningSteps.value)
                    } catch (error) {
                      console.error('Failed to save conversation:', error)
                    }
                  }
                  
                  break
                } else if (data.type === 'metadata') {
                  // Handle conversation metadata
                  if (data.conversation_id) {
                    conversationId.value = data.conversation_id
                  }
                  if (data.title) {
                    conversationTitle.value = data.title
                  }
                } else if (data.type === 'activity') {
                  // Handle activity messages (like "Creating visualizations...")
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        content: `*${data.content}*`,
                        isLoading: true,
                        isStreaming: false
                      }
                    }
                  }
                } else if (data.type === 'tool_output' && data.content) {
                  // Handle tool outputs (charts, tables, etc.)
                  accumulatedContent += data.content + '\n\n'
                  
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        content: accumulatedContent,
                        isStreaming: true
                      }
                    }
                  }
                } else if (data.type === 'reasoning') {
                  // Handle reasoning/thinking steps - can happen anywhere during conversation
                  isReasoning.value = true
                  
                  // Check if this is a continuation of existing reasoning or new step
                  const lastStep = currentReasoningSteps.value[currentReasoningSteps.value.length - 1]
                  
                  if (lastStep && lastStep.status === 'active') {
                    // Continue existing reasoning step
                    lastStep.content += data.content || ''
                    lastStep.timestamp = new Date()
                  } else {
                    // Create new reasoning step
                    const stepId = `reasoning-${Date.now()}-${Math.random()}`
                    const reasoningStep: ReasoningStep = {
                      id: stepId,
                      type: 'thinking',
                      content: data.content || '',
                      status: 'active',
                      timestamp: new Date()
                    }
                    currentReasoningSteps.value.push(reasoningStep)
                  }
                  
                  // Update the assistant message with reasoning steps
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        reasoningSteps: [...currentReasoningSteps.value],
                        isLoading: false,
                        isStreaming: true
                      }
                    }
                  }
                } else if (data.type === 'conversation_created') {
                  // Handle conversation creation (first message only)
                  conversationId.value = data.conversation_id
                  conversationTitle.value = data.title
                  console.log('Conversation created:', data.conversation_id, data.title)
                } else if (data.type === 'status') {
                  // Handle status messages (like "Thinking...", "Creating visualization...")
                  console.log('Status:', data.content)
                } else if (data.type === 'complete') {
                  // Stream is complete
                  isReasoning.value = false
                  
                  // Mark all reasoning steps as completed
                  currentReasoningSteps.value = currentReasoningSteps.value.map(step => ({
                    ...step,
                    status: 'completed' as const
                  }))
                  
                  // Update the assistant message with final reasoning steps
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        reasoningSteps: [...currentReasoningSteps.value]
                      }
                    }
                  }
                  
                  break
                } else if (data.type === 'error') {
                  throw new Error(data.content || 'Unknown error from backend')
                }
              } catch (parseError) {
                console.warn('Failed to parse streaming data:', parseError)
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }

      // Mark streaming as complete
      const finalIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (finalIndex !== -1) {
        const finalMessage = messages.value[finalIndex]
        if (finalMessage) {
          messages.value[finalIndex] = {
            ...finalMessage,
            isStreaming: false
          }
        }
      }



    } catch (error) {
      // Handle aborted requests silently
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was cancelled')
        return
      }
      
      console.error('Streaming chat error:', error)
      
      // Update message with error
      const errorIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (errorIndex !== -1) {
        const errorMessage = messages.value[errorIndex]
        if (errorMessage) {
          messages.value[errorIndex] = {
            ...errorMessage,
            content: 'Sorry, I encountered an error while processing your request. Please try again.',
            isLoading: false,
            isStreaming: false,
            error: error instanceof Error ? error.message : 'Unknown error'
          }
        }
      }
    } finally {
      isLoading.value = false
      isStreaming.value = false
      currentAbortController.value = null
    }
  }

  const clearMessages = () => {
    messages.value = []
    conversationId.value = null
    conversationTitle.value = ''
  }

  // Load conversation history from API
  const loadConversationMessages = (conversationMessages: Array<{
    id: number
    role: 'user' | 'assistant'
    content: string
    reasoning_steps?: {
      steps: Array<{
        id: string
        type: 'thinking' | 'tool_call'
        content: string
        status: string
        timestamp: string
        tool_name?: string
        result?: unknown
        inputJson?: string
      }>
    }
    created_at: string
  }>) => {
    // Convert API messages to frontend Message format
    const convertedMessages: Message[] = conversationMessages.map(msg => ({
      id: msg.id,
      content: msg.content,
      role: msg.role,
      timestamp: new Date(msg.created_at),
      isLoading: false,
      isStreaming: false,
      reasoningSteps: msg.reasoning_steps?.steps?.map(step => ({
        id: step.id,
        type: step.type,
        content: step.content,
        status: step.status as 'pending' | 'active' | 'completed' | 'error',
        timestamp: new Date(step.timestamp),
        tool_name: step.tool_name,
        result: step.result,
        inputJson: step.inputJson
      })) || []
    }))
    
    messages.value = convertedMessages
    console.log('Loaded conversation messages:', convertedMessages.length)
    console.log('Converted messages:', convertedMessages)
  }
  
  const startNewConversation = () => {
    clearMessages()
    conversationId.value = null
    conversationTitle.value = 'New Conversation'
    currentReasoningSteps.value = []
    isReasoning.value = false
    
    // Clear current conversation in the conversations composable
    const { clearCurrentConversation } = useConversations()
    clearCurrentConversation()
  }

  // Set conversation state (for switching conversations)
  const setConversationState = (id: number | null, title: string) => {
    conversationId.value = id
    conversationTitle.value = title
  }

  const regenerateMessage = async (messageId: string | number) => {
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    const message = messages.value[messageIndex]
    if (!message || message.role !== 'assistant') return

    // Find the user message before this assistant message
    const userMessageIndex = messageIndex - 1
    if (userMessageIndex < 0) return

    const userMessage = messages.value[userMessageIndex]
    if (!userMessage) return
    
    // Remove the assistant message and regenerate
    messages.value.splice(messageIndex, 1)
    await sendStreamingMessage(userMessage.content)
  }

  return {
    messages,
    isLoading,
    isStreaming,
    conversationId: readonly(conversationId),
    conversationTitle: readonly(conversationTitle),
    currentReasoningSteps: readonly(currentReasoningSteps),
    isReasoning: readonly(isReasoning),
    isProcessingComponents: readonly(isProcessingComponents),
    sendMessage: sendStreamingMessage,
    clearMessages,
    loadConversationMessages,
    startNewConversation,
    setConversationState,
    regenerateMessage
  }
}
