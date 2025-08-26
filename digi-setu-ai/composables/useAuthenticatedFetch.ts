/**
 * Smart authenticated fetch composable
 * Automatically handles token refresh when needed (activity-based)
 */

export const useAuthenticatedFetch = () => {
  const authStore = useAuthStore()

  /**
   * Make an authenticated API request with automatic token refresh
   * Only refreshes token when API returns 401 (activity-based)
   */
  const authenticatedFetch = async <T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> => {
    return await authStore.makeAuthenticatedRequest<T>(url, options)
  }

  /**
   * Convenience methods for common HTTP verbs
   */
  const get = <T>(url: string, options: RequestInit = {}): Promise<T> => {
    return authenticatedFetch<T>(url, { ...options, method: 'GET' })
  }

  const post = <T>(url: string, body?: any, options: RequestInit = {}): Promise<T> => {
    return authenticatedFetch<T>(url, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined
    })
  }

  const put = <T>(url: string, body?: any, options: RequestInit = {}): Promise<T> => {
    return authenticatedFetch<T>(url, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined
    })
  }

  const del = <T>(url: string, options: RequestInit = {}): Promise<T> => {
    return authenticatedFetch<T>(url, { ...options, method: 'DELETE' })
  }

  return {
    authenticatedFetch,
    get,
    post,
    put,
    delete: del
  }
}
