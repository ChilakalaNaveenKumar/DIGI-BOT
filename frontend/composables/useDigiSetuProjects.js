/**
 * Digi Setu Projects Composable
 * 
 * Manages project state, CRUD operations, and collaboration features.
 */

import { ref, computed, watch } from 'vue'

// Global project state
const projects = ref([])
const currentProject = ref(null)
const currentProjectId = ref(null)
const isLoading = ref(false)
const error = ref(null)

// Mock data for development (will be replaced with API calls)
const mockProjects = [
  {
    id: 1,
    name: "AI Research",
    description: "Research project on AI capabilities and limitations",
    slug: "ai-research",
    visibility: "private",
    color: "#2563eb",
    icon: "brain",
    conversation_count: 15,
    member_count: 3,
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-20T15:30:00Z",
    owner_id: 1
  },
  {
    id: 2,
    name: "Content Creation",
    description: "AI-assisted content creation and optimization",
    slug: "content-creation",
    visibility: "team",
    color: "#10b981",
    icon: "edit",
    conversation_count: 8,
    member_count: 2,
    created_at: "2024-01-10T09:00:00Z",
    updated_at: "2024-01-18T14:20:00Z",
    owner_id: 1
  },
  {
    id: 3,
    name: "Code Analysis",
    description: "Automated code review and optimization suggestions",
    slug: "code-analysis",
    visibility: "private",
    color: "#f59e0b",
    icon: "code",
    conversation_count: 22,
    member_count: 1,
    created_at: "2024-01-05T08:00:00Z",
    updated_at: "2024-01-19T16:45:00Z",
    owner_id: 1
  }
]

export const useDigiSetuProjects = () => {
  // Computed properties
  const activeProjects = computed(() => {
    return projects.value.filter(project => project.visibility !== 'deleted')
  })
  
  const recentProjects = computed(() => {
    return [...activeProjects.value]
      .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
      .slice(0, 5)
  })
  
  const projectsByVisibility = computed(() => {
    const grouped = {
      private: [],
      team: [],
      public: []
    }
    
    activeProjects.value.forEach(project => {
      if (grouped[project.visibility]) {
        grouped[project.visibility].push(project)
      }
    })
    
    return grouped
  })
  
  // Methods
  const loadProjects = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      // TODO: Replace with actual API call
      // const response = await $fetch('/api/v1/projects')
      // projects.value = response.data
      
      // Mock implementation
      await new Promise(resolve => setTimeout(resolve, 500))
      projects.value = [...mockProjects]
      
      console.log('📁 Projects loaded successfully', projects.value.length)
    } catch (err) {
      error.value = err.message || 'Failed to load projects'
      console.error('Failed to load projects:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  const createProject = async (projectData) => {
    isLoading.value = true
    error.value = null
    
    try {
      // TODO: Replace with actual API call
      // const response = await $fetch('/api/v1/projects', {
      //   method: 'POST',
      //   body: projectData
      // })
      
      // Mock implementation
      await new Promise(resolve => setTimeout(resolve, 300))
      
      const newProject = {
        id: Date.now(),
        ...projectData,
        slug: projectData.name.toLowerCase().replace(/\s+/g, '-'),
        conversation_count: 0,
        member_count: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        owner_id: 1
      }
      
      projects.value.unshift(newProject)
      
      console.log('✅ Project created successfully:', newProject.name)
      return newProject
    } catch (err) {
      error.value = err.message || 'Failed to create project'
      console.error('Failed to create project:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const updateProject = async (projectId, updates) => {
    isLoading.value = true
    error.value = null
    
    try {
      // TODO: Replace with actual API call
      // const response = await $fetch(`/api/v1/projects/${projectId}`, {
      //   method: 'PUT',
      //   body: updates
      // })
      
      // Mock implementation
      await new Promise(resolve => setTimeout(resolve, 300))
      
      const projectIndex = projects.value.findIndex(p => p.id === projectId)
      if (projectIndex !== -1) {
        projects.value[projectIndex] = {
          ...projects.value[projectIndex],
          ...updates,
          updated_at: new Date().toISOString()
        }
        
        // Update current project if it's the one being updated
        if (currentProject.value?.id === projectId) {
          currentProject.value = projects.value[projectIndex]
        }
      }
      
      console.log('✅ Project updated successfully:', projectId)
    } catch (err) {
      error.value = err.message || 'Failed to update project'
      console.error('Failed to update project:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const deleteProject = async (projectId) => {
    isLoading.value = true
    error.value = null
    
    try {
      // TODO: Replace with actual API call
      // await $fetch(`/api/v1/projects/${projectId}`, {
      //   method: 'DELETE'
      // })
      
      // Mock implementation
      await new Promise(resolve => setTimeout(resolve, 300))
      
      projects.value = projects.value.filter(p => p.id !== projectId)
      
      // Clear current project if it was deleted
      if (currentProject.value?.id === projectId) {
        currentProject.value = null
        currentProjectId.value = null
      }
      
      console.log('🗑️ Project deleted successfully:', projectId)
    } catch (err) {
      error.value = err.message || 'Failed to delete project'
      console.error('Failed to delete project:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const selectProject = (project) => {
    if (project && typeof project === 'object') {
      currentProject.value = project
      currentProjectId.value = project.id
      
      // Save to localStorage
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('digi-setu-current-project', JSON.stringify({
          id: project.id,
          name: project.name,
          slug: project.slug
        }))
      }
      
      console.log('📁 Project selected:', project.name)
    } else {
      currentProject.value = null
      currentProjectId.value = null
      
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem('digi-setu-current-project')
      }
    }
  }
  
  const getProjectById = (projectId) => {
    return projects.value.find(p => p.id === projectId)
  }
  
  const getProjectBySlug = (slug) => {
    return projects.value.find(p => p.slug === slug)
  }
  
  const searchProjects = (query) => {
    if (!query || query.trim() === '') {
      return activeProjects.value
    }
    
    const searchTerm = query.toLowerCase().trim()
    return activeProjects.value.filter(project => 
      project.name.toLowerCase().includes(searchTerm) ||
      project.description?.toLowerCase().includes(searchTerm) ||
      project.slug.toLowerCase().includes(searchTerm)
    )
  }
  
  const getProjectStats = (projectId) => {
    const project = getProjectById(projectId)
    if (!project) return null
    
    return {
      conversations: project.conversation_count || 0,
      members: project.member_count || 0,
      created: project.created_at,
      lastActivity: project.updated_at
    }
  }
  
  // Load saved project on initialization
  const loadSavedProject = () => {
    if (typeof localStorage !== 'undefined') {
      try {
        const saved = localStorage.getItem('digi-setu-current-project')
        if (saved) {
          const projectData = JSON.parse(saved)
          const project = getProjectById(projectData.id)
          if (project) {
            selectProject(project)
          }
        }
      } catch (err) {
        console.warn('Failed to load saved project:', err)
      }
    }
  }
  
  // Watch for project changes
  watch(currentProjectId, (newId) => {
    if (newId) {
      const project = getProjectById(newId)
      if (project && project !== currentProject.value) {
        currentProject.value = project
      }
    }
  })
  
  // Initialize projects if empty
  if (projects.value.length === 0) {
    loadProjects()
  }
  
  // Load saved project
  loadSavedProject()
  
  return {
    // State
    projects: readonly(projects),
    currentProject: readonly(currentProject),
    currentProjectId: readonly(currentProjectId),
    isLoading: readonly(isLoading),
    error: readonly(error),
    
    // Computed
    activeProjects,
    recentProjects,
    projectsByVisibility,
    
    // Methods
    loadProjects,
    createProject,
    updateProject,
    deleteProject,
    selectProject,
    getProjectById,
    getProjectBySlug,
    searchProjects,
    getProjectStats,
    loadSavedProject
  }
}
