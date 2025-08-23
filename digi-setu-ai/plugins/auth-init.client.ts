/**
 * Client-side plugin to initialize authentication state
 * This runs once when the app starts on the client side
 */

export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore()
  
  // Initialize authentication state
  await authStore.initialize()
  
  console.log('Auth store initialized:', {
    isAuthenticated: authStore.isAuthenticated,
    user: authStore.user?.email
  })
})
