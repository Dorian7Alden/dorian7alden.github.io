<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Category {
  name: string
  count: number
}

const modules = import.meta.glob('/content/categories.json', { eager: true })
const jsonModule = modules['/content/categories.json'] as { default: { total: number; categories: Category[] } }
const totalPosts = jsonModule.default.total
const totalCategories = jsonModule.default.categories.length

const displayPosts = ref(0)
const displayCats = ref(0)

onMounted(() => {
  const duration = 1200
  const steps = 40
  let step = 0

  const timer = setInterval(() => {
    step++
    const progress = step / steps
    const eased = 1 - Math.pow(1 - progress, 3)
    displayPosts.value = Math.round(eased * totalPosts)
    displayCats.value = Math.round(eased * totalCategories)
    if (step >= steps) clearInterval(timer)
  }, duration / steps)
})
</script>

<template>
  <section class="hero">
    <div class="hero-bg">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
    </div>
    <div class="hero-content">
      <div class="hero-avatar">
        <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="40" cy="40" r="40" fill="var(--brand-soft)"/>
          <circle cx="40" cy="30" r="14" fill="var(--brand)" opacity="0.6"/>
          <ellipse cx="40" cy="62" rx="24" ry="12" fill="var(--brand)" opacity="0.4"/>
        </svg>
      </div>
      <h1 class="hero-name">Dorian Alden Dai</h1>
      <p class="hero-tagline">
        软件工程学生 · 记录学习，分享技术，积累成长
      </p>
      <div class="hero-stats">
        <div class="stat">
          <span class="stat-number">{{ displayPosts }}</span>
          <span class="stat-label">篇文章</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-number">{{ displayCats }}</span>
          <span class="stat-label">个分类</span>
        </div>
      </div>
      <div class="hero-actions">
        <a href="/about" class="btn btn-primary">关于我</a>
        <a href="/categories" class="btn btn-ghost">浏览分类</a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  position: relative;
  padding: 64px 24px 56px;
  text-align: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.35;
}

.blob-1 {
  width: 320px;
  height: 320px;
  background: var(--brand);
  top: -120px;
  right: -80px;
  animation: blob-float 12s ease-in-out infinite;
}

.blob-2 {
  width: 240px;
  height: 240px;
  background: var(--accent);
  bottom: -80px;
  left: -60px;
  opacity: 0.25;
  animation: blob-float 15s ease-in-out infinite reverse;
}

@keyframes blob-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%      { transform: translate(30px, -20px) scale(1.05); }
  66%      { transform: translate(-20px, 10px) scale(0.95); }
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 560px;
  margin: 0 auto;
}

.hero-avatar {
  width: 88px;
  height: 88px;
  margin: 0 auto 20px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  border: 3px solid #fff;
  background: var(--bg-card);
}

.dark .hero-avatar {
  border-color: var(--vp-c-bg-soft);
}

.hero-avatar svg {
  width: 100%;
  height: 100%;
}

.hero-name {
  font-size: 2.25rem;
  font-weight: 800;
  letter-spacing: -1px;
  color: var(--text-heading);
  margin: 0 0 8px;
}

.hero-tagline {
  font-size: 1.05rem;
  color: var(--vp-c-text-2);
  margin: 0 0 32px;
  line-height: 1.6;
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 36px;
}

.stat {
  padding: 0 28px;
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 800;
  color: var(--brand);
  font-variant-numeric: tabular-nums;
  letter-spacing: -1px;
}

.stat-label {
  display: block;
  font-size: 0.85rem;
  color: var(--vp-c-text-3);
  margin-top: 2px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--vp-c-divider);
}

.hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 10px 24px;
  border-radius: var(--radius-full);
  font-size: 0.93rem;
  font-weight: 600;
  text-decoration: none;
  transition: all var(--duration-normal) var(--ease-out);
  cursor: pointer;
}

.btn-primary {
  background: var(--brand);
  color: #fff;
}

.btn-primary:hover {
  background: var(--brand-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-ghost {
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  border: 1px solid var(--vp-c-border);
}

.btn-ghost:hover {
  border-color: var(--brand);
  color: var(--brand);
  background: var(--brand-soft);
}

@media (max-width: 600px) {
  .hero {
    padding: 40px 16px 36px;
  }

  .hero-name {
    font-size: 1.75rem;
  }

  .hero-tagline {
    font-size: 0.95rem;
  }

  .hero-stats {
    gap: 0;
  }

  .stat {
    padding: 0 20px;
  }

  .stat-number {
    font-size: 1.6rem;
  }
}
</style>
