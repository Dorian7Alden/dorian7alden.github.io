<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const visible = ref(false)

function onScroll() {
  visible.value = window.scrollY > 300
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <Transition name="fab">
    <button
      v-show="visible"
      class="back-to-top"
      @click="scrollToTop"
      aria-label="返回顶部"
      title="返回顶部"
    >
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M10 17V4m0 0L5 9m5-5l5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
  </Transition>
</template>

<style scoped>
.back-to-top {
  position: fixed;
  bottom: 32px;
  right: 32px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--vp-c-border);
  background: var(--bg-elevated);
  color: var(--vp-c-text-2);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  transition: all var(--duration-normal) var(--ease-out);
}

.back-to-top:hover {
  color: var(--brand);
  border-color: var(--brand);
  box-shadow: var(--shadow-lg);
  transform: scale(1.08);
}

/* Transition */
.fab-enter-active {
  transition: all var(--duration-slow) var(--ease-out);
}

.fab-leave-active {
  transition: all var(--duration-normal) var(--ease-in-out);
}

.fab-enter-from,
.fab-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(8px);
}

@media (max-width: 768px) {
  .back-to-top {
    bottom: 20px;
    right: 20px;
    width: 40px;
    height: 40px;
  }
}
</style>
