/**
 * Centralized Authentication Store using Pinia
 * Single source of truth for authentication state across the entire application
 */

import { defineStore } from 'pinia'
import type { User } from '~/types'

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  isInitialized: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    isInitialized: false
  }),

  getters: {
    // Computed properties based on state
    userName: (state) => state.user?.name || '',
    userEmail: (state) => state.user?.email || '',
    isVerified: (state) => state.user?.verified_email || false,
    
    // Helper to check if we should show loading states
    shouldShowLoading: (state) => state.isLoading && !state.isInitialized
  },

  actions: {
    /**
     * Initialize authentication state on app startup
     * This should be called once when the app starts
     */
    async initialize() {
      if (this.isInitialized) return
      
      this.isLoading = true
      this.error = null
      
      try {
        await this.checkAuthStatus()
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        this.error = 'Failed to initialize authentication'
      } finally {
        this.isInitialized = true
        this.isLoading = false
      }
    },

    /**
     * Check current authentication status with the server
     */
    async checkAuthStatus(): Promise<boolean> {
      try {
        const response = await $fetch<{
          authenticated: boolean
          user: User | null
        }>('http://localhost:8000/api/auth/status', {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        })

        const wasAuthenticated = this.isAuthenticated
        this.isAuthenticated = response.authenticated
        this.user = response.user
        this.error = null

        // Debug logging for auth state changes
        if (wasAuthenticated !== response.authenticated) {
          console.log('🔐 Auth state changed:', {
            from: wasAuthenticated,
            to: response.authenticated,
            user: response.user?.name || 'none'
          })
        }

        return response.authenticated
      } catch (error: any) {
        console.error('Auth status check failed:', error)
        this.isAuthenticated = false
        this.user = null
        this.error = 'Authentication check failed'
        return false
      }
    },

    /**
     * Login with Google OAuth
     */
    async loginWithGoogle(credential: string): Promise<boolean> {
      this.isLoading = true
      this.error = null

      try {
        const response = await $fetch<{
          success: boolean
          user: User
        }>('http://localhost:8000/api/auth/google/verify', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          },
          body: { credential }
        })

        if (response.success && response.user) {
          this.isAuthenticated = true
          this.user = response.user
          this.error = null
          
          // Set up token refresh
          this.setupTokenRefresh()
          
          return true
        }

        throw new Error('Login failed')
      } catch (error: any) {
        console.error('Google login failed:', error)
        this.error = error.message || 'Login failed'
        this.isAuthenticated = false
        this.user = null
        return false
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Logout user
     */
    async logout(): Promise<void> {
      try {
        // Clear refresh timer
        this.clearTokenRefresh()

        // Call logout endpoint
        await $fetch('http://localhost:8000/api/auth/logout', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        })
      } catch (error) {
        console.error('Logout request failed:', error)
      } finally {
        // Always clear local state regardless of server response
        this.isAuthenticated = false
        this.user = null
        this.error = null
      }
    },

    /**
     * Refresh access token
     */
    async refreshToken(): Promise<boolean> {
      try {
        const response = await $fetch('http://localhost:8000/api/auth/refresh', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        })

        if (response) {
          console.log('Token refreshed successfully')
          // Re-check auth status to update user data
          await this.checkAuthStatus()
          return true
        }

        return false
      } catch (error) {
        console.error('Token refresh failed:', error)
        await this.logout()
        return false
      }
    },

    /**
     * Set authentication state (for external auth flows)
     */
    setAuthenticated(user: User) {
      this.isAuthenticated = true
      this.user = user
      this.error = null
      this.setupTokenRefresh()
    },

    /**
     * Clear error state
     */
    clearError() {
      this.error = null
    },

    /**
     * Setup automatic token refresh
     */
    setupTokenRefresh() {
      // Clear any existing timer
      this.clearTokenRefresh()
      
      // Set up refresh every 10 minutes
      if (import.meta.client) {
        refreshTimer = setInterval(async () => {
          if (this.isAuthenticated) {
            await this.refreshToken()
          }
        }, 10 * 60 * 1000) // 10 minutes
      }
    },

    /**
     * Clear token refresh timer
     */
    clearTokenRefresh() {
      if (refreshTimer) {
        clearInterval(refreshTimer)
        refreshTimer = null
      }
    }
  }
})

// Global refresh timer (outside of reactive state)
let refreshTimer: NodeJS.Timeout | null = null
