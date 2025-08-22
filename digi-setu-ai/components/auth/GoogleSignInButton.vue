<template>
  <div class="google-signin-wrapper">
    <!-- Google Sign-In Button -->
    <div 
      class="btn-google"
      :disabled="isLoading"
      @click="handleGoogleSignIn"
    >
      <div class="btn-google-content">
        <svg class="google-icon" viewBox="0 0 24 24" width="20" height="20">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        <span v-if="!isLoading">Continue with Google</span>
        <span v-else>Signing in...</span>
      </div>
      <div v-if="isLoading" class="loading-spinner" />
    </div>

    <!-- Error message -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
const isLoading = ref(false)
const errorMessage = ref('')

// Auth service configuration
const AUTH_SERVICE_URL = 'http://localhost:8000'

// Use enhanced auth composable (get it at component setup time)
const { loginWithGoogle, checkAuthStatus } = useEnhancedAuth()

interface AuthResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: {
    id: string
    email: string
    name: string
    picture: string
    verified_email: boolean
  }
}

// Removed unused interfaces - GoogleNotification and GoogleCredentialResponse

const emit = defineEmits<{
  'auth-success': [user: AuthResponse['user']]
  'auth-error': [error: string]
}>()

const handleGoogleSignIn = async () => {
  if (isLoading.value) return
  
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    // Step 1: Get Google auth URL from our authentication service
    console.log('Getting Google auth URL...')
    const authUrlResponse = await $fetch<{auth_url: string}>(`${AUTH_SERVICE_URL}/auth/google/url`)
    
    // Step 2: Open Google OAuth popup
    console.log('Opening Google OAuth popup...')
    const popup = window.open(
      authUrlResponse.auth_url,
      'google-auth',
      'width=500,height=600,scrollbars=yes,resizable=yes,left=' + 
      (window.screen.width / 2 - 250) + ',top=' + (window.screen.height / 2 - 300)
    )
    
    if (!popup) {
      throw new Error('Popup window was blocked. Please allow popups for this site.')
    }
    
    // Step 3: Wait for the authentication callback
    console.log('Waiting for auth callback...')
    const result = await waitForAuthCallback(popup)
    
    if (result.success && result.auth_code && result.user) {
      console.log('Received auth code from popup...')
      
      // Step 4: Exchange auth code for secure cookies in parent window
      try {
        console.log('Exchanging auth code for cookies...')
        
        const response = await fetch('http://localhost:8000/api/auth/exchange-auth-code', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            auth_code: result.auth_code
          })
        })
        
        if (response.ok) {
          console.log('Auth code exchanged successfully, cookies set')
          
          // Verify auth status
          const isNowAuthenticated = await checkAuthStatus()
          if (isNowAuthenticated) {
            console.log('Parent window authentication confirmed')
            emit('auth-success', result.user)
          } else {
            console.log('Auth status check failed, but proceeding...')
            emit('auth-success', result.user)
          }
        } else {
          console.error('Failed to exchange auth code:', response.status)
          throw new Error('Authentication exchange failed')
        }
      } catch (error) {
        console.error('Error exchanging auth code:', error)
        throw new Error('Authentication failed')
      }
    } else {
      throw new Error('Authentication was cancelled or failed')
    }
  } catch (error: unknown) {
    console.error('Authentication failed:', error)
    errorMessage.value = error instanceof Error ? error.message : 'Authentication failed. Please try again.'
    emit('auth-error', error instanceof Error ? error.message : 'Authentication failed')
  } finally {
    isLoading.value = false
  }
}

const waitForAuthCallback = (_popup: Window): Promise<{success: boolean, access_token?: string, user?: AuthResponse['user']}> => {
  return new Promise((resolve) => {
    let resolved = false
    
    // Listen for postMessage from popup
    const messageHandler = (event: MessageEvent) => {
      // Accept messages from localhost (our auth service callback)
      if (event.origin !== window.location.origin && 
          event.origin !== 'http://localhost:8000') {
        return
      }
      
      console.log('Received message from popup:', event.data.type)
      
      if (event.data.type === 'GOOGLE_AUTH_SUCCESS' && !resolved) {
        resolved = true
        window.removeEventListener('message', messageHandler)
        console.log('Auth success received, resolving...')
        resolve({ 
          success: true, 
          auth_code: event.data.auth_code,
          user: event.data.user
        })
      } else if (event.data.type === 'GOOGLE_AUTH_ERROR' && !resolved) {
        resolved = true
        window.removeEventListener('message', messageHandler)
        console.log('Auth error received')
        resolve({ success: false })
      }
    }
    
    window.addEventListener('message', messageHandler)
    
    // Cleanup after 5 minutes - no popup.closed check to avoid COOP errors
    setTimeout(() => {
      if (!resolved) {
        resolved = true
        window.removeEventListener('message', messageHandler)
        console.log('Auth timeout - no response received')
        resolve({ success: false })
      }
    }, 300000) // 5 minutes
  })
}
</script>

<style scoped>
.google-signin-wrapper {
  width: 100%;
}

.btn-google {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.btn-google:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--border-secondary);
}

.btn-google:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-google-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.google-icon {
  flex-shrink: 0;
}

.loading-spinner {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  border: 2px solid var(--border-primary);
  border-top: 2px solid var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: translateY(-50%) rotate(0deg); }
  100% { transform: translateY(-50%) rotate(360deg); }
}

.error-message {
  margin-top: 8px;
  padding: 8px 12px;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c33;
  font-size: 12px;
  text-align: center;
}
</style>