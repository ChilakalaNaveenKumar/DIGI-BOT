/**
 * Authentication middleware
 * Redirects unauthenticated users to the signin page
 */

export default defineNuxtRouteMiddleware(async (to, from) => {
  // Skip middleware on server-side rendering to avoid hydration issues
  if (import.meta.server) return
  
  const authStore = useAuthStore()
  
  // Wait for auth store to be initialized
  if (!authStore.isInitialized) {
    await authStore.initialize()
  }
  
  if (!authStore.isAuthenticated) {
    // Store the intended destination
    const intendedRoute = to.fullPath
    
    // Redirect to signin with return URL
    return navigateTo({
      path: '/signin',
      query: { redirect: intendedRoute }
    })
  }
})
