/**
 * Enhanced Authentication Composable with Secure Cookies
 * HIPAA-compliant authentication with automatic token refresh
 */

import { ref, computed, onMounted, onUnmounted, getCurrentInstance } from 'vue'

export interface User {
  id: string
  email: string
  name: string
  picture?: string
  verified_email: boolean
}

export interface AuthStatus {
  authenticated: boolean
  user: User | null
  loading: boolean
  error: string | null
}

export const useEnhancedAuth = () => {
  // Reactive state
  const authStatus = ref<AuthStatus>({
    authenticated: false,
    user: null,
    loading: true,
    error: null
  })

  const refreshTimer = ref<NodeJS.Timeout | null>(null)

  // Computed properties
  const isAuthenticated = computed(() => authStatus.value.authenticated)
  const user = computed(() => authStatus.value.user)
  const isLoading = computed(() => authStatus.value.loading)
  const error = computed(() => authStatus.value.error)

  // Check authentication status
  const checkAuthStatus = async (): Promise<boolean> => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/status', {
        method: 'GET',
        credentials: 'include', // Include httpOnly cookies
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        
        authStatus.value = {
          authenticated: data.authenticated,
          user: data.user,
          loading: false,
          error: null
        }

        return data.authenticated
      } else {
        authStatus.value = {
          authenticated: false,
          user: null,
          loading: false,
          error: null
        }
        return false
      }
    } catch (err) {
      console.error('Auth status check failed:', err)
      authStatus.value = {
        authenticated: false,
        user: null,
        loading: false,
        error: err instanceof Error ? err.message : 'Authentication check failed'
      }
      return false
    }
  }

  // Refresh access token
  const refreshToken = async (): Promise<boolean> => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Token refreshed successfully')
        
        // Update auth status
        await checkAuthStatus()
        return true
      } else {
        console.log('Token refresh failed, user needs to re-authenticate')
        await logout()
        return false
      }
    } catch (err) {
      console.error('Token refresh error:', err)
      await logout()
      return false
    }
  }

  // Login with Google (enhanced)
  const loginWithGoogle = async (credential: string): Promise<boolean> => {
    try {
      authStatus.value.loading = true
      authStatus.value.error = null

      const response = await fetch('http://localhost:8000/api/auth/google/verify', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ credential })
      })

      if (response.ok) {
        const data = await response.json()
        
        if (data.success) {
          authStatus.value = {
            authenticated: true,
            user: data.user,
            loading: false,
            error: null
          }

          // Set up automatic token refresh
          setupTokenRefresh()
          
          console.log('Enhanced authentication successful')
          return true
        }
      }

      throw new Error('Authentication failed')
      
    } catch (err) {
      authStatus.value = {
        authenticated: false,
        user: null,
        loading: false,
        error: err instanceof Error ? err.message : 'Login failed'
      }
      return false
    }
  }

  // Secure logout
  const logout = async (): Promise<void> => {
    try {
      // Clear refresh timer
      if (refreshTimer.value) {
        clearInterval(refreshTimer.value)
        refreshTimer.value = null
      }

      // Call logout endpoint to clear server-side sessions
      await fetch('http://localhost:8000/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      // Update local state
      authStatus.value = {
        authenticated: false,
        user: null,
        loading: false,
        error: null
      }

      // Redirect to home page
      if (process.client) {
        await navigateTo('/')
      }

      console.log('Secure logout completed')
    } catch (err) {
      console.error('Logout error:', err)
      
      // Even if logout request fails, clear local state
      authStatus.value = {
        authenticated: false,
        user: null,
        loading: false,
        error: null
      }
    }
  }

  // Get authentication headers (for API calls)
  const getAuthHeaders = (): Record<string, string> => {
    // With httpOnly cookies, we don't need to manually add Authorization headers
    // The browser automatically includes cookies with requests
    return {
      'Content-Type': 'application/json'
    }
  }

  // Make authenticated API call
  const authenticatedFetch = async (
    url: string, 
    options: RequestInit = {}
  ): Promise<Response> => {
    const response = await fetch(url, {
      ...options,
      credentials: 'include', // Always include cookies
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    })

    // Handle token expiration
    if (response.status === 401) {
      console.log('Access token expired, attempting refresh...')
      
      const refreshSuccess = await refreshToken()
      if (refreshSuccess) {
        // Retry the original request
        return fetch(url, {
          ...options,
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            ...options.headers
          }
        })
      } else {
        // Refresh failed, redirect to login
        await logout()
        throw new Error('Authentication required')
      }
    }

    return response
  }

  // Setup automatic token refresh (every 10 minutes)
  const setupTokenRefresh = () => {
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
    }

    refreshTimer.value = setInterval(async () => {
      if (authStatus.value.authenticated) {
        console.log('Refreshing access token...')
        await refreshToken()
      }
    }, 10 * 60 * 1000) // 10 minutes
  }

  // Revoke all sessions (security feature)
  const revokeAllSessions = async (): Promise<boolean> => {
    try {
      const response = await authenticatedFetch('http://localhost:8000/api/auth/revoke-all-sessions', {
        method: 'POST'
      })

      if (response.ok) {
        const data = await response.json()
        console.log(`Revoked ${data.revoked_sessions} sessions`)
        
        // This will log out the current session too
        await logout()
        return true
      }
      
      return false
    } catch (err) {
      console.error('Failed to revoke sessions:', err)
      return false
    }
  }

  // Initialize authentication on mount (only if we're in a component context)
  if (process.client && getCurrentInstance()) {
    onMounted(async () => {
      console.log('Initializing enhanced authentication...')
      
      const isAuth = await checkAuthStatus()
      if (isAuth) {
        setupTokenRefresh()
      }
    })

    // Cleanup on unmount
    onUnmounted(() => {
      if (refreshTimer.value) {
        clearInterval(refreshTimer.value)
      }
    })
  } else if (process.client) {
    // If not in component context, initialize immediately
    checkAuthStatus().then((isAuth) => {
      if (isAuth) {
        setupTokenRefresh()
      }
    })
  }

  return {
    // State
    isAuthenticated,
    user,
    isLoading,
    error,
    
    // Methods
    checkAuthStatus,
    loginWithGoogle,
    logout,
    refreshToken,
    getAuthHeaders,
    authenticatedFetch,
    revokeAllSessions
  }
}
