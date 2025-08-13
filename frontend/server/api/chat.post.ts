// server/api/chat.post.ts
// AI SDK 5 compatible route - proxy to Python FastAPI backend

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    console.log('🔄 AI SDK 5 request to Python backend:', body)
    
    // AI SDK 5 sends messages in different format
    const messages = body.messages || []
    const provider = body.data?.provider || body.provider || 'openai'
    
    console.log('📨 Messages count:', messages.length)
    console.log('🔧 Provider:', provider)
    
    // Convert AI SDK 5 messages to Python backend format
    const convertedMessages = messages.map(msg => ({
      role: msg.role,
      content: msg.parts ? 
        msg.parts.filter(part => part.type === 'text').map(part => part.text).join('') :
        msg.content || ''
    }))
    
    // Forward to Python backend
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: convertedMessages,
        provider: provider,
        model: body.model
      })
    })

    if (!response.ok) {
      throw new Error(`Python backend error: ${response.status} ${response.statusText}`)
    }

    // Set proper headers for AI SDK 5 streaming
    setHeader(event, 'Content-Type', 'text/plain; charset=utf-8')
    setHeader(event, 'Cache-Control', 'no-cache')
    setHeader(event, 'Connection', 'keep-alive')
    setHeader(event, 'Access-Control-Allow-Origin', '*')
    
    // Convert Python backend streaming to AI SDK 5 format
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    
    if (!reader) {
      throw new Error('No response body from Python backend')
    }
    
    // Create a readable stream that converts Python format to AI SDK 5 format
    const stream = new ReadableStream({
      async start(controller) {
        try {
          let messageId = `msg-${Date.now()}`
          let hasStarted = false
          
          while (true) {
            const { done, value } = await reader.read()
            
            if (done) {
              // Send finish chunk
              if (hasStarted) {
                controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                  type: 'text-end',
                  id: messageId
                })}\n\n`))
                
                controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                  type: 'finish'
                })}\n\n`))
              }
              break
            }
            
            const chunk = decoder.decode(value, { stream: true })
            const lines = chunk.split('\n')
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6).trim()
                
                if (data === '[DONE]') {
                  continue
                }
                
                try {
                  const parsed = JSON.parse(data)
                  
                  if (parsed.content) {
                    // Send start chunk if this is the first content
                    if (!hasStarted) {
                      controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                        type: 'text-start',
                        id: messageId
                      })}\n\n`))
                      hasStarted = true
                    }
                    
                    // Send text delta chunk
                    controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({
                      type: 'text-delta',
                      id: messageId,
                      delta: parsed.content
                    })}\n\n`))
                  } else if (parsed.error) {
                    // Send error chunk
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
          console.error('Stream conversion error:', error)
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
    console.error('❌ AI SDK 5 Proxy error:', error)
    
    // Return error in AI SDK 5 compatible format
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
