import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import markdownItTaskLists from 'markdown-it-task-lists'
import markdownItKatex from '@iktakahiro/markdown-it-katex'
import markdownItContainer from 'markdown-it-container'
import markdownItFootnote from 'markdown-it-footnote'
import markdownItMark from 'markdown-it-mark'
import markdownItIns from 'markdown-it-ins'
import markdownItSub from 'markdown-it-sub'
import markdownItSup from 'markdown-it-sup'
import markdownItDeflist from 'markdown-it-deflist'
import markdownItAbbr from 'markdown-it-abbr'
import type { ComponentBlock } from './useEnhancedStreaming'

// ComponentBlock interface is defined in useEnhancedStreaming.ts to avoid duplication

export interface ParsedContent {
  html: string
  components: ComponentBlock[]
  plainText: string
}

export const useEnhancedMarkdown = () => {
  // Initialize markdown-it with enhanced configuration
  const md = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true, // Convert line breaks to <br>
    highlight: function (str: string, lang: string) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return `<pre class="hljs"><code class="language-${lang}">${hljs.highlight(str, { language: lang }).value}</code></pre>`
        } catch (error) {
          console.error('Highlighting error:', error)
        }
      }
      return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`
    }
  })

  // Configure all plugins
  md.use(markdownItTaskLists, { enabled: true, label: true, labelAfter: true })
  
  // Enhanced KaTeX configuration
  md.use(markdownItKatex, { 
    throwOnError: false,
    errorColor: '#cc0000',
    strict: false,
    trust: true,
    output: 'html',
    displayMode: false,
    macros: {
      "\\RR": "\\mathbb{R}",
      "\\NN": "\\mathbb{N}",
      "\\ZZ": "\\mathbb{Z}",
      "\\QQ": "\\mathbb{Q}",
      "\\CC": "\\mathbb{C}",
      "\\vec": "\\overrightarrow{#1}",
      "\\norm": "\\left\\|#1\\right\\|",
      "\\abs": "\\left|#1\\right|",
      "\\set": "\\left\\{#1\\right\\}",
      "\\paren": "\\left(#1\\right)",
      "\\bracket": "\\left[#1\\right]"
    }
  })

  md.use(markdownItFootnote)
  md.use(markdownItMark) // ==highlighted text==
  md.use(markdownItIns) // ++inserted text++
  md.use(markdownItSub) // H~2~O
  md.use(markdownItSup) // x^2^
  md.use(markdownItDeflist)
  md.use(markdownItAbbr)

  // Enhanced containers for different message types
  const containerTypes = [
    { name: 'info', icon: '💡', title: 'Info' },
    { name: 'warning', icon: '⚠️', title: 'Warning' },
    { name: 'tip', icon: '✨', title: 'Tip' },
    { name: 'danger', icon: '🚨', title: 'Danger' },
    { name: 'success', icon: '✅', title: 'Success' },
    { name: 'error', icon: '❌', title: 'Error' },
    { name: 'note', icon: '📝', title: 'Note' }
  ]

  containerTypes.forEach(({ name, icon, title }) => {
    md.use(markdownItContainer, name, {
      validate: (params: string) => params.trim().match(new RegExp(`^${name}\\s*(.*)`)),
      render: (tokens: any[], idx: number) => {
        const token = tokens[idx]
        if (token.nesting === 1) {
          const titleText = token.info.trim().match(new RegExp(`^${name}\\s+(.*)`))
          const customTitle = titleText && titleText[1] ? titleText[1] : title
          return `<div class="container ${name}"><div class="container-header">${icon} ${customTitle}</div>\n`
        } else {
          return '</div>\n'
        }
      }
    })
  })

  // Custom component container for enhanced components
  md.use(markdownItContainer, 'component', {
    validate: (params: string) => params.trim().match(/^component\s+(.*)/),
    render: (tokens: any[], idx: number) => {
      const token = tokens[idx]
      if (token.nesting === 1) {
        const componentInfo = token.info.trim().match(/^component\s+(.*)/)
        const componentType = componentInfo ? componentInfo[1] : 'unknown'
        return `<div class="component-placeholder" data-component-type="${componentType}">\n`
      } else {
        return '</div>\n'
      }
    }
  })

  // Enhanced table rendering with better styling
  const defaultTableRender = md.renderer.rules.table_open || function(tokens, idx, options, env, renderer) {
    return renderer.renderToken(tokens, idx, options)
  }

  md.renderer.rules.table_open = function(tokens, idx, options, env, renderer) {
    return '<div class="table-container"><table class="enhanced-table">'
  }

  const defaultTableClose = md.renderer.rules.table_close || function(tokens, idx, options, env, renderer) {
    return renderer.renderToken(tokens, idx, options)
  }

  md.renderer.rules.table_close = function(tokens, idx, options, env, renderer) {
    return '</table></div>'
  }

  // Enhanced code block rendering
  const defaultCodeBlock = md.renderer.rules.code_block || function(tokens, idx, options, env, renderer) {
    return renderer.renderToken(tokens, idx, options)
  }

  md.renderer.rules.code_block = function(tokens, idx, options, env, renderer) {
    const token = tokens[idx]
    const langName = token.info ? token.info.trim().split(/\s+/g)[0] : ''
    
    return `<div class="code-block-container">
      <div class="code-block-header">
        <span class="code-language">${langName || 'text'}</span>
        <button class="copy-code-btn" onclick="copyCode(this)">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        </button>
      </div>
      <pre class="code-block"><code class="language-${langName}">${md.utils.escapeHtml(token.content)}</code></pre>
    </div>`
  }

  /**
   * Parse component blocks from markdown text
   */
  const parseComponents = (text: string): ComponentBlock[] => {
    const components: ComponentBlock[] = []
    const componentRegex = /:::([\w-]+)(?:\n)([\s\S]*?)(?:\n):::/g
    let match

    while ((match = componentRegex.exec(text)) !== null) {
      const componentType = match[1]
      const componentContent = match[2]
      const fullMatch = match[0]

      try {
        const component: Partial<ComponentBlock> = {
          type: componentType,
          rawContent: fullMatch
        }

        // Parse component properties
        const lines = componentContent.split('\n')
        for (const line of lines) {
          const trimmedLine = line.trim()
          if (trimmedLine.startsWith('title:')) {
            component.title = trimmedLine.replace('title:', '').trim()
          } else if (trimmedLine.startsWith('position:')) {
            component.position = parseInt(trimmedLine.replace('position:', '').trim())
          } else if (trimmedLine.startsWith('action:')) {
            component.action = trimmedLine.replace('action:', '').trim() as 'insert' | 'update'
          } else if (trimmedLine.startsWith('data:')) {
            // Handle multi-line data
            const dataStartIndex = componentContent.indexOf('data:')
            const dataContent = componentContent.substring(dataStartIndex + 5).trim()
            try {
              component.data = JSON.parse(dataContent)
            } catch (e) {
              console.warn('Failed to parse component data:', e)
              component.data = null
            }
          }
        }

        // Validate required fields
        if (component.type && component.position !== undefined && component.action) {
          components.push(component as ComponentBlock)
        }
      } catch (error) {
        console.error('Error parsing component:', error)
      }
    }

    return components.sort((a, b) => a.position - b.position)
  }

  /**
   * Remove component blocks from text
   */
  const removeComponents = (text: string): string => {
    return text.replace(/:::([\w-]+)(?:\n)([\s\S]*?)(?:\n):::/g, '').trim()
  }

  /**
   * Enhanced render function with component extraction
   */
  const renderWithComponents = (content: string): ParsedContent => {
    if (!content) return { html: '', components: [], plainText: '' }
    
    try {
      // Extract components first
      const components = parseComponents(content)
      
      // Remove component blocks from content for clean markdown rendering
      const cleanContent = removeComponents(content)
      
      // Render markdown
      const html = md.render(cleanContent)
      
      // Get plain text (strip HTML)
      const plainText = cleanContent.replace(/[#*_`~\[\]()]/g, '').trim()
      
      return {
        html,
        components,
        plainText
      }
    } catch (error) {
      console.error('Enhanced markdown rendering error:', error)
      return {
        html: `<p>Error rendering markdown: ${error}</p>`,
        components: [],
        plainText: content
      }
    }
  }

  /**
   * Simple render function (backward compatibility)
   */
  const render = (content: string): string => {
    const result = renderWithComponents(content)
    return result.html
  }

  /**
   * Render only text content without components
   */
  const renderTextOnly = (content: string): string => {
    const cleanContent = removeComponents(content)
    return md.render(cleanContent)
  }

  /**
   * Extract plain text from markdown
   */
  const extractPlainText = (content: string): string => {
    const cleanContent = removeComponents(content)
    return cleanContent
      .replace(/[#*_`~\[\]()]/g, '')
      .replace(/\n+/g, ' ')
      .trim()
  }

  /**
   * Get word count from content
   */
  const getWordCount = (content: string): number => {
    const plainText = extractPlainText(content)
    return plainText.split(/\s+/).filter(word => word.length > 0).length
  }

  /**
   * Get reading time estimate (words per minute)
   */
  const getReadingTime = (content: string, wpm: number = 200): number => {
    const wordCount = getWordCount(content)
    return Math.ceil(wordCount / wpm)
  }

  return {
    // Core functionality
    md,
    render,
    renderWithComponents,
    renderTextOnly,
    
    // Component handling
    parseComponents,
    removeComponents,
    
    // Utility functions
    extractPlainText,
    getWordCount,
    getReadingTime
  }
}
