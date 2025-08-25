// Comprehensive mock markdown content for testing all features
export const mockMarkdownContent = `# 🚀 Complete AI Chat Markdown Demo

This demonstrates **all** markdown features working together in your digi-setu chat interface, including advanced AI-specific features!

## 🧮 Math & LaTeX Support

Inline math: $E = mc^2$ and $\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$

Block equations:
$$
\\mathcal{L}\\{f(t)\\} = F(s) = \\int_0^\\infty f(t)e^{-st} dt
$$

$$
\\frac{\\partial^2 u}{\\partial t^2} = c^2 \\nabla^2 u
$$

$$
\\nabla^2 u = \\frac{\\partial^2 u}{\\partial x^2} + \\frac{\\partial^2 u}{\\partial y^2} + \\frac{\\partial^2 u}{\\partial z^2}
$$

Advanced equations:
$$
\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}
$$

$$
\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1
$$

Complex analysis:
$$
\\oint_C f(z) dz = 2\\pi i \\sum \\text{Res}(f, z_k)
$$

Statistics:
$$
P(X = k) = \\binom{n}{k} p^k (1-p)^{n-k}
$$

## 📦 AI Response Containers

::: info
💡 **AI Insight**: This is helpful information that AI commonly provides to users.
:::

::: warning
⚠️ **Important**: This code might have security implications. Always validate user input!
:::

::: tip
✨ **Pro Tip**: Use containers to highlight important information in AI responses.
:::

::: danger
🚨 **Critical**: Never store passwords in plain text! Always use proper hashing.
:::

## 🎨 Enhanced Text Formatting

Here's ==highlighted text== that stands out, and ++inserted text++ that shows additions.

Chemical formulas work great: H~2~O, CO~2~, and mathematical expressions: x^2^ + y^2^ = z^2^

## 😀 Emoji Support

AI responses are more engaging with emojis: 🚀 ❤️ 🔥 💯 🎉 👍 🧠 🤖

Note: Direct emoji characters work perfectly! (Emoji shortcode plugin temporarily disabled due to import issues)

## Text Formatting

Here's some *italic text*, **bold text**, and ***bold italic text***.
You can also use ~~strikethrough~~ and \`inline code\`.

## Code Blocks

### JavaScript Example:
\`\`\`javascript
function calculateSum(a, b) {
  // This is a comment
  const result = a + b;
  console.log(\`Sum: \${result}\`);
  return result;
}

const numbers = [1, 2, 3, 4, 5];
const total = numbers.reduce((acc, num) => acc + num, 0);
console.log('Total:', total);
\`\`\`

### Python Example:
\`\`\`python
def fibonacci(n):
    """Generate Fibonacci sequence"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Generate first 10 numbers
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
\`\`\`

### TypeScript Example:
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
    return this.users.find(user => user.id === id);
  }
}
\`\`\`

## Lists

### Unordered List:
- First item
- Second item with **bold text**
  - Nested item A
  - Nested item B
    - Deep nested item
- Third item with [a link](https://example.com)

### Ordered List:
1. First step
2. Second step with \`code\`
3. Third step
   1. Sub-step A
   2. Sub-step B
4. Final step

### Task List:
- [x] Completed task
- [x] Another completed task  
- [ ] Pending task
- [ ] Another pending task

## Links & Images

Visit [OpenAI](https://openai.com) or [Claude](https://claude.ai) for AI tools.

Auto-link: https://github.com

![Sample Image](data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjRkY2QjM1Ii8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIyNCIgZmlsbD0iI0ZGRkZGRiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkRpZ2ktU2V0dSBEZW1vPC90ZXh0Pgo8L3N2Zz4K)

## Tables

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| **Markdown** | ✅ Complete | High | Full syntax support |
| *Code Highlighting* | ✅ Complete | High | 100+ languages |
| Tables | ✅ Complete | Medium | Responsive design |
| \`Images\` | 🚧 In Progress | Medium | Upload & display |
| Links | ✅ Complete | Low | Auto-linking works |

### Aligned Table:
| Left Align | Center Align | Right Align |
|:-----------|:------------:|------------:|
| Apple      | Banana       | Cherry      |
| Dog        | Elephant     | Fox         |
| 123        | 456          | 789         |

## Blockquotes

> 💡 **Pro Tip**: This is a single-line blockquote with markdown formatting.

> This is a multi-line blockquote.
> 
> It can contain **formatted text**, \`code\`, and [links](https://example.com).
> 
> > This is a nested blockquote.
> > Very useful for conversations!

## Horizontal Rules

Above this line...

---

Below this line...

***

And another style...

## Special Characters & Escaping

You can escape special characters: \\*not italic\\* and \\**not bold\\**

Emojis work too: 🎉 🚀 💻 🎨 ⚡ 🔥

## Complex Nested Content

1. **Main Topic**: AI Development with Digi-Setu
   
   > "The future belongs to those who understand AI" - *Someone Smart*
   
   - Subtopic: Machine Learning
     - \`scikit-learn\` for beginners
     - \`tensorflow\` for deep learning
     - \`pytorch\` for research
   
   - Subtopic: Natural Language Processing
     
     \`\`\`python
     import openai
     
     response = openai.chat.completions.create(
         model="gpt-4",
         messages=[{"role": "user", "content": "Hello!"}]
     )
     print(response.choices[0].message.content)
     \`\`\`

2. **Advanced Features**:
   
   | Framework | Language | Use Case |
   |-----------|----------|----------|
   | React | JavaScript | Frontend |
   | FastAPI | Python | Backend |
   | Vue.js | JavaScript | Frontend |
   | Nuxt.js | JavaScript | Full-stack |
   
   > **Note**: Choose based on team expertise and project requirements.

## HTML Support (if enabled)

<details>
<summary>Click to expand</summary>

This content is hidden by default!

- Item 1  
- Item 2
- Item 3

</details>

---

## 🎯 Testing Checklist

- [x] Headers (H1-H6)
- [x] Text formatting (bold, italic, strikethrough)
- [x] Code blocks with syntax highlighting  
- [x] Inline code
- [x] Lists (ordered, unordered, nested, tasks)
- [x] Links (inline, auto-link)
- [x] Images
- [x] Tables (basic, aligned)
- [x] Blockquotes (single, multi-line, nested)
- [x] Horizontal rules
- [x] Special characters & emojis
- [x] Complex nested content
- [x] HTML elements (if supported)

**All markdown features tested in Digi-Setu!** ✨

## More Code Examples

### CSS Example:
\`\`\`css
.digi-setu-chat {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-primary);
}

.message-bubble {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
}

.message-bubble.assistant {
  background: var(--bg-secondary);
  border-left: 4px solid var(--accent-primary);
}
\`\`\`

### JSON Example:
\`\`\`json
{
  "name": "digi-setu-demo",
  "version": "1.0.0",
  "features": [
    "markdown-rendering",
    "syntax-highlighting",
    "responsive-design"
  ],
  "config": {
    "theme": "auto",
    "codeHighlighting": true,
    "mathSupport": false
  }
}
\`\`\`

### SQL Example:
\`\`\`sql
-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (name, email) VALUES 
    ('John Doe', 'john@example.com'),
    ('Jane Smith', 'jane@example.com');

-- Query with join
SELECT u.name, u.email, COUNT(m.id) as message_count
FROM users u
LEFT JOIN messages m ON u.id = m.user_id
GROUP BY u.id, u.name, u.email
ORDER BY message_count DESC;
\`\`\`

## 📝 Footnotes

Here's text with a footnote[^1] and another reference[^2].

[^1]: This footnote explains the first reference with **formatting** support.
[^2]: This is the second footnote with [link support](https://example.com).

## 📚 Definition Lists

API
:   Application Programming Interface - allows different software applications to communicate

AI
:   Artificial Intelligence - computer systems that perform tasks typically requiring human intelligence

REST
:   Representational State Transfer - architectural style for web services

## 🔤 Abbreviations

*[HTML]: HyperText Markup Language
*[CSS]: Cascading Style Sheets
*[API]: Application Programming Interface
*[AI]: Artificial Intelligence

When you hover over HTML, CSS, API, or AI in this text, you'll see their definitions!

## 🎯 Complete Feature Test

This comprehensive example showcases **ALL** markdown features including:

- ✅ **Math equations** with KaTeX
- ✅ **Custom containers** for AI responses  
- ✅ **Enhanced formatting** (mark, insert, sub/sup)
- ✅ **Direct emoji support** for engaging responses
- ✅ **Footnotes** for detailed explanations
- ✅ **Definition lists** for glossaries
- ✅ **Abbreviations** with hover definitions
- ✅ **Task lists** with real checkboxes
- ✅ **Code highlighting** with 100+ languages
- ✅ **Tables**, **links**, **images**, and more!

Perfect for AI chat interfaces! 🎉🚀`

// Additional test messages for different scenarios
export const testMessages = [
  {
    id: 1,
    content: mockMarkdownContent,
    role: 'assistant' as const,
    timestamp: new Date()
  },
  {
    id: 2,
    content: 'Can you show me a simple example of **markdown formatting**?',
    role: 'user' as const,
    timestamp: new Date()
  },
  {
    id: 3,
    content: `Here's a quick example:

## Simple Markdown

- **Bold text**
- *Italic text*
- \`inline code\`
- [Link to Google](https://google.com)

\`\`\`javascript
console.log('Hello from Digi-Setu!');
\`\`\`

> This is a blockquote with **formatting**!`,
    role: 'assistant' as const,
    timestamp: new Date()
  },
  {
    id: 4,
    content: 'Perfect! The markdown rendering looks great. Can you also show me a table example?',
    role: 'user' as const,
    timestamp: new Date()
  },
  {
    id: 5,
    content: `Absolutely! Here's a comprehensive table:

| Feature | Status | Description |
|---------|--------|-------------|
| **Headers** | ✅ Working | All H1-H6 levels |
| **Tables** | ✅ Working | With alignment support |
| **Code** | ✅ Working | Syntax highlighting |
| **Lists** | ✅ Working | Ordered, unordered, tasks |
| **Links** | ✅ Working | Internal and external |

### Task Progress:
- [x] Markdown parsing ✅
- [x] Syntax highlighting ✅  
- [x] Table rendering ✅
- [ ] Math equations (future)
- [ ] Mermaid diagrams (future)

Everything is working perfectly! 🎉`,
    role: 'assistant' as const,
    timestamp: new Date()
  }
]
