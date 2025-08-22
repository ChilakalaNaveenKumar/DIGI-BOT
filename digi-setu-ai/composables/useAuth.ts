/**
 * Authentication composable using cookies
 * Provides reactive auth state and methods for login/logout
 */

export interface User {
  id: string
  email: string
  name: string
  picture: string
  verified_email: boolean
}

export const useAuth = () => {
  // Access token cookie
  const tokenCookie = useCookie('access_token', {
    default: () => '',
    maxAge: 60 * 60 * 24 * 7, // 7 days
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    httpOnly: false // We need client-side access for API calls
  })
  
  // User info cookie
  const userCookie = useCookie<User | null>('user', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 7, // 7 days
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    httpOnly: false,
    serializer: {
      read: (value: string) => {
        try {
          return JSON.parse(value)
        } catch {
          return null
        }
      },
      write: (value: any) => JSON.stringify(value)
    }
  })
  
  // Computed reactive state
  const isAuthenticated = computed(() => {
    return !!(tokenCookie.value && userCookie.value)
  })
  
  const user = computed(() => userCookie.value)
  const token = computed(() => tokenCookie.value)
  
  // Methods
  const login = (accessToken: string, userData: User) => {
    tokenCookie.value = accessToken
    userCookie.value = userData
  }
  
  const logout = () => {
    tokenCookie.value = ''
    userCookie.value = null
    
    // Redirect to home page after logout
    if (process.client) {
      navigateTo('/')
    }
  }
  
  const getAuthHeaders = () => {
    if (!tokenCookie.value) return {}
    
    return {
      'Authorization': `Bearer ${tokenCookie.value}`
    }
  }
  
  // Check if user has specific role/permission
  const hasRole = (role: string) => {
    // Extend this based on your role system
    return user.value?.verified_email || false
  }
  
  return {
    // State
    isAuthenticated,
    user,
    token,
    
    // Methods
    login,
    logout,
    getAuthHeaders,
    hasRole
  }
}
