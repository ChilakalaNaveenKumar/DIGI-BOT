<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <div class="header-content">
        <div class="brand-section">
          <div class="brand-logo">
            <Icon name="lucide:graduation-cap" class="logo-icon" />
            <span class="brand-name">Digi Setu AI</span>
          </div>
        </div>
        
        <div class="user-section">
          <div class="user-info">
            <div class="user-avatar" v-if="user?.picture">
              <img :src="user.picture" :alt="user.name" class="avatar-image" />
            </div>
            <div class="user-avatar" v-else>
              <Icon name="lucide:user" />
            </div>
            <div class="user-details">
              <span class="user-name">{{ user?.name || 'Welcome!' }}</span>
              <span class="user-email">{{ user?.email }}</span>
            </div>
          </div>
          <button @click="signOut" class="sign-out-btn">
            <Icon name="lucide:log-out" />
            Sign Out
          </button>
        </div>
      </div>
    </div>

    <div class="dashboard-main">
      <div class="welcome-section">
        <h1 class="welcome-title">Welcome to Digi Setu AI</h1>
        <p class="welcome-subtitle">Transform your static content into interactive learning experiences</p>
      </div>

      <div class="quick-actions">
        <NuxtLink to="/chat" class="action-card action-card--link">
          <div class="card-icon">
            <Icon name="lucide:message-circle" />
          </div>
          <h3 class="card-title">Start Chatting</h3>
          <p class="card-description">Experience AI-powered conversations with advanced markdown support</p>
          <div class="card-button">Try Chat</div>
        </NuxtLink>

        <div class="action-card">
          <div class="card-icon">
            <Icon name="lucide:plus-circle" />
          </div>
          <h3 class="card-title">Create New Lesson</h3>
          <p class="card-description">Start building interactive educational content</p>
          <button class="card-button">Get Started</button>
        </div>

        <div class="action-card">
          <div class="card-icon">
            <Icon name="lucide:book-open" />
          </div>
          <h3 class="card-title">My Lessons</h3>
          <p class="card-description">View and manage your existing lessons</p>
          <button class="card-button">View Lessons</button>
        </div>

        <div class="action-card">
          <div class="card-icon">
            <Icon name="lucide:bar-chart" />
          </div>
          <h3 class="card-title">Analytics</h3>
          <p class="card-description">Track student engagement and performance</p>
          <button class="card-button">View Analytics</button>
        </div>
      </div>

      <div class="recent-activity">
        <h2 class="section-title">Recent Activity</h2>
        <div class="activity-list">
          <div class="activity-item">
            <div class="activity-icon">
              <Icon name="lucide:leaf" />
            </div>
            <div class="activity-content">
              <h4 class="activity-title">Photosynthesis Lesson</h4>
              <p class="activity-description">Interactive biology lesson with process diagrams</p>
              <span class="activity-time">2 hours ago</span>
            </div>
            <button class="activity-action">Edit</button>
          </div>

          <div class="activity-item">
            <div class="activity-icon">
              <Icon name="lucide:calculator" />
            </div>
            <div class="activity-content">
              <h4 class="activity-title">Fractions Practice</h4>
              <p class="activity-description">Math lesson with interactive quizzes</p>
              <span class="activity-time">1 day ago</span>
            </div>
            <button class="activity-action">Edit</button>
          </div>

          <div class="activity-item">
            <div class="activity-icon">
              <Icon name="lucide:clock" />
            </div>
            <div class="activity-content">
              <h4 class="activity-title">WWII Timeline</h4>
              <p class="activity-description">History lesson with interactive timeline</p>
              <span class="activity-time">3 days ago</span>
            </div>
            <button class="activity-action">Edit</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Set page meta
definePageMeta({
  layout: 'chat',
  middleware: 'auth'
})

// SEO
useHead({
  title: 'Dashboard - Digi Setu AI',
  meta: [
    { name: 'description', content: 'Your Digi Setu AI dashboard - create and manage interactive learning experiences.' }
  ]
})

// User data interface
interface User {
  picture?: string
  name?: string
  email?: string
}

const user = ref<User | null>(null)

// Load user data on mount
onMounted(() => {
  if (process.client) {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
        console.log('Loaded user data:', user.value)
      } catch (error) {
        console.error('Error parsing user data:', error)
        // Redirect to sign-in if user data is corrupted
        navigateTo('/auth/signin')
      }
    } else {
      // No user data found, redirect to sign-in
      navigateTo('/auth/signin')
    }
  }
})

// Sign out function
const signOut = async () => {
  try {
    console.log('Signing out...')
    
    // Clear user data from localStorage
    if (process.client) {
      localStorage.removeItem('user')
    }
    
    // Clear user state
    user.value = null
    
    // Here you would also revoke Google tokens if needed
    // await googleSignOut() // if using Google Sign-In library
    
    // Redirect back to sign-in page
    await navigateTo('/auth/signin')
  } catch (error) {
    console.error('Sign out error:', error)
  }
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: var(--bg-primary);
}

.dashboard-header {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-primary);
  padding: 1rem 2rem;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand-section {
  display: flex;
  align-items: center;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  width: 2rem;
  height: 2rem;
  color: var(--accent-primary);
}

.brand-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.user-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 2.5rem;
  height: 2.5rem;
  background: var(--accent-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.user-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.user-email {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.sign-out-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid var(--border-primary);
  border-radius: 0.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.sign-out-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.dashboard-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.welcome-section {
  text-align: center;
  margin-bottom: 3rem;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
}

.welcome-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin: 0;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.action-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: 1rem;
  padding: 2rem;
  text-align: center;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-secondary);
}

.card-icon {
  width: 3rem;
  height: 3rem;
  background: var(--accent-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem auto;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.card-description {
  color: var(--text-secondary);
  margin: 0 0 1.5rem 0;
  line-height: 1.5;
}

.card-button {
  padding: 0.75rem 1.5rem;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.card-button:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.recent-activity {
  margin-top: 3rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: 0.75rem;
  transition: all 0.2s ease;
}

.activity-item:hover {
  background: var(--bg-hover);
  border-color: var(--border-secondary);
}

.activity-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: var(--accent-primary);
  color: white;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
}

.activity-description {
  color: var(--text-secondary);
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
}

.activity-time {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.activity-action {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid var(--border-primary);
  border-radius: 0.375rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.activity-action:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-header {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .dashboard-main {
    padding: 1rem;
  }
  
  .welcome-title {
    font-size: 2rem;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
  
  .activity-item {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }
}

.action-card--link {
  text-decoration: none;
  color: inherit;
}
</style>