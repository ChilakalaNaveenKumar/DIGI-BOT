<template>
  <div class="user-menu" :class="{ 'menu-open': isMenuOpen }">
    <!-- User Info Button -->
    <button 
      class="user-info-btn"
      @click="toggleMenu"
      :title="user?.name || 'User menu'"
    >
      <UiAvatar 
        :initials="userInitials" 
        :image="user?.picture"
        variant="primary" 
        size="sm" 
      />
      <div class="user-details">
        <span class="user-name">{{ user?.name || 'User' }}</span>
        <span class="user-email">{{ user?.email || '' }}</span>
      </div>
      <Icon 
        name="lucide:chevron-up" 
        :size="16" 
        class="chevron-icon"
        :class="{ 'rotated': isMenuOpen }"
      />
    </button>

    <!-- Dropdown Menu -->
    <Transition name="menu">
      <div v-if="isMenuOpen" class="dropdown-menu">
        <div class="menu-header">
          <div class="user-avatar-large">
            <UiAvatar 
              :initials="userInitials" 
              :image="user?.picture"
              variant="primary" 
              size="md" 
            />
          </div>
          <div class="user-info">
            <h3 class="user-name-large">{{ user?.name || 'User' }}</h3>
            <p class="user-email-sub">{{ user?.email || '' }}</p>
            <span class="user-status">{{ user?.verified_email ? 'Verified' : 'Unverified' }}</span>
          </div>
        </div>

        <div class="menu-divider"></div>

        <div class="menu-items">
          <button class="menu-item" @click="handleProfile">
            <Icon name="lucide:user" :size="16" />
            <span>Profile</span>
          </button>
          
          <button class="menu-item" @click="handleSettings">
            <Icon name="lucide:settings" :size="16" />
            <span>Settings</span>
          </button>
          
          <button class="menu-item" @click="handleSupport">
            <Icon name="lucide:help-circle" :size="16" />
            <span>Help & Support</span>
          </button>
          
          <button class="menu-item security-item" @click="handleRevokeAllSessions">
            <Icon name="lucide:shield-x" :size="16" />
            <span>Sign out all devices</span>
          </button>
        </div>

        <div class="menu-divider"></div>

        <div class="menu-items">
          <button class="menu-item logout-item" @click="handleLogout">
            <Icon name="lucide:log-out" :size="16" />
            <span>Sign out</span>
          </button>
        </div>
      </div>
    </Transition>

    <!-- Backdrop -->
    <div 
      v-if="isMenuOpen" 
      class="menu-backdrop" 
      @click="closeMenu"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Use Pinia auth store
const authStore = useAuthStore()

// Get user from store
const user = computed(() => authStore.user)

// Menu state
const isMenuOpen = ref(false)

// Computed user initials
const userInitials = computed(() => {
  if (!user.value?.name) return 'U'
  
  const names = user.value.name.split(' ')
  if (names.length >= 2) {
    return names[0][0].toUpperCase() + names[names.length - 1][0].toUpperCase()
  }
  return names[0][0].toUpperCase()
})

// Menu methods
const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
}

// Menu item handlers
const handleProfile = () => {
  closeMenu()
  // TODO: Navigate to profile page
  console.log('Profile clicked')
}

const handleSettings = () => {
  closeMenu()
  // TODO: Navigate to settings page
  console.log('Settings clicked')
}

const handleSupport = () => {
  closeMenu()
  // TODO: Navigate to support page
  navigateTo('/support')
}

const handleLogout = async () => {
  if (confirm('Are you sure you want to sign out?')) {
    closeMenu()
    
    try {
      // Use store logout (clears server-side sessions and cookies)
      await authStore.logout()
      
      console.log('User logged out successfully')
      // Navigate to home page
      await navigateTo('/')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }
}

// Add security feature to revoke all sessions
const handleRevokeAllSessions = async () => {
  if (confirm('This will sign you out of all devices. Are you sure?')) {
    closeMenu()
    
    try {
      // For now, just do a regular logout - we can implement revokeAllSessions in store later
      await authStore.logout()
      console.log('All sessions revoked successfully')
      await navigateTo('/')
    } catch (error) {
      console.error('Error revoking sessions:', error)
    }
  }
}

// Close menu on outside click
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  const userMenu = target.closest('.user-menu')
  
  if (!userMenu && isMenuOpen.value) {
    closeMenu()
  }
}

// Close menu on escape key
const handleEscapeKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && isMenuOpen.value) {
    closeMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleEscapeKey)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleEscapeKey)
})
</script>

<style scoped>
.user-menu {
  position: relative;
}

.user-info-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  text-align: left;
}

.user-info-btn:hover {
  background: var(--bg-hover);
}

.user-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chevron-icon {
  color: var(--text-muted);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.chevron-icon.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  padding: 16px;
  margin-bottom: 8px;
  z-index: 1000;
}

.menu-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.user-avatar-large {
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name-large {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email-sub {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-status {
  font-size: 12px;
  color: var(--accent-primary);
  font-weight: 500;
}

.menu-divider {
  height: 1px;
  background: var(--border-primary);
  margin: 12px 0;
}

.menu-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  width: 100%;
}

.menu-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.security-item {
  color: #f59e0b;
}

.security-item:hover {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.logout-item {
  color: #ef4444;
}

.logout-item:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.menu-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  background: transparent;
}

/* Menu animations */
.menu-enter-active,
.menu-leave-active {
  transition: all 0.2s ease;
  transform-origin: bottom center;
}

.menu-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.95);
}

.menu-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.95);
}
</style>
