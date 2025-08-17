<template>
  <div class="ds-smart-renderer">
    <!-- Render content sections based on detected boundaries -->
    <div v-for="(section, index) in contentSections" :key="index">
      
      <!-- Code Block Section -->
      <div v-if="section.type === 'code'" class="ds-code-wrapper">
        <DigiSetuCodeHighlighter 
          :content="section.content"
          :is-streaming="section.isStreaming"
        />
      </div>
      
      <!-- Math Section -->
      <div v-else-if="section.type === 'math'" class="ds-math-wrapper">
        <DigiSetuMathRenderer 
          :content="section.content"
          :is-streaming="section.isStreaming"
        />
      </div>
      
      <!-- SVG Section -->
      <div v-else-if="section.type === 'svg'" class="ds-svg-wrapper">
        <DigiSetuSvgRenderer 
          :content="section.content"
          :is-streaming="section.isStreaming"
        />
      </div>
      
      <!-- Diagram Section -->
      <div v-else-if="section.type === 'diagram'" class="ds-diagram-wrapper">
        <DigiSetuDiagramRenderer 
          :content="section.content"
          :is-streaming="section.isStreaming"
        />
      </div>
      
      <!-- Table Section -->
      <div v-else-if="section.type === 'table'" class="ds-table-wrapper">
        <DigiSetuTableRenderer 
          :content="section.content"
          :is-streaming="section.isStreaming"
        />
      </div>
      
      <!-- Default: Plain text/markdown -->
      <div v-else class="ds-text-wrapper">
        <DigiSetuTextRenderer 
          :content="section.content"
          :is-streaming="section.isStreaming"
        />
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import DigiSetuCodeHighlighter from './DigiSetuCodeHighlighter.vue'
import DigiSetuMathRenderer from './DigiSetuMathRenderer.vue'
import DigiSetuSvgRenderer from './DigiSetuSvgRenderer.vue'
import DigiSetuDiagramRenderer from './DigiSetuDiagramRenderer.vue'
import DigiSetuTableRenderer from './DigiSetuTableRenderer.vue'
import DigiSetuTextRenderer from './DigiSetuTextRenderer.vue'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  isStreaming: {
    type: Boolean,
    default: false
  }
})

// Parse content into sections with boundary detection
const contentSections = computed(() => {
  if (!props.content) return [{ type: 'text', content: '', isStreaming: false }]
  
  const sections = []
  let currentIndex = 0
  const content = props.content
  
  while (currentIndex < content.length) {
    // Look for code block start ```
    const codeStart = content.indexOf('```', currentIndex)
    
    // Look for math start \\( or \\[ - improved detection
    const mathInlineStart = content.indexOf('\\(', currentIndex)
    const mathBlockStart = content.indexOf('\\[', currentIndex)
    
    // Also look for common math patterns in the middle of text
    const mathPatternRegex = /\\[a-zA-Z]+\{|\\frac\{|\\sqrt\{|\\sum|\\int|\\alpha|\\beta|\\gamma|\\delta|\\pi|\\theta/
    const mathPatternMatch = content.substring(currentIndex).search(mathPatternRegex)
    const mathPatternStart = mathPatternMatch !== -1 ? currentIndex + mathPatternMatch : -1
    
    const mathStart = Math.min(
      ...[mathInlineStart, mathBlockStart, mathPatternStart].filter(pos => pos !== -1)
    )
    
    // Look for SVG content
    const svgStart = content.indexOf('<svg', currentIndex)
    
    // Look for Venn diagram keywords
    const vennStart = findVennDiagramStart(content, currentIndex)
    
    // Look for table start (| with ---)
    const tableStart = findTableStart(content, currentIndex)
    
    // Find the earliest special content
    const earliestSpecial = Math.min(
      ...[codeStart, mathStart, svgStart, vennStart, tableStart].filter(pos => pos !== -1)
    )
    
    // If no special content found, add rest as text
    if (earliestSpecial === Infinity) {
      const textContent = content.substring(currentIndex)
      if (textContent.trim()) {
        sections.push({
          type: 'text',
          content: textContent,
          isStreaming: props.isStreaming && currentIndex + textContent.length === content.length
        })
      }
      break
    }
    
    // Add text before special content
    if (earliestSpecial > currentIndex) {
      const textContent = content.substring(currentIndex, earliestSpecial)
      if (textContent.trim()) {
        sections.push({
          type: 'text',
          content: textContent,
          isStreaming: false
        })
      }
    }
    
    // Handle the special content
    if (earliestSpecial === codeStart) {
      const codeSection = extractCodeSection(content, codeStart)
      sections.push(codeSection.section)
      currentIndex = codeSection.nextIndex
    } else if (earliestSpecial === mathStart) {
      const mathSection = extractMathSection(content, mathStart)
      sections.push(mathSection.section)
      currentIndex = mathSection.nextIndex
    } else if (earliestSpecial === svgStart) {
      const svgSection = extractSvgSection(content, svgStart)
      sections.push(svgSection.section)
      currentIndex = svgSection.nextIndex
    } else if (earliestSpecial === vennStart) {
      const vennSection = extractVennDiagramSection(content, vennStart)
      sections.push(vennSection.section)
      currentIndex = vennSection.nextIndex
    } else if (earliestSpecial === tableStart) {
      const tableSection = extractTableSection(content, tableStart)
      sections.push(tableSection.section)
      currentIndex = tableSection.nextIndex
    }
  }
  
  return sections.length > 0 ? sections : [{ type: 'text', content: props.content, isStreaming: props.isStreaming }]
})

// Helper functions for boundary detection
const findVennDiagramStart = (content, startIndex) => {
  const lowerContent = content.toLowerCase()
  
  // Look for ASCII art patterns (text-based Venn diagrams)
  const asciiPatterns = [
    /```[\s\S]*?[\/\\()\-_|]+[\s\S]*?```/,  // Code blocks with ASCII art characters
    /\s+[\/\\()\-_]{3,}/,  // Lines with ASCII drawing characters
    /\s+\|\s+/,  // Pipe characters with spaces
    /\s+\/\\|\\\//,  // Forward/back slashes
    /\s+\+[-=]+\+/,  // Box drawing characters
    /\s+○|●|◯/,  // Circle characters
  ]
  
  // Check for ASCII patterns first
  for (const pattern of asciiPatterns) {
    const match = content.substring(startIndex).match(pattern)
    if (match && match.index !== undefined) {
      return startIndex + match.index
    }
  }
  
  // Look for Venn diagram keywords
  const vennKeywords = ['venn diagram', 'overlapping circles', 'sets', 'intersection']
  
  for (const keyword of vennKeywords) {
    const keywordIndex = lowerContent.indexOf(keyword, startIndex)
    if (keywordIndex !== -1) {
      // Find the start of the sentence/paragraph containing the keyword
      const sentenceStart = content.lastIndexOf('.', keywordIndex) + 1
      return Math.max(sentenceStart, startIndex)
    }
  }
  
  return -1
}

const findTableStart = (content, startIndex) => {
  const pipeIndex = content.indexOf('|', startIndex)
  if (pipeIndex === -1) return -1
  
  // Check if there's a --- separator nearby
  const lineEnd = content.indexOf('\n', pipeIndex)
  const nextLineStart = lineEnd === -1 ? content.length : lineEnd + 1
  const nextLine = content.substring(nextLineStart, content.indexOf('\n', nextLineStart))
  
  if (nextLine.includes('---')) {
    return pipeIndex
  }
  
  return -1
}

const extractCodeSection = (content, startIndex) => {
  const codeEnd = content.indexOf('```', startIndex + 3)
  
  if (codeEnd === -1) {
    // No closing ```, take rest of content (streaming)
    return {
      section: {
        type: 'code',
        content: content.substring(startIndex),
        isStreaming: true
      },
      nextIndex: content.length
    }
  } else {
    // Complete code block
    return {
      section: {
        type: 'code',
        content: content.substring(startIndex, codeEnd + 3),
        isStreaming: false
      },
      nextIndex: codeEnd + 3
    }
  }
}

const extractMathSection = (content, startIndex) => {
  const isBlock = content.substring(startIndex, startIndex + 2) === '\\['
  const endPattern = isBlock ? '\\]' : '\\)'
  const mathEnd = content.indexOf(endPattern, startIndex + 2)
  
  if (mathEnd === -1) {
    // No closing, take rest of content (streaming)
    return {
      section: {
        type: 'math',
        content: content.substring(startIndex),
        isStreaming: true
      },
      nextIndex: content.length
    }
  } else {
    // Complete math block
    return {
      section: {
        type: 'math',
        content: content.substring(startIndex, mathEnd + 2),
        isStreaming: false
      },
      nextIndex: mathEnd + 2
    }
  }
}

const extractSvgSection = (content, startIndex) => {
  // Find the closing </svg> tag
  const svgEnd = content.indexOf('</svg>', startIndex)
  
  if (svgEnd === -1) {
    // No closing tag, take rest of content (streaming)
    return {
      section: {
        type: 'svg',
        content: content.substring(startIndex),
        isStreaming: true
      },
      nextIndex: content.length
    }
  } else {
    // Complete SVG
    return {
      section: {
        type: 'svg',
        content: content.substring(startIndex, svgEnd + 6), // +6 for </svg>
        isStreaming: false
      },
      nextIndex: svgEnd + 6
    }
  }
}

const extractVennDiagramSection = (content, startIndex) => {
  // Find end of Venn diagram description (next paragraph or end of content)
  let vennEnd = startIndex
  const lines = content.substring(startIndex).split('\n')
  let emptyLineCount = 0
  
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim() === '') {
      emptyLineCount++
      if (emptyLineCount >= 2) {
        // Two empty lines = end of diagram description
        vennEnd = startIndex + lines.slice(0, i - 1).join('\n').length
        break
      }
    } else {
      emptyLineCount = 0
    }
    
    if (i === lines.length - 1) {
      vennEnd = content.length
    }
  }
  
  return {
    section: {
      type: 'diagram',
      content: content.substring(startIndex, vennEnd),
      isStreaming: vennEnd === content.length && props.isStreaming
    },
    nextIndex: vennEnd
  }
}

const extractTableSection = (content, startIndex) => {
  // Find end of table (empty line or no more | characters)
  let tableEnd = startIndex
  const lines = content.substring(startIndex).split('\n')
  
  for (let i = 0; i < lines.length; i++) {
    if (!lines[i].includes('|') && lines[i].trim() === '') {
      tableEnd = startIndex + lines.slice(0, i).join('\n').length
      break
    }
    if (i === lines.length - 1) {
      tableEnd = content.length
    }
  }
  
  return {
    section: {
      type: 'table',
      content: content.substring(startIndex, tableEnd),
      isStreaming: tableEnd === content.length && props.isStreaming
    },
    nextIndex: tableEnd
  }
}
</script>

<style scoped>
.ds-smart-renderer {
  width: 100%;
}

.ds-code-wrapper,
.ds-math-wrapper, 
.ds-table-wrapper,
.ds-text-wrapper {
  width: 100%;
  margin: 0;
  padding: 0;
}
</style>
