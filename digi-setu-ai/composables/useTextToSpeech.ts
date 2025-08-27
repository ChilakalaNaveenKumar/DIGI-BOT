import { ref, computed, readonly } from 'vue'

export const useTextToSpeech = () => {
  const isSpeaking = ref(false)
  const currentUtterance = ref<SpeechSynthesisUtterance | null>(null)
  const voices = ref<SpeechSynthesisVoice[]>([])
  const selectedVoice = ref<SpeechSynthesisVoice | null>(null)
  const rate = ref(1.0)
  const pitch = ref(1.0)
  const volume = ref(0.8)

  // Initialize voices
  const loadVoices = () => {
    voices.value = speechSynthesis.getVoices()
    
    // Try to find a good English voice
    const englishVoices = voices.value.filter(voice => 
      voice.lang.startsWith('en') && !voice.name.includes('Google')
    )
    
    // Prefer system voices over Google voices for better quality
    const preferredVoice = englishVoices.find(voice => 
      voice.name.includes('Samantha') || 
      voice.name.includes('Alex') || 
      voice.name.includes('Daniel') ||
      voice.name.includes('Karen') ||
      voice.name.includes('Moira')
    ) || englishVoices[0] || voices.value[0]
    
    selectedVoice.value = preferredVoice
  }

  // Load voices when available
  if (speechSynthesis.getVoices().length > 0) {
    loadVoices()
  } else {
    speechSynthesis.addEventListener('voiceschanged', loadVoices)
  }

  const speak = async (text: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!text.trim()) {
        resolve()
        return
      }

      // Stop any current speech
      stop()

      const utterance = new SpeechSynthesisUtterance(text)
      currentUtterance.value = utterance

      // Configure utterance
      if (selectedVoice.value) {
        utterance.voice = selectedVoice.value
      }
      utterance.rate = rate.value
      utterance.pitch = pitch.value
      utterance.volume = volume.value

      // Set up event handlers
      utterance.onstart = () => {
        isSpeaking.value = true
      }

      utterance.onend = () => {
        isSpeaking.value = false
        currentUtterance.value = null
        resolve()
      }

      utterance.onerror = (event) => {
        isSpeaking.value = false
        currentUtterance.value = null
        console.error('Speech synthesis error:', event.error)
        reject(new Error(`Speech synthesis failed: ${event.error}`))
      }

      // Start speaking
      speechSynthesis.speak(utterance)
    })
  }

  const speakStreaming = async (text: string, onChunk?: (chunk: string) => void): Promise<void> => {
    // Split text into sentences for more natural streaming
    const sentences = text.match(/[^\.!?]+[\.!?]+/g) || [text]
    
    for (const sentence of sentences) {
      if (sentence.trim()) {
        onChunk?.(sentence.trim())
        await speak(sentence.trim())
        
        // Small pause between sentences
        await new Promise(resolve => setTimeout(resolve, 200))
      }
    }
  }

  const stop = () => {
    if (isSpeaking.value) {
      speechSynthesis.cancel()
      isSpeaking.value = false
      currentUtterance.value = null
    }
  }

  const pause = () => {
    if (isSpeaking.value) {
      speechSynthesis.pause()
    }
  }

  const resume = () => {
    if (speechSynthesis.paused) {
      speechSynthesis.resume()
    }
  }

  const setVoice = (voice: SpeechSynthesisVoice) => {
    selectedVoice.value = voice
  }

  const setRate = (newRate: number) => {
    rate.value = Math.max(0.1, Math.min(10, newRate))
  }

  const setPitch = (newPitch: number) => {
    pitch.value = Math.max(0, Math.min(2, newPitch))
  }

  const setVolume = (newVolume: number) => {
    volume.value = Math.max(0, Math.min(1, newVolume))
  }

  const isSupported = computed(() => {
    return 'speechSynthesis' in window
  })

  return {
    // State
    isSpeaking: readonly(isSpeaking),
    voices: readonly(voices),
    selectedVoice: readonly(selectedVoice),
    rate: readonly(rate),
    pitch: readonly(pitch),
    volume: readonly(volume),
    isSupported,

    // Methods
    speak,
    speakStreaming,
    stop,
    pause,
    resume,
    setVoice,
    setRate,
    setPitch,
    setVolume,
    loadVoices
  }
}
