import type { Message } from '~/types'
import { mockMarkdownContent } from '~/utils/mockMarkdownContent'

export const useChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const isStreaming = ref(false)

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading.value || isStreaming.value) return

    // Add user message
    const userMessage: Message = {
      id: Date.now() + Math.random(),
      content: content.trim(),
      role: 'user',
      timestamp: new Date()
    }
    messages.value.push(userMessage)

    // Start loading assistant response
    isLoading.value = true
    
    const assistantMessage: Message = {
      id: Date.now() + Math.random() + 1,
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      isLoading: true,
      isStreaming: false,
      components: []
    }
    messages.value.push(assistantMessage)

    try {
      // Simulate response delay
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // Update message to start streaming
      const index = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (index !== -1) {
        messages.value[index] = {
          ...assistantMessage,
          isLoading: false,
          isStreaming: true
        }
      }

      // Determine response content based on input
      let responseContent = ''
      const lowerContent = content.toLowerCase()
      
      if (lowerContent.includes('hi') || lowerContent.includes('hello')) {
        responseContent = mockMarkdownContent
      } else if (lowerContent.includes('test') || lowerContent.includes('demo')) {
        responseContent = `# Test Response 🧪

Here's a **comprehensive test** of our chat functionality:

## Features Working:
- ✅ **Markdown rendering** with full syntax support
- ✅ **Code highlighting** for multiple languages
- ✅ **Tables** and **lists** 
- ✅ **Links** and **formatting**

### Code Example:
\`\`\`javascript
function greet(name) {
  console.log(\`Hello, \${name}!\`);
  return \`Welcome to Digi Setu AI!\`;
}

greet('Developer');
\`\`\`

### Data Table:
| Component | Status | Notes |
|-----------|--------|-------|
| Chat UI | ✅ Working | Full functionality |
| Markdown | ✅ Working | All features enabled |
| Streaming | ✅ Working | Real-time updates |

> **Success!** All systems are working perfectly! 🎉`
      } else if (lowerContent.includes('table')) {
        responseContent = `# Data Tables 📊

Here are some examples of different table formats:

## Simple Table:
| Name | Role | Experience |
|------|------|------------|
| Alice | Developer | 5 years |
| Bob | Designer | 3 years |
| Carol | Manager | 8 years |

## Aligned Table:
| Left Align | Center Align | Right Align |
|:-----------|:------------:|------------:|
| Apple      | Banana       | Cherry      |
| Dog        | Elephant     | Fox         |
| 123        | 456          | 789         |

## Feature Comparison:
| Feature | Basic Plan | Pro Plan | Enterprise |
|---------|------------|----------|------------|
| **Users** | 5 | 50 | Unlimited |
| **Storage** | 1GB | 100GB | 1TB |
| **Support** | Email | Priority | 24/7 Phone |
| **Price** | $9/mo | $29/mo | $99/mo |

Perfect for displaying structured data! 📋`
      } else if (lowerContent.includes('code')) {
        responseContent = `# Code Examples 💻

Here are various programming language examples:

## JavaScript/TypeScript:
\`\`\`typescript
interface User {
  id: number;
  name: string;
  email: string;
}

class UserService {
  private users: User[] = [];
  
  addUser(user: User): void {
    this.users.push(user);
  }
  
  findUser(id: number): User | undefined {
    return this.users.find(u => u.id === id);
  }
}
\`\`\`

## Python:
\`\`\`python
def fibonacci(n):
    """Generate Fibonacci sequence"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# List comprehension example
squares = [x**2 for x in range(10)]
print(squares)
\`\`\`

## CSS:
\`\`\`css
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-primary);
}

.message {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
\`\`\`

All with **syntax highlighting**! ✨`
      } else {
        responseContent = `# Response to: "${content}"

Thank you for your message! Here's what I can help you with:

## Available Commands:
- **"hi"** or **"hello"** - Show comprehensive markdown demo
- **"test"** or **"demo"** - Display feature testing examples  
- **"table"** - Show various table formats
- **"code"** - Display code examples with syntax highlighting

## General Capabilities:
- ✅ **Markdown rendering** with full syntax support
- ✅ **Code highlighting** for 100+ languages
- ✅ **Tables**, **lists**, and **formatting**
- ✅ **Math equations** (LaTeX/KaTeX support)
- ✅ **Custom containers** for info, warnings, tips
- ✅ **Task lists** with checkboxes
- ✅ **Links** and **images**

### Quick Example:
\`\`\`javascript
console.log('Hello from Digi Setu AI! 🚀');
\`\`\`

> **Tip**: Try asking about specific topics or use the commands above to see different features in action!

What would you like to explore next? 🤔`
      }

      // Simulate streaming by updating content gradually
      await simulateStreaming(assistantMessage.id, responseContent)

    } catch (error) {
      console.error('Chat error:', error)
      
      const index = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (index !== -1) {
        messages.value[index] = {
          ...assistantMessage,
          content: 'Sorry, I encountered an error. Please try again.',
          isLoading: false,
          isStreaming: false,
          error: error instanceof Error ? error.message : String(error)
        }
      }
    } finally {
      isLoading.value = false
      isStreaming.value = false
    }
  }

  const simulateStreaming = async (messageId: string | number, content: string) => {
    const index = messages.value.findIndex(m => m.id === messageId)
    if (index === -1) return

    isStreaming.value = true
    
    // Stream content character by character for more realistic effect
    let currentContent = ''
    const chars = content.split('')
    
    for (let i = 0; i < chars.length; i++) {
      currentContent += chars[i]
      
      // Update message content
      const currentMessage = messages.value[index]
      if (currentMessage) {
        messages.value[index] = {
          ...currentMessage,
          content: currentContent,
          isStreaming: true
        }
      }
      
      // Variable delay for more natural streaming
      let delay = 15 // Base delay for characters
      if (chars[i] === ' ') delay = 25 // Slightly longer for spaces
      if (chars[i] === '.' || chars[i] === '!' || chars[i] === '?') delay = 100 // Pause at sentence endings
      if (chars[i] === '\n') delay = 50 // Pause at line breaks
      
      await new Promise(resolve => setTimeout(resolve, delay))
    }
    
    // Mark streaming as complete
    const finalMessage = messages.value[index]
    if (finalMessage) {
      messages.value[index] = {
        ...finalMessage,
        isStreaming: false
      }
    }
    
    isStreaming.value = false
  }

  const clearMessages = () => {
    messages.value = []
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
    await sendMessage(userMessage.content)
  }

  return {
    messages: readonly(messages),
    isLoading: readonly(isLoading),
    isStreaming: readonly(isStreaming),
    sendMessage,
    clearMessages,
    regenerateMessage
  }
}
