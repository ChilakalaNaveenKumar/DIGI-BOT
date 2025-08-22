/**
 * Authentication middleware
 * Redirects unauthenticated users to the signin page
 */

export default defineNuxtRouteMiddleware((to, from) => {
  const { isAuthenticated } = useAuth()
  
  // Skip middleware on server-side rendering to avoid hydration issues
  if (process.server) return
  
  if (!isAuthenticated.value) {
    // Store the intended destination
    const intendedRoute = to.fullPath
    
    // Redirect to signin with return URL
    return navigateTo({
      path: '/auth/signin',
      query: { redirect: intendedRoute }
    })
  }
})
