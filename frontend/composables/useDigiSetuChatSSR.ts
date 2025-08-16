// composables/useDigiSetuChatSSR.ts
// SSR-safe AI SDK 5 composable with enhanced features

import { ref, computed, onMounted, nextTick } from 'vue'
import type { 
  ChatMessage, 
  FileUIPart, 
  Provider, 
  ChatOptions,
  ToolDefinition
} from '~/types/chat'

export const useDigiSetuChatSSR = () => {
  // Provider and model management
  const selectedProvider = ref<string>('openai')
  const selectedModel = ref<string>('')
  const uploadedFiles = ref<FileUIPart[]>([])
  
  // SSR-safe state
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref<boolean>(false)
  const chatError = ref<string | null>(null)
  const isThinking = ref<boolean>(false)
  const currentThought = ref<string>('')
  const input = ref<string>('')
  
  // Chat instance (client-only) - unused but kept for compatibility
  const _chat = ref<unknown>(null)
  const isInitialized = ref<boolean>(false)
  const interactiveTools = ref<Record<string, unknown> | null>(null)
  
  // Provider options
  const providers: Provider[] = [
    { 
      id: 'openai', 
      name: 'GPT-5', 
      icon: 'openai',
      models: ['gpt-5', 'gpt-4o', 'gpt-4o-mini', 'o1', 'o1-mini'],
      description: '1M context, 64k output',
      reasoning: true
    },
    { 
      id: 'anthropic', 
      name: 'Claude 4 Sonnet', 
      icon: 'claude',
      models: ['claude-4-sonnet', 'claude-4-opus', 'claude-3-7-sonnet', 'claude-3-5-sonnet-20241022'],
      description: '200k context, 64k output',
      reasoning: true
    },
    { 
      id: 'grok', 
      name: 'Grok-4', 
      icon: 'xai',
      models: ['grok-4', 'grok-4-vision', 'grok-2-1212'],
      description: '256k context, 256k output',
      reasoning: false
    }
  ]

  // Get available tools (works on both client and server)
  const getAvailableTools = () => {
    // Define tools directly to ensure they're always available
    const toolDefinitions = {
      createTable: {
        description: 'Create an interactive data table from information',
        parameters: {
          type: 'object' as const,
          properties: {
            title: { type: 'string', description: 'Table title' },
            headers: { type: 'array', items: { type: 'string' }, description: 'Column headers' },
            rows: { 
              type: 'array', 
              items: { 
                type: 'array',
                items: { type: 'string' }
              }, 
              description: 'Table data rows (array of arrays)' 
            },
            sortable: { type: 'boolean', description: 'Enable sorting' },
            searchable: { type: 'boolean', description: 'Enable search' }
          },
          required: ['title', 'headers', 'rows']
        }
      },
      
      createQuiz: {
        description: 'Create an interactive quiz from content',
        parameters: {
          type: 'object' as const,
          properties: {
            title: { type: 'string', description: 'Quiz title' },
            questions: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  question: { type: 'string' },
                  options: { type: 'array', items: { type: 'string' } },
                  correct: { type: 'number' },
                  explanation: { type: 'string' }
                }
              }
            }
          },
          required: ['title', 'questions']
        }
      },
      
      createChart: {
        description: 'Create an interactive chart from data',
        parameters: {
          type: 'object' as const,
          properties: {
            title: { type: 'string', description: 'Chart title' },
            type: { type: 'string', enum: ['bar', 'line', 'pie', 'scatter'], description: 'Chart type' },
            data: { 
              type: 'array', 
              items: { 
                type: 'object',
                properties: {
                  label: { type: 'string' },
                  value: { type: 'number' }
                }
              },
              description: 'Chart data points with label and value pairs' 
            },
            xAxis: { type: 'string', description: 'X-axis label' },
            yAxis: { type: 'string', description: 'Y-axis label' }
          },
          required: ['title', 'type', 'data']
        }
      },
      
      createFlashcards: {
        description: 'Create interactive flashcards for learning',
        parameters: {
          type: 'object' as const,
          properties: {
            title: { type: 'string', description: 'Flashcard set title' },
            cards: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  front: { type: 'string' },
                  back: { type: 'string' },
                  category: { type: 'string' }
                },
                required: ['front', 'back']
              },
              description: 'Array of flashcard objects with front and back text'
            }
          },
          required: ['title', 'cards']
        }
      },

      // 🎨 IMAGE GENERATION TOOLS
      generateImage: {
        description: 'Generate an image using AI (DALL-E 3 for OpenAI, Aurora for Grok). Use when users request images or when images would enhance understanding of concepts.',
        parameters: {
          type: 'object' as const,
          properties: {
            prompt: { 
              type: 'string', 
              description: 'Detailed description of the image to generate. Be specific about style, composition, colors, and subject matter.' 
            },
            size: { 
              type: 'string', 
              enum: ['1024x1024', '1024x1792', '1792x1024'], 
              description: 'Image dimensions',
              default: '1024x1024'
            },
            quality: { 
              type: 'string', 
              enum: ['standard', 'hd'], 
              description: 'Image quality level',
              default: 'standard'
            },
            style: {
              type: 'string',
              enum: ['natural', 'vivid'],
              description: 'Image style preference',
              default: 'vivid'
            }
          },
          required: ['prompt']
        }
      },

      createDiagram: {
        description: 'Generate a visual diagram or infographic to explain concepts, processes, or relationships. Use when complex information needs visual representation.',
        parameters: {
          type: 'object' as const,
          properties: {
            prompt: { 
              type: 'string', 
              description: 'Description of the diagram to create (e.g., "network topology diagram showing router connections", "flowchart of user authentication process")' 
            },
            type: { 
              type: 'string', 
              enum: ['flowchart', 'network-diagram', 'process-diagram', 'infographic', 'architectural-diagram', 'concept-map'], 
              description: 'Type of diagram to create' 
            },
            style: {
              type: 'string',
              enum: ['technical', 'educational', 'professional', 'colorful'],
              description: 'Visual style of the diagram',
              default: 'educational'
            }
          },
          required: ['prompt', 'type']
        }
      },

      // 🎵 AUDIO GENERATION TOOLS  
      generateAudio: {
        description: 'Generate speech audio from text using AI text-to-speech. Use when users request audio, voice narration, or when audio would enhance the experience.',
        parameters: {
          type: 'object' as const,
          properties: {
            text: { 
              type: 'string', 
              description: 'The text to convert to speech. Should be clear and well-formatted for natural speech synthesis.' 
            },
            voice: { 
              type: 'string', 
              enum: ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'], 
              description: 'Voice style for the generated audio',
              default: 'alloy'
            },
            model: {
              type: 'string',
              enum: ['tts-1', 'tts-1-hd'],
              description: 'TTS model quality (tts-1 for speed, tts-1-hd for quality)',
              default: 'tts-1'
            },
            speed: {
              type: 'number',
              minimum: 0.25,
              maximum: 4.0,
              description: 'Speech speed multiplier (0.25 to 4.0)',
              default: 1.0
            }
          },
          required: ['text']
        }
      },

      // 🎤 SPEECH-TO-TEXT TOOLS
      speechToText: {
        description: 'Transcribe audio to text using AI speech recognition. Use when users provide audio files or recordings that need to be converted to text.',
        parameters: {
          type: 'object' as const,
          properties: {
            audio_data: { 
              type: 'string', 
              description: 'Base64 encoded audio data to transcribe' 
            },
            audio_file: { 
              type: 'string', 
              description: 'Path to audio file to transcribe (alternative to audio_data)' 
            },
            language: { 
              type: 'string', 
              description: 'Language of the audio (auto-detect if not specified)',
              default: 'auto'
            },
            model: { 
              type: 'string', 
              enum: ['whisper-1'], 
              description: 'Speech recognition model to use',
              default: 'whisper-1'
            }
          },
          required: []
        }
      },
      
      transcribeAudio: {
        description: 'Alternative name for speech-to-text tool',
        parameters: {
          type: 'object' as const,
          properties: {
            audio_data: { 
              type: 'string', 
              description: 'Base64 encoded audio data to transcribe' 
            },
            audio_file: { 
              type: 'string', 
              description: 'Path to audio file to transcribe' 
            },
            language: { 
              type: 'string', 
              description: 'Language of the audio',
              default: 'auto'
            }
          },
          required: []
        }
      },

      // 📄 FILE PROCESSING TOOLS
      processFile: {
        description: 'Process, analyze, or summarize file content. Use when users upload files or need content analysis.',
        parameters: {
          type: 'object' as const,
          properties: {
            file_content: { 
              type: 'string', 
              description: 'The content of the file to process' 
            },
            file_type: { 
              type: 'string', 
              description: 'Type of file being processed (text, pdf, docx, etc.)',
              default: 'text'
            },
            task: { 
              type: 'string', 
              enum: ['summarize', 'analyze', 'extract'], 
              description: 'Processing task to perform',
              default: 'summarize'
            }
          },
          required: ['file_content']
        }
      },
      
      analyzeFile: {
        description: 'Analyze file content in detail, providing insights and observations',
        parameters: {
          type: 'object' as const,
          properties: {
            file_content: { 
              type: 'string', 
              description: 'The content of the file to analyze' 
            },
            file_type: { 
              type: 'string', 
              description: 'Type of file being analyzed',
              default: 'text'
            }
          },
          required: ['file_content']
        }
      },
      
      summarizeFile: {
        description: 'Summarize file content, highlighting key points and main ideas',
        parameters: {
          type: 'object' as const,
          properties: {
            file_content: { 
              type: 'string', 
              description: 'The content of the file to summarize' 
            },
            file_type: { 
              type: 'string', 
              description: 'Type of file being summarized',
              default: 'text'
            }
          },
          required: ['file_content']
        }
      }
    }

    // Convert to the format expected by the backend
    return Object.keys(toolDefinitions).map(name => {
      const tool = toolDefinitions[name as keyof typeof toolDefinitions] as ToolDefinition
      return {
        name,
        description: tool.description,
        parameters: tool.parameters
      }
    })
  }

  // Initialize chat system (no longer using AI SDK Chat class)
  const initializeChat = async () => {
    if (import.meta.client && !isInitialized.value) {
      try {
        await import('ai')
        
        // Initialize tools on client side - use the same definitions as getAvailableTools
        const toolDefs = getAvailableTools()
        interactiveTools.value = {}
        toolDefs.forEach(tool => {
          if (interactiveTools.value) {
            interactiveTools.value[tool.name] = {
              description: tool.description,
              parameters: tool.parameters
            }
          }
        })
        
        // Direct streaming approach - no Chat class needed
        
        isInitialized.value = true
        
      } catch (error) {
        console.error('Failed to initialize Chat:', error)
        chatError.value = 'Failed to initialize chat system'
      }
    }
  }

  // Enhanced message processing
  const enhancedMessages = computed(() => {
    if (!messages.value || !Array.isArray(messages.value)) {
      return []
    }
    return messages.value.map((message: ChatMessage) => {
      const hasReasoning = message.parts?.some(part => part.type === 'reasoning')
      const hasTools = message.parts?.some(part => part.type?.startsWith('tool-'))
      const hasFiles = message.parts?.some(part => part.type === 'file')
      
      return {
        ...message,
        hasReasoning,
        hasTools,
        hasFiles,
        reasoning: message.parts?.filter(part => part.type === 'reasoning') || [],
        tools: message.parts?.filter(part => part.type?.startsWith('tool-')) || [],
        files: message.parts?.filter(part => part.type === 'file') || []
      }
    })
  })

  // Provider management
  const changeProvider = (newProvider: string) => {
    selectedProvider.value = newProvider
    const provider = providers.find(p => p.id === newProvider)
    if (provider && provider.models.length > 0) {
      selectedModel.value = provider.models[0] || ''
    }
  }

  const changeModel = (newModel: string) => {
    selectedModel.value = newModel
  }

  // File upload handling
  const handleFileUpload = async (files: FileList): Promise<FileUIPart[]> => {
    try {
      if (import.meta.client) {
        const { convertFileListToFileUIParts } = await import('ai')
        const fileUIParts = await convertFileListToFileUIParts(files)
        uploadedFiles.value = [...uploadedFiles.value, ...fileUIParts]
        return fileUIParts
      }
      return []
    } catch (error: unknown) {
      console.error('File upload error:', error)
      chatError.value = `File upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      return []
    }
  }

  const removeFile = (index: number) => {
    uploadedFiles.value.splice(index, 1)
  }

  const clearFiles = () => {
    uploadedFiles.value = []
  }

  // Enhanced message sending
  const sendMessage = async (content: string, options: ChatOptions = {}) => {
    if (!isInitialized.value) {
      console.warn('Chat not initialized yet')
      return
    }
    
    try {
      chatError.value = null
      isLoading.value = true
      isThinking.value = true
      
      // Add user message immediately
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: content,
        parts: [{ type: 'text', text: content }],
        createdAt: new Date().toISOString()
      }
      messages.value.push(userMessage)
      
      // Prepare assistant message
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        parts: [{ type: 'text', text: '' }],
        createdAt: new Date().toISOString()
      }
      messages.value.push(assistantMessage)
      
      // Process files if provided
      let filesToSend = uploadedFiles.value
      if (options.files) {
        const newFiles = await handleFileUpload(options.files)
        filesToSend = [...filesToSend, ...newFiles]
      }

      const toolsToSend = getAvailableTools()

      // Direct backend connection for faster response (bypass Nuxt proxy)
      const apiUrl = import.meta.client ? 'http://localhost:8000/api/chat' : '/api/chat'
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messages.value.slice(0, -1).map((msg: ChatMessage) => ({
            role: msg.role,
            content: msg.content,
            parts: msg.parts
          })),
          data: {
            provider: selectedProvider.value
          },
          model: selectedModel.value,
          enableReasoning: options.enableReasoning ?? true,
          files: filesToSend,
          tools: toolsToSend
        })
      })

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`)
      }

      // Process streaming response
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      
      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          const chunk = decoder.decode(value, { stream: true })
          const lines = chunk.split('\n')
          
          for (const line of lines) {
            if (line.trim().startsWith('data: ')) {
              const data = line.trim().slice(6)
              
              if (data === '[DONE]') {
                continue
              }
              
              try {
                const parsed = JSON.parse(data)
                
                const lastMessage = messages.value[messages.value.length - 1]
                
                // Handle Enhanced Multimodal Response Format
                if (parsed.type === 'reasoning') {
                  // Enhanced reasoning with multimodal content
                  isThinking.value = true
                  currentThought.value = parsed.content || ''
                  
                  if (lastMessage && lastMessage.role === 'assistant') {
                    if (!lastMessage.parts) lastMessage.parts = []
                    let reasoningPart = lastMessage.parts.find(part => part.type === 'reasoning')
                    if (!reasoningPart) {
                      reasoningPart = { 
                        type: 'reasoning', 
                        text: '', 
                        state: 'streaming',
                        multimodal_content: [],
                        content_type: 'reasoning'
                      }
                      lastMessage.parts.push(reasoningPart)
                    }
                    reasoningPart.text += parsed.content || ''
                    reasoningPart.multimodal_content = parsed.multimodal_content || []
                  }
                } else if (parsed.type === 'thinking') {
                  // AI thinking/planning phase
                  isThinking.value = true
                  currentThought.value = parsed.content || ''
                  
                  if (lastMessage && lastMessage.role === 'assistant') {
                    if (!lastMessage.parts) lastMessage.parts = []
                    let reasoningPart = lastMessage.parts.find(part => part.type === 'reasoning')
                    if (!reasoningPart) {
                      reasoningPart = { 
                        type: 'reasoning', 
                        text: '', 
                        state: 'streaming',
                        multimodal_content: [],
                        content_type: 'reasoning'
                      }
                      lastMessage.parts.push(reasoningPart)
                    }
                    reasoningPart.text += parsed.content || ''
                    reasoningPart.multimodal_content = parsed.multimodal_content || []
                  }
                } else if (parsed.type === 'tool_loading') {
                  // Tool preparation phase
                  isThinking.value = true
                  currentThought.value = parsed.content || 'Preparing tools...'
                } else if (parsed.type === 'tool_executing') {
                  // Tool execution with loading animation
                  isThinking.value = true
                  currentThought.value = parsed.content || 'Executing tool...'
                } else if (parsed.type === 'content' || parsed.type === 'text-delta') {
                  // Enhanced content with multimodal support
                  
                  if (lastMessage && lastMessage.role === 'assistant') {
                    // Only add content if it's not already included (avoid duplication)
                    const newContent = parsed.content || parsed.delta || ''
                    if (newContent && !lastMessage.content.includes(newContent)) {
                      lastMessage.content += newContent
                    }
                    
                    // Handle multimodal content parts
                    if (!lastMessage.parts) lastMessage.parts = []
                    
                    // Skip multimodal processing for simple text to avoid duplication
                    // The main content is already being added above
                    
                    // Also maintain a main text part for legacy support
                    let mainTextPart = lastMessage.parts.find(part => part.type === 'text' && !part.format)
                    if (!mainTextPart) {
                      mainTextPart = { type: 'text', text: '', state: 'streaming' }
                      lastMessage.parts.unshift(mainTextPart) // Add at beginning for priority
                    }
                    mainTextPart.text = lastMessage.content
                    
                    nextTick(() => scrollToBottom())
                  }
                } 
                // Handle legacy content format (direct from backend) - avoid duplication
                else if (parsed.content && !parsed.type && parsed.content.trim()) {
                  if (lastMessage && lastMessage.role === 'assistant') {
                    // Only add if it's not already in the message content
                    if (!lastMessage.content.includes(parsed.content)) {
                      lastMessage.content += parsed.content || ''
                      
                      // Ensure we have a text part
                      if (!lastMessage.parts) lastMessage.parts = []
                      let mainTextPart = lastMessage.parts.find(part => part.type === 'text')
                      if (!mainTextPart) {
                        mainTextPart = { type: 'text', text: '', state: 'streaming' }
                        lastMessage.parts.push(mainTextPart)
                      }
                      mainTextPart.text = lastMessage.content
                      
                      nextTick(() => scrollToBottom())
                    }
                  }
                } else if (parsed.type === 'tool_call') {
                  // Enhanced tool call with multimodal support
                  
                  if (lastMessage && lastMessage.role === 'assistant') {
                    if (!lastMessage.parts) lastMessage.parts = []
                    
                    const toolPart = {
                      type: 'tool-call' as const,
                      toolName: parsed.tool_call?.name || 'unknown',
                      toolId: parsed.tool_call?.id || '',
                      input: parsed.tool_call?.arguments ? JSON.parse(parsed.tool_call.arguments || '{}') : {},
                      state: 'input-streaming' as const, // Start as streaming
                      multimodal_content: parsed.multimodal_content || [],
                      content_type: parsed.content_type
                    }
                    
                    lastMessage.parts.push(toolPart)
                  }
                } else if (parsed.type === 'tool_result') {
                  // Handle tool execution results

                  
                  if (lastMessage && lastMessage.role === 'assistant' && lastMessage.parts) {
                    // Find the corresponding tool call part
                    const toolCallPart = lastMessage.parts.find(part => 
                      part.type === 'tool-call' && part.toolId === parsed.tool_result?.id
                    )
                    

                    
                    if (toolCallPart) {

                      // Update the tool call with results
                      toolCallPart.state = 'output-available' as const
                      toolCallPart.output = parsed.tool_result?.result
                      
                    } else {
                      console.warn('❌ No matching tool call found for result ID:', parsed.tool_result?.id)
                    }
                  }
                } else if (parsed.type === 'tool_error') {
                  // Handle tool execution errors
                  
                  if (lastMessage && lastMessage.role === 'assistant' && lastMessage.parts) {
                    // Find the corresponding tool call part
                    const toolCallPart = lastMessage.parts.find(part => 
                      part.type === 'tool-call' && part.toolId === parsed.tool_error?.id
                    )
                    
                    if (toolCallPart) {
                      // Update the tool call with error
                      toolCallPart.state = 'output-error' as const
                      toolCallPart.errorText = parsed.tool_error?.error
                      
                    }
                  }
                } else if (parsed.type === 'image_generation') {
                  // Handle image generation results
                  
                  if (lastMessage && lastMessage.role === 'assistant') {
                    if (!lastMessage.parts) lastMessage.parts = []
                    
                    const imagePart = {
                      type: 'image' as const,
                      url: parsed.multimodal_content?.[0]?.url || parsed.multimodal_content?.[0]?.data,
                      metadata: parsed.multimodal_content?.[0]?.metadata,
                      format: parsed.multimodal_content?.[0]?.format || 'png',
                      state: 'done' as const
                    }
                    
                    lastMessage.parts.push(imagePart)
                  }
                } else if (parsed.type === 'error') {
                  throw new Error(parsed.error || 'Unknown error')
                } else {
                  // Handle legacy AI SDK 5 format for backward compatibility
                  if (parsed.type === 'reasoning-start') {
                    isThinking.value = true
                    currentThought.value = ''
                  } else if (parsed.type === 'reasoning-delta') {
                    currentThought.value += parsed.delta || ''
                    isThinking.value = true
                  } else if (parsed.type === 'reasoning-end') {
                    isThinking.value = false
                  } else if (parsed.type === 'text-delta') {
                    if (lastMessage && lastMessage.role === 'assistant') {
                      lastMessage.content += parsed.delta || ''
                      if (!lastMessage.parts) lastMessage.parts = []
                      let textPart = lastMessage.parts.find(part => part.type === 'text')
                      if (!textPart) {
                        textPart = { type: 'text', text: '', state: 'streaming' }
                        lastMessage.parts.push(textPart)
                      }
                      textPart.text = lastMessage.content
                      nextTick(() => scrollToBottom())
                    }
                  } else if (parsed.type === 'finish' || data === '[DONE]') {
                    isLoading.value = false
                    isThinking.value = false
                    // Mark all streaming parts as done
                    if (lastMessage && lastMessage.parts) {
                      lastMessage.parts.forEach(part => {
                        if (part.state === 'streaming') {
                          part.state = 'done'
                        }
                      })
                    }
                  } else if (parsed.content !== undefined) {
                    // Very legacy format
                    if (lastMessage && lastMessage.role === 'assistant') {
                      lastMessage.content += parsed.content
                      if (lastMessage.parts && lastMessage.parts[0]) {
                        lastMessage.parts[0].text = lastMessage.content
                      }
                      nextTick(() => scrollToBottom())
                    }
                  }
                }
              } catch (parseError) {
                console.warn('❌ Parse error for line:', line, parseError)
              }
            }
          }
        }
      }

      // Clear uploaded files after sending
      clearFiles()
      isLoading.value = false
      isThinking.value = false
      
      // Mark all parts as done when stream ends
      const lastMessage = messages.value[messages.value.length - 1]
      if (lastMessage && lastMessage.role === 'assistant' && lastMessage.parts) {
        lastMessage.parts.forEach(part => {
          if (part.state === 'streaming') {
            part.state = 'done'
          }
        })
      }
      
      // Final scroll to bottom
      nextTick(() => scrollToBottom())
      
    } catch (error: unknown) {
      console.error('Send message error:', error)
      chatError.value = error instanceof Error ? error.message : 'Unknown error occurred'
      isLoading.value = false
      isThinking.value = false
    }
  }

  // Enhanced regeneration
  const regenerateMessage = async () => {
    // Note: Direct fetch approach doesn't use chat.value.regenerate
    // Implementation would go here if needed
  }

  // Chat management
  const clearChat = () => {
    messages.value = []
    clearFiles()
    chatError.value = null
    currentThought.value = ''
    isThinking.value = false
    isLoading.value = false
  }

  const stopGeneration = async () => {
    try {
      isLoading.value = false
      isThinking.value = false
      // Note: Direct fetch doesn't support stop, but we can set loading states
    } catch (error) {
      console.error('Stop generation error:', error)
    }
  }

  // Export functionality
  const exportChat = () => {
    const exportData = {
      timestamp: new Date().toISOString(),
      provider: selectedProvider.value,
      model: selectedModel.value,
      messages: (messages.value || []).map((msg: ChatMessage) => ({
        role: msg?.role || 'user',
        content: msg.parts?.filter(part => part && part.type === 'text').map(part => part.text || '').join('') || msg?.content || '',
        reasoning: msg.parts?.filter(part => part && part.type === 'reasoning').map(part => part.text || '').join('') || '',
        timestamp: msg?.createdAt || new Date().toISOString()
      }))
    }
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `digi-setu-chat-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Utility functions
  const scrollToBottom = () => {
    setTimeout(() => {
      const container = document.querySelector('[data-messages-container]')
      if (container) {
        container.scrollTo({
          top: container.scrollHeight,
          behavior: 'smooth'
        })
      }
    }, 100)
  }

  // Clear error function
  const clearError = () => {
    chatError.value = null
    isLoading.value = false
    isThinking.value = false
  }

  // Initialize on mount (client-side only)
  onMounted(() => {
    initializeChat()
  })

  return {
    // Chat instance and state
    chat: computed(() => null), // No longer using Chat class
    isInitialized,
    
    // Enhanced messages
    messages: enhancedMessages,
    
    // State
    isLoading,
    status: computed(() => isLoading.value ? 'streaming' : 'ready'),
    error: chatError,
    isThinking,
    currentThought,
    input,
    
    // Provider management
    selectedProvider,
    selectedModel,
    providers,
    changeProvider,
    changeModel,
    
    // File management
    uploadedFiles,
    handleFileUpload,
    removeFile,
    clearFiles,
    
    // Message operations
    sendMessage,
    regenerateMessage,
    
    // Chat controls
    clearChat,
    stopGeneration,
    exportChat,
    
    // Tools
    interactiveTools: computed(() => interactiveTools?.value || null),
    
    // Utilities
    scrollToBottom,
    initializeChat,
    clearError
  }
}

// Helper functions for message processing
export const extractTextFromMessage = (message: ChatMessage | null): string => {
  if (!message) return ''
  if (!message.parts && message.content) return message.content
  if (!message.parts || !Array.isArray(message.parts)) return ''
  
  return message.parts
    .filter(part => part && part.type === 'text')
    .map(part => part.text || '')
    .join('')
}

export const extractReasoningFromMessage = (message: ChatMessage | null): string => {
  if (!message || !message.parts || !Array.isArray(message.parts)) return ''
  
  return message.parts
    .filter(part => part && part.type === 'reasoning')
    .map(part => part.text || '')
    .join('')
}

export const getToolCallsFromMessage = (message: ChatMessage | null): unknown[] => {
  if (!message || !message.parts || !Array.isArray(message.parts)) return []
  
  return message.parts.filter(part => 
    part && part.type?.startsWith('tool-')
  )
}
