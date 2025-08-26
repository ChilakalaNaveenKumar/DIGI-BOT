import { createPersistedState } from 'pinia-plugin-persistedstate'

export default defineNuxtPlugin((nuxtApp) => {
  // @ts-ignore - Pinia is available in nuxtApp
  nuxtApp.$pinia.use(createPersistedState())
})
