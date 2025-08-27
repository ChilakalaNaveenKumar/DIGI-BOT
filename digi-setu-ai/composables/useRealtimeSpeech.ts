import { ref, computed, readonly } from 'vue'

export const useRealtimeSpeech = () => {
  const isListening = ref(false)
  const transcript = ref('')
  const interimTranscript = ref('')
  const isConnected = ref(false)
  const error = ref<string | null>(null)
  
  let deepgram: any = null
  let connection: any = null
  let mediaRecorder: MediaRecorder | null = null
  let stream: MediaStream | null = null

  // Deepgram API key - you'll need to set this in your environment
  const DEEPGRAM_API_KEY = import.meta.env.NUXT_PUBLIC_DEEPGRAM_API_KEY || 'your-deepgram-api-key'

  const initializeDeepgram = async () => {
    try {
      if (typeof window === 'undefined') return false
      
      const { createClient } = await import('@deepgram/sdk')
      deepgram = createClient(DEEPGRAM_API_KEY)
      return true
    } catch (err) {
      console.error('Failed to initialize Deepgram:', err)
      error.value = 'Failed to initialize speech recognition service'
      return false
    }
  }

  const startListening = async () => {
    try {
      error.value = null
      
      // Initialize Deepgram if not already done
      if (!deepgram && !(await initializeDeepgram())) {
        return false
      }

      // Get microphone access
      stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000
        }
      })

      // Create Deepgram connection
      connection = deepgram.listen.live({
        model: 'nova-2',
        language: 'en-US',
        smart_format: true,
        interim_results: true,
        endpointing: 300,
        utterance_end_ms: 1000,
        vad_events: true
      })

      // Set up event listeners
      const { LiveTranscriptionEvents } = await import('@deepgram/sdk')
      
      connection.on(LiveTranscriptionEvents.Open, () => {
        console.log('Deepgram connection opened')
        isConnected.value = true
      })

      connection.on(LiveTranscriptionEvents.Transcript, (data: any) => {
        const words = data.channel?.alternatives?.[0]?.words
        if (words && words.length > 0) {
          const transcriptText = words.map((word: any) => word.word).join(' ')
          
          if (data.is_final) {
            transcript.value += transcriptText + ' '
            interimTranscript.value = ''
            console.log('Final transcript:', transcriptText)
          } else {
            interimTranscript.value = transcriptText
            console.log('Interim transcript:', transcriptText)
          }
        }
      })

      connection.on(LiveTranscriptionEvents.Error, (err: any) => {
        console.error('Deepgram error:', err)
        error.value = 'Speech recognition error occurred'
      })

      connection.on(LiveTranscriptionEvents.Close, () => {
        console.log('Deepgram connection closed')
        isConnected.value = false
      })

      // Set up MediaRecorder to send audio to Deepgram
      mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && connection && isConnected.value) {
          connection.send(event.data)
        }
      }

      // Start recording and sending audio
      mediaRecorder.start(100) // Send data every 100ms
      isListening.value = true

      return true
    } catch (err) {
      console.error('Failed to start listening:', err)
      error.value = 'Failed to access microphone or start speech recognition'
      return false
    }
  }

  const stopListening = () => {
    try {
      isListening.value = false

      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop()
      }

      if (stream) {
        stream.getTracks().forEach(track => track.stop())
        stream = null
      }

      if (connection) {
        connection.finish()
        connection = null
      }

      isConnected.value = false
      console.log('Stopped listening')
    } catch (err) {
      console.error('Error stopping speech recognition:', err)
    }
  }

  const clearTranscript = () => {
    transcript.value = ''
    interimTranscript.value = ''
  }

  const fullTranscript = computed(() => {
    return transcript.value + interimTranscript.value
  })

  const hasApiKey = computed(() => {
    return DEEPGRAM_API_KEY && DEEPGRAM_API_KEY !== 'your-deepgram-api-key'
  })

  return {
    // State
    isListening: readonly(isListening),
    transcript: readonly(transcript),
    interimTranscript: readonly(interimTranscript),
    fullTranscript,
    isConnected: readonly(isConnected),
    error: readonly(error),
    hasApiKey,

    // Methods
    startListening,
    stopListening,
    clearTranscript
  }
}

// Fallback to Web Speech API if Deepgram is not available
export const useWebSpeechFallback = () => {
  const isListening = ref(false)
  const transcript = ref('')
  const interimTranscript = ref('')
  const error = ref<string | null>(null)
  
  let recognition: any = null

  const startListening = async () => {
    try {
      error.value = null

      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        error.value = 'Speech recognition not supported in this browser'
        return false
      }

      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      recognition = new SpeechRecognition()

      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'en-US'
      recognition.maxAlternatives = 3

      recognition.onstart = () => {
        isListening.value = true
        console.log('Web Speech API started')
      }

      recognition.onresult = (event: any) => {
        let finalTranscript = ''
        let interim = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i]
          const transcriptText = result[0].transcript

          if (result.isFinal) {
            finalTranscript += transcriptText
          } else {
            interim += transcriptText
          }
        }

        if (finalTranscript) {
          transcript.value += finalTranscript + ' '
          console.log('Web Speech final transcript:', finalTranscript)
        }
        interimTranscript.value = interim
        if (interim) {
          console.log('Web Speech interim transcript:', interim)
        }
      }

      recognition.onerror = (event: any) => {
        console.error('Web Speech API error:', event.error)
        error.value = `Speech recognition error: ${event.error}`
      }

      recognition.onend = () => {
        console.log('Web Speech API ended, isListening:', isListening.value)
        if (isListening.value) {
          // Restart if still supposed to be listening
          setTimeout(() => {
            if (recognition && isListening.value) {
              try {
                recognition.start()
                console.log('Web Speech API restarted')
              } catch (err) {
                console.error('Failed to restart Web Speech API:', err)
              }
            }
          }, 500)
        }
      }

      recognition.start()
      return true
    } catch (err) {
      console.error('Failed to start Web Speech API:', err)
      error.value = 'Failed to start speech recognition'
      return false
    }
  }

  const stopListening = () => {
    isListening.value = false
    if (recognition) {
      recognition.stop()
      recognition = null
    }
  }

  const clearTranscript = () => {
    transcript.value = ''
    interimTranscript.value = ''
  }

  const fullTranscript = computed(() => {
    return transcript.value + interimTranscript.value
  })

  return {
    isListening: readonly(isListening),
    transcript: readonly(transcript),
    interimTranscript: readonly(interimTranscript),
    fullTranscript,
    error: readonly(error),
    startListening,
    stopListening,
    clearTranscript
  }
}
