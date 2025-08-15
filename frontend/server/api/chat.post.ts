// server/api/chat.post.ts
// Enhanced AI SDK 5 route with reasoning, tool calling, and file support

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    console.log('🚀 AI SDK 5 Enhanced Request:', {
      messagesCount: body.messages?.length || 0,
      provider: body.data?.provider || body.provider,
      hasFiles: body.files?.length > 0,
      hasTools: body.tools?.length > 0
    })
    
    // Extract AI SDK 5 data
    const messages = body.messages || []
    const provider = body.data?.provider || body.provider || 'openai'
    const model = body.model
    const files = body.files || []
    const tools = body.tools || []
    
    // Convert AI SDK 5 messages to Python backend format
    const convertedMessages = messages.map(msg => {
      if (msg.parts) {
        // Handle AI SDK 5 message parts
        const textParts = msg.parts?.filter(part => part.type === 'text') || []
        const reasoningParts = msg.parts?.filter(part => part.type === 'reasoning') || []
        const fileParts = msg.parts?.filter(part => part.type === 'file') || []
        
        return {
          role: msg.role,
          content: textParts.map(part => part.text).join(''),
          reasoning: reasoningParts.map(part => part.text).join(''),
          files: fileParts.map(part => ({
            url: part.url,
            mediaType: part.mediaType,
            filename: part.filename
          }))
        }
      } else {
        return {
          role: msg.role,
          content: msg.content || '',
          reasoning: '',
          files: []
        }
      }
    })
    
    // Enhanced request to Python backend
    const pythonRequest = {
      messages: convertedMessages,
      provider: provider,
      model: model,
      files: files,
      tools: tools,
      enableReasoning: true,  // Enable reasoning/thinking process
      enableToolCalling: tools.length > 0,
      streamMode: 'enhanced'  // Request enhanced streaming
    }
    
    // Forward to Python backend
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(pythonRequest)
    })

    if (!response.ok) {
      throw new Error(`Python backend error: ${response.status} ${response.statusText}`)
    }

    // Set AI SDK 5 streaming headers
    setHeader(event, 'Content-Type', 'text/plain; charset=utf-8')
    setHeader(event, 'Cache-Control', 'no-cache')
    setHeader(event, 'Connection', 'keep-alive')
    setHeader(event, 'Access-Control-Allow-Origin', '*')
    
    // Enhanced Python to AI SDK 5 stream conversion
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    
    if (!reader) {
      throw new Error('No response body from Python backend')
    }
    
    // AI SDK 5 Enhanced Stream with reasoning and tool support
    const stream = new ReadableStream({
      async start(controller) {
        try {
          let messageId = `msg-${Date.now()}`
          let hasTextStarted = false
          let hasReasoningStarted = false
          let currentToolCall = null
          
          while (true) {
            const { done, value } = await reader.read()
            
            if (done) {
              // Send proper finish chunks
              if (hasTextStarted) {
                controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                  type: 'text-end',
                  id: messageId
                })}\n\n`))
              }
              
              if (hasReasoningStarted) {
                controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                  type: 'reasoning-end',
                  id: messageId
                })}\n\n`))
              }
              
              controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                type: 'finish'
              })}\n\n`))
              break
            }
            
            const chunk = decoder.decode(value, { stream: true })
            const lines = chunk.split('\n')
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6).trim()
                
                if (data === '[DONE]') continue
                
                try {
                  const parsed = JSON.parse(data)
                  
                  // Handle reasoning/thinking content
                  if (parsed.reasoning) {
                    if (!hasReasoningStarted) {
                      controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                        type: 'reasoning-start',
                        id: messageId
                      })}\n\n`))
                      hasReasoningStarted = true
                    }
                    
                    controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                      type: 'reasoning-delta',
                      id: messageId,
                      delta: parsed.reasoning
                    })}\n\n`))
                  }
                  
                  // Handle regular content
                  if (parsed.content) {
                    if (!hasTextStarted) {
                      controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                        type: 'text-start',
                        id: messageId
                      })}\n\n`))
                      hasTextStarted = true
                    }
                    
                    controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                      type: 'text-delta',
                      id: messageId,
                      delta: parsed.content
                    })}\n\n`))
                  }
                  
                  // Handle tool calls - pass through the backend format directly
                  if (parsed.type === 'tool_call' && parsed.tool_call) {
                    // Pass through the tool call data as-is since the composable handles it
                    controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify(parsed)}\n\n`))
                  }
                  
                  // Handle tool results - pass through the backend format directly  
                  if (parsed.type === 'tool_result' && parsed.tool_result) {
                    // Pass through the tool result data as-is since the composable handles it
                    controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify(parsed)}\n\n`))
                  }
                  
                  // Handle tool errors - pass through the backend format directly
                  if (parsed.type === 'tool_error' && parsed.tool_error) {
                    // Pass through the tool error data as-is since the composable handles it
                    controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify(parsed)}\n\n`))
                  }
                  
                  // Handle errors
                  if (parsed.error) {
                    controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                      type: 'error',
                      errorText: parsed.error
                    })}\n\n`))
                    break
                  }
                  
                } catch (parseError) {
                  console.warn('Failed to parse chunk:', data)
                  continue
                }
              }
            }
          }
        } catch (error) {
          console.error('Enhanced stream conversion error:', error)
          controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
            type: 'error',
            errorText: error.message
          })}\n\n`))
        } finally {
          controller.close()
        }
      }
    })
    
    return new Response(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
      }
    })
    
  } catch (error) {
    console.error('❌ AI SDK 5 Enhanced Proxy error:', error)
    
    return new Response(
      `data: ${JSON.stringify({ type: 'error', errorText: error.message })}\n\n`,
      {
        status: 500,
        headers: {
          'Content-Type': 'text/plain; charset=utf-8'
        }
      }
    )
  }
})
