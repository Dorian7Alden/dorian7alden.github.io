<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { withBase, useData } from 'vitepress'
import { useCategories } from '../../composables/useCategories'

const { theme } = useData()
const blog = theme.value.blog
const author = blog.author

const { total: totalPosts, categories } = useCategories()
const totalCategories = categories.length

const isVisible = ref(false)
let observer: IntersectionObserver | null = null

onMounted(() => {
  const target = document.getElementById('personal-card')
  if (!target) return

  observer = new IntersectionObserver(
    ([entry]) => {
      isVisible.value = !entry.isIntersecting
    },
    { threshold: 0 }
  )
  observer.observe(target)
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<template>
  <Transition name="float-sidebar">
    <aside v-if="isVisible" class="floating-sidebar">
      <div class="float-avatar">
        <img :src="withBase(author.avatar)" :alt="author.name" />
      </div>
      <div class="float-name">{{ author.name }}</div>
      <div class="float-bio">{{ author.bio }}</div>
      <div class="float-stats">
        <div class="float-stat">
          <span class="float-stat-num">{{ totalPosts }}</span>
          <span class="float-stat-label">文章</span>
        </div>
        <div class="float-stat">
          <span class="float-stat-num">{{ totalCategories }}</span>
          <span class="float-stat-label">分类</span>
        </div>
      </div>
    </aside>
  </Transition>
</template>

<style scoped>
.floating-sidebar {
  position: fixed;
  right: max(24px, calc((100vw - var(--page-width)) / 2 + 24px));
  top: 96px;
  width: 200px;
  z-index: 20;
  padding: 22px 16px;
  text-align: center;
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border: 1px solid var(--vp-c-border);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(14px);
  overflow: hidden;
}

.floating-sidebar::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 0%, var(--brand-soft), transparent 60%);
  pointer-events: none;
}

.float-avatar {
  width: 56px;
  height: 56px;
  padding: 3px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--brand-light), var(--accent));
  margin: 0 auto 10px;
}

.float-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: 11px;
  border: 2px solid var(--bg-elevated);
}

.float-name {
  color: var(--text-heading);
  font-size: 0.92rem;
  font-weight: 750;
  letter-spacing: -0.02em;
}

.float-bio {
  margin-top: 3px;
  color: var(--vp-c-text-2);
  font-size: 0.75rem;
  line-height: 1.4;
}

.float-stats {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--vp-c-divider);
}

.float-stat {
  text-align: center;
}

.float-stat-num {
  display: block;
  color: var(--brand);
  font-size: 1.05rem;
  font-weight: 850;
  line-height: 1;
  letter-spacing: -0.03em;
}

.float-stat-label {
  display: block;
  margin-top: 2px;
  color: var(--vp-c-text-3);
  font-size: 0.68rem;
  font-weight: 600;
}

/* Transitions */

.float-sidebar-enter-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.float-sidebar-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.float-sidebar-enter-from,
.float-sidebar-leave-to {
  opacity: 0;
  transform: translateX(40px);
}

/* Hide on mobile */

@media (max-width: 768px) {
  .floating-sidebar {
    display: none;
  }
}
</style>
