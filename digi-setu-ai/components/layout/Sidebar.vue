<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo-section">
        <div class="logo-icon">
          <Icon name="lucide:cpu" :size="20" />
        </div>
        <h1 class="logo-text">Digi Setu</h1>
      </div>
      
      <button class="new-chat-btn">
        <Icon name="lucide:plus" :size="16" />
        New chat
      </button>
    </div>
    
    <nav class="sidebar-nav">
      <div class="nav-section">
        <h2 class="nav-title">Recents</h2>
        <div class="nav-items">
          <a href="#" class="nav-item active">
            <Icon name="lucide:message-circle" class="nav-icon" :size="16" />
            Ready to create with Digi Setu?
          </a>
          <a href="#" class="nav-item">
            <Icon name="lucide:message-circle" class="nav-icon" :size="16" />
            AI Learning Experience
          </a>
          <a href="#" class="nav-item">
            <Icon name="lucide:message-circle" class="nav-icon" :size="16" />
            Interactive Components
          </a>
        </div>
      </div>
    </nav>
    
    <div class="sidebar-footer">
      <LayoutThemeToggle />
      <div class="user-section">
        <UiAvatar initials="NK" variant="primary" size="sm" />
        <span class="user-name">Naveen Kumar</span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
// Sidebar logic
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 260px;
  height: 100vh;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-primary);
  display: flex;
  flex-direction: column;
  z-index: 50;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-primary);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: var(--accent-primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.new-chat-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
}

.nav-section {
  padding: 16px;
}

.nav-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 8px 0;
}

.nav-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--accent-primary);
  color: white;
}

.nav-icon {
  opacity: 0.7;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-primary);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  font-size: 14px;
  color: var(--text-secondary);
}
</style>