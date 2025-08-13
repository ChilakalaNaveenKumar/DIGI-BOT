import { ref, onMounted } from 'vue'

export const useTheme = () => {
  const theme = ref('light')

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    updateTheme()
    localStorage.setItem('theme', theme.value)
  }

  const updateTheme = () => {
    if (theme.value === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  const initTheme = () => {
    // Check localStorage first, then system preference
    const savedTheme = localStorage.getItem('theme')
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

    if (savedTheme) {
      theme.value = savedTheme
    } else if (systemPrefersDark) {
      theme.value = 'dark'
    }

    updateTheme()
  }

  onMounted(() => {
    initTheme()
  })

  return {
    theme,
    toggleTheme
  }
}

