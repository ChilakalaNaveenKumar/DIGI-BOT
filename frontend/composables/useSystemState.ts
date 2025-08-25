// Global system state using Vue's useState (Nuxt 3)
export const useSystemState = () => {
  // Use Nuxt's global state management
  const useDigiSetuSystem = useState('digi-setu-system', () => false)
  
  const toggleSystem = (value: boolean) => {
    useDigiSetuSystem.value = value
  }
  
  const getCurrentSystem = () => {
    return useDigiSetuSystem.value ? 'Digi Setu' : 'Mock'
  }
  
  return {
    useDigiSetuSystem,
    toggleSystem,
    getCurrentSystem
  }
}
