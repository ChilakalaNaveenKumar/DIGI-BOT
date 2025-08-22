<template>
  <div class="auth-callback">
    <div class="callback-container">
      <div v-if="isProcessing" class="processing">
        <div class="loading-spinner"></div>
        <h2>Completing authentication...</h2>
        <p>Please wait while we verify your credentials.</p>
      </div>
      
      <div v-else-if="error" class="error">
        <div class="error-icon">⚠️</div>
        <h2>Authentication Error</h2>
        <p>{{ error }}</p>
        <button @click="closeWindow" class="btn-close">Close Window</button>
      </div>
      
      <div v-else class="success">
        <div class="success-icon">✅</div>
        <h2>Authentication Successful</h2>
        <p>You can close this window and return to the application.</p>
        <button @click="closeWindow" class="btn-close">Close Window</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const isProcessing = ref(true)
const error = ref('')

// Set page layout
definePageMeta({
  layout: false // Don't use the default layout for this popup page
})

onMounted(async () => {
  const code = route.query.code as string
  const authError = route.query.error as string
  const state = route.query.state as string
  
  console.log('Auth callback received:', { code: !!code, error: authError, state })
  
  if (authError) {
    error.value = `Authentication failed: ${authError}`
    isProcessing.value = false
    notifyParent('GOOGLE_AUTH_ERROR', { error: authError })
    return
  }
  
  if (!code) {
    error.value = 'No authorization code received from Google'
    isProcessing.value = false
    notifyParent('GOOGLE_AUTH_ERROR', { error: 'No authorization code' })
    return
  }
  
  try {
    // Exchange authorization code for tokens using our backend
    console.log('Exchanging authorization code for tokens...')
    
    const response = await fetch(`http://localhost:8000/auth/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state || '')}`, {
      method: 'GET',
      credentials: 'include', // Important: include cookies
      headers: {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      }
    })
    
    if (response.ok) {
      // The backend should have set secure cookies
      console.log('Authentication successful, cookies should be set')
      
      // Try to get user info from the response if it's JSON
      let userData = null
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        userData = await response.json()
      }
      
      // Notify parent window of success
      notifyParent('GOOGLE_AUTH_SUCCESS', { 
        success: true,
        user: userData?.user || null,
        access_token: 'cookie-based', // Indicate we're using cookies
        reload_parent: true // Signal parent to reload/refresh auth state
      })
      
      isProcessing.value = false
      
      // Auto-close after 2 seconds
      setTimeout(() => {
        closeWindow()
      }, 2000)
    } else {
      throw new Error(`Authentication failed: ${response.status} ${response.statusText}`)
    }
    
  } catch (err: any) {
    console.error('Error processing auth callback:', err)
    error.value = 'Failed to process authentication'
    isProcessing.value = false
    notifyParent('GOOGLE_AUTH_ERROR', { error: err.message })
  }
})

const notifyParent = (type: string, data: any) => {
  if (window.opener) {
    try {
      window.opener.postMessage({
        type,
        ...data
      }, window.location.origin)
    } catch (err) {
      console.error('Failed to notify parent window:', err)
    }
  }
}

const closeWindow = () => {
  if (window.opener) {
    window.close()
  } else {
    // If not opened as popup, redirect to main app
    navigateTo('/')
  }
}
</script>

<style scoped>
.auth-callback {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 20px;
}

.callback-container {
  text-align: center;
  max-width: 400px;
  width: 100%;
}

.processing, .error, .success {
  padding: 40px 20px;
  border-radius: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid var(--border-primary);
  border-top: 4px solid var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon, .success-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

h2 {
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 12px 0;
}

p {
  color: var(--text-secondary);
  font-size: 16px;
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.btn-close {
  background: var(--accent-primary);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: var(--accent-hover);
}

.error .btn-close {
  background: #dc3545;
}

.error .btn-close:hover {
  background: #c82333;
}
</style>
