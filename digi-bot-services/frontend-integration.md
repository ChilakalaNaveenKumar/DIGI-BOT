# Frontend Integration Guide

## How to Update Your Frontend to Use the Auth Service

### 1. Update GoogleSignInButton.vue

Replace the current Google Sign-In implementation with calls to your auth service:

```vue
<template>
  <div class="google-signin-container">
    <button 
      @click="handleGoogleSignIn" 
      :disabled="isLoading"
      class="google-signin-btn"
    >
      <div v-if="isLoading" class="loading-spinner"></div>
      <span v-else>{{ buttonText }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
const isLoading = ref(false)
const buttonText = ref('Sign in with Google')

// Auth service configuration
const AUTH_SERVICE_URL = 'http://localhost:8000'

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

const handleGoogleSignIn = async () => {
  isLoading.value = true
  buttonText.value = 'Signing in...'
  
  try {
    // Step 1: Get Google auth URL from your service
    const authUrlResponse = await $fetch(`${AUTH_SERVICE_URL}/auth/google/url`)
    
    // Step 2: Open Google OAuth popup
    const popup = window.open(
      authUrlResponse.auth_url,
      'google-auth',
      'width=500,height=600,scrollbars=yes,resizable=yes'
    )
    
    // Step 3: Listen for the callback
    const result = await waitForAuthCallback(popup)
    
    if (result.success) {
      // Step 4: Verify the credential with your service
      const authResponse: AuthResponse = await $fetch(`${AUTH_SERVICE_URL}/auth/google/verify`, {
        method: 'POST',
        body: {
          credential: result.credential
        }
      })
      
      // Step 5: Store the token and user info
      localStorage.setItem('access_token', authResponse.access_token)
      localStorage.setItem('user', JSON.stringify(authResponse.user))
      
      // Step 6: Emit success event
      emit('auth-success', authResponse.user)
      
      buttonText.value = `Welcome, ${authResponse.user.name}!`
    }
  } catch (error) {
    console.error('Authentication failed:', error)
    buttonText.value = 'Sign in failed'
    emit('auth-error', error)
  } finally {
    isLoading.value = false
    setTimeout(() => {
      buttonText.value = 'Sign in with Google'
    }, 3000)
  }
}

const waitForAuthCallback = (popup: Window): Promise<{success: boolean, credential?: string}> => {
  return new Promise((resolve) => {
    const checkClosed = setInterval(() => {
      if (popup.closed) {
        clearInterval(checkClosed)
        resolve({ success: false })
      }
    }, 1000)
    
    // Listen for postMessage from popup
    const messageHandler = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return
      
      if (event.data.type === 'GOOGLE_AUTH_SUCCESS') {
        clearInterval(checkClosed)
        popup.close()
        window.removeEventListener('message', messageHandler)
        resolve({ success: true, credential: event.data.credential })
      }
    }
    
    window.addEventListener('message', messageHandler)
  })
}

const emit = defineEmits<{
  'auth-success': [user: any]
  'auth-error': [error: any]
}>()
</script>
```

### 2. Create Auth Callback Page

Create `pages/auth/callback.vue`:

```vue
<template>
  <div class="auth-callback">
    <div v-if="isProcessing">
      <h2>Completing authentication...</h2>
      <div class="loading-spinner"></div>
    </div>
    <div v-else-if="error">
      <h2>Authentication Error</h2>
      <p>{{ error }}</p>
    </div>
    <div v-else>
      <h2>Authentication Successful</h2>
      <p>You can close this window.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const isProcessing = ref(true)
const error = ref('')

onMounted(async () => {
  const code = route.query.code as string
  const authError = route.query.error as string
  
  if (authError) {
    error.value = authError
    isProcessing.value = false
    return
  }
  
  if (!code) {
    error.value = 'No authorization code received'
    isProcessing.value = false
    return
  }
  
  try {
    // For now, just pass the code to parent window
    // In a full implementation, you'd exchange the code for tokens
    if (window.opener) {
      window.opener.postMessage({
        type: 'GOOGLE_AUTH_SUCCESS',
        credential: code  // This would be the actual credential/token
      }, window.location.origin)
      
      window.close()
    }
  } catch (err) {
    error.value = 'Failed to process authentication'
    console.error(err)
  } finally {
    isProcessing.value = false
  }
})
</script>
```

### 3. Update Your Environment

In your frontend's `.env` file, add:

```env
NUXT_PUBLIC_AUTH_SERVICE_URL=http://localhost:8000
```

## Usage

1. **Start the auth service:**
   ```bash
   cd digi-bot-services
   ./setup.sh
   source venv/bin/activate
   python main.py
   ```

2. **Start your frontend:**
   ```bash
   cd digi-setu-ai
   npm run dev
   ```

3. **The auth flow:**
   - User clicks "Sign in with Google" in your local frontend
   - Frontend calls your auth service at `localhost:8000`
   - Auth service redirects to Google OAuth (with HTTPS)
   - Google redirects back to your tunnel domain
   - Your auth service handles the callback and issues a JWT
   - Frontend stores the JWT and user info

## Benefits

✅ **Google OAuth works with HTTPS** (through tunnel)
✅ **Client secrets are secure** (on backend)  
✅ **Local development works** (frontend on localhost)
✅ **JWT tokens for API calls**
✅ **Same packages as main backend**
