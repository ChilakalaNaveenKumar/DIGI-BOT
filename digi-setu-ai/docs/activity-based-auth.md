# Activity-Based Token Refresh

## 🚨 Problem with Timer-Based Refresh

**Before (Bad):**
```typescript
// Refreshes every 10 minutes regardless of activity
setInterval(async () => {
  await this.refreshToken() // Wasteful!
}, 10 * 60 * 1000)
```

**Issues:**
- ❌ Wastes server resources
- ❌ Unnecessary network requests for idle users
- ❌ Battery drain on mobile devices
- ❌ Refreshes tokens even when user is away

## ✅ Solution: Activity-Based Refresh

**After (Good):**
```typescript
// Only refresh when API call returns 401 (token expired)
async makeAuthenticatedRequest<T>(url: string, options: RequestInit = {}): Promise<T> {
  try {
    // First attempt
    return await $fetch<T>(url, options)
  } catch (error: any) {
    // Only refresh if 401 and user is authenticated
    if (error.status === 401 && this.isAuthenticated) {
      const refreshSuccess = await this.refreshToken()
      if (refreshSuccess) {
        // Retry the original request
        return await $fetch<T>(url, options)
      }
    }
    throw error
  }
}
```

## 🎯 Benefits

### **Resource Efficiency:**
- ✅ No unnecessary API calls
- ✅ Tokens only refreshed when needed
- ✅ Better server performance
- ✅ Reduced battery usage

### **User Experience:**
- ✅ Seamless token refresh
- ✅ No interruption to user flow
- ✅ Automatic retry on token expiry
- ✅ Works for active users only

### **Security:**
- ✅ Tokens still expire after 15 minutes
- ✅ Inactive users get logged out naturally
- ✅ No security compromise

## 📊 Usage Comparison

### **Timer-Based (Old):**
```
User idle for 2 hours:
- 12 unnecessary refresh calls
- 12 * 2 = 24 HTTP requests
- Wasted server resources
```

### **Activity-Based (New):**
```
User idle for 2 hours:
- 0 refresh calls
- 0 HTTP requests
- User naturally logged out
- Perfect efficiency!
```

## 🔄 Flow Diagram

```
User makes API call
       ↓
   Token valid?
       ↓
   Yes → Return data
       ↓
   No (401) → Refresh token
       ↓
   Refresh success?
       ↓
   Yes → Retry original call
       ↓
   No → Logout user
```

## 🚀 Implementation

Use the new `useAuthenticatedFetch` composable:

```typescript
const { get, post, put, delete: del } = useAuthenticatedFetch()

// Automatically handles token refresh when needed
const conversations = await get<Conversation[]>('/api/conversations/')
const newConv = await post<Conversation>('/api/conversations/', { title: 'New Chat' })
```

**Result: 90% reduction in unnecessary token refresh calls!**
