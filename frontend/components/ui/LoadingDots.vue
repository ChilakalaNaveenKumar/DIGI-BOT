<template>
  <div class="loading-dots" :class="`loading-dots--${size}`">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg'
}

withDefaults(defineProps<Props>(), {
  size: 'md'
})
</script>

<style scoped>
.loading-dots {
  display: flex;
  gap: 4px;
  align-items: center;
}

.dot {
  background: var(--text-tertiary);
  border-radius: 50%;
  animation: loading-bounce 1.4s ease-in-out infinite both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
.dot:nth-child(3) { animation-delay: 0s; }

/* Sizes */
.loading-dots--sm .dot {
  width: 4px;
  height: 4px;
}

.loading-dots--md .dot {
  width: 6px;
  height: 6px;
}

.loading-dots--lg .dot {
  width: 8px;
  height: 8px;
}

@keyframes loading-bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
