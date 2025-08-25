import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import markdownItTaskLists from 'markdown-it-task-lists'
// Import the modern, actively maintained KaTeX plugin
import markdownItKatex from '@iktakahiro/markdown-it-katex'
import markdownItContainer from 'markdown-it-container'
import markdownItFootnote from 'markdown-it-footnote'
import markdownItMark from 'markdown-it-mark'
import markdownItIns from 'markdown-it-ins'
import markdownItSub from 'markdown-it-sub'
import markdownItSup from 'markdown-it-sup'
import markdownItDeflist from 'markdown-it-deflist'
import markdownItAbbr from 'markdown-it-abbr'

export const useMarkdown = () => {
  // Initialize markdown-it with all plugins
  const md = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    highlight: function (str: string, lang: string) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return hljs.highlight(str, { language: lang }).value
        } catch (error) {
          console.error('Highlighting error:', error)
        }
      }
      return '' // use external default escaping
    }
  })

  // Configure all plugins
  md.use(markdownItTaskLists, { enabled: true, label: true })
  
  // Configure KaTeX plugin with enhanced settings
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

  // Custom containers for AI responses
  md.use(markdownItContainer, 'info', {
    validate: (params: string) => params.trim().match(/^info\s*(.*)$/),
    render: (tokens: unknown[], idx: number) => {
      const token = tokens[idx] as { nesting: number }
      if (token.nesting === 1) {
        return '<div class="container info"><div class="container-header">💡 Info</div>\n'
      } else {
        return '</div>\n'
      }
    }
  })

  md.use(markdownItContainer, 'warning', {
    validate: (params: string) => params.trim().match(/^warning\s*(.*)$/),
    render: (tokens: unknown[], idx: number) => {
      const token = tokens[idx] as { nesting: number }
      if (token.nesting === 1) {
        return '<div class="container warning"><div class="container-header">⚠️ Warning</div>\n'
      } else {
        return '</div>\n'
      }
    }
  })

  md.use(markdownItContainer, 'tip', {
    validate: (params: string) => params.trim().match(/^tip\s*(.*)$/),
    render: (tokens: unknown[], idx: number) => {
      const token = tokens[idx] as { nesting: number }
      if (token.nesting === 1) {
        return '<div class="container tip"><div class="container-header">✨ Tip</div>\n'
      } else {
        return '</div>\n'
      }
    }
  })

  md.use(markdownItContainer, 'danger', {
    validate: (params: string) => params.trim().match(/^danger\s*(.*)$/),
    render: (tokens: unknown[], idx: number) => {
      const token = tokens[idx] as { nesting: number }
      if (token.nesting === 1) {
        return '<div class="container danger"><div class="container-header">🚨 Danger</div>\n'
      } else {
        return '</div>\n'
      }
    }
  })

  // Simple render function
  const render = (content: string): string => {
    if (!content) return ''
    
    try {
      // Remove any remaining component blocks that might have slipped through
      // This prevents the markdown renderer from trying to process them
      const cleanContent = content.replace(/:::[^:]+\n[\s\S]*?\n:::/g, '')
      return md.render(cleanContent)
    } catch (error) {
      console.error('Markdown rendering error:', error)
      return `<p>Error rendering markdown: ${error}</p>`
    }
  }

  return {
    md,
    render
  }
}
