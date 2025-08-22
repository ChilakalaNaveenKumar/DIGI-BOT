// Type declarations for markdown-it plugins without official types
declare module 'markdown-it-task-lists' {
  import type MarkdownIt from 'markdown-it'
  
  interface TaskListOptions {
    enabled?: boolean
    label?: boolean
    labelAfter?: boolean
  }
  
  function taskLists(md: MarkdownIt, options?: TaskListOptions): void
  export = taskLists
}

declare module '@iktakahiro/markdown-it-katex' {
  import type MarkdownIt from 'markdown-it'
  
  interface KatexOptions {
    throwOnError?: boolean
    errorColor?: string
    strict?: boolean
    trust?: boolean
    output?: string
    displayMode?: boolean
    macros?: Record<string, string>
  }
  
  function katex(md: MarkdownIt, options?: KatexOptions): void
  export = katex
}

declare module 'markdown-it-container' {
  import type MarkdownIt from 'markdown-it'
  
  interface ContainerOptions {
    validate?: (params: string) => RegExpMatchArray | null
    render?: (tokens: any[], idx: number) => string
  }
  
  function container(md: MarkdownIt, name: string, options?: ContainerOptions): void
  export = container
}

declare module 'markdown-it-footnote' {
  import type MarkdownIt from 'markdown-it'
  
  function footnote(md: MarkdownIt): void
  export = footnote
}

declare module 'markdown-it-mark' {
  import type MarkdownIt from 'markdown-it'
  
  function mark(md: MarkdownIt): void
  export = mark
}

declare module 'markdown-it-ins' {
  import type MarkdownIt from 'markdown-it'
  
  function ins(md: MarkdownIt): void
  export = ins
}

declare module 'markdown-it-sub' {
  import type MarkdownIt from 'markdown-it'
  
  function sub(md: MarkdownIt): void
  export = sub
}

declare module 'markdown-it-sup' {
  import type MarkdownIt from 'markdown-it'
  
  function sup(md: MarkdownIt): void
  export = sup
}

declare module 'markdown-it-deflist' {
  import type MarkdownIt from 'markdown-it'
  
  function deflist(md: MarkdownIt): void
  export = deflist
}

declare module 'markdown-it-abbr' {
  import type MarkdownIt from 'markdown-it'
  
  function abbr(md: MarkdownIt): void
  export = abbr
}

