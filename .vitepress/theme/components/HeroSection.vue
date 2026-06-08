<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { withBase } from 'vitepress'

interface Category {
  name: string
  count: number
}

const modules = import.meta.glob('/generated/notes/categories.json', { eager: true })
const jsonModule = modules['/generated/notes/categories.json'] as { default: { total: number; categories: Category[] } }
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
      <div class="grid-glow"></div>
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
    </div>

    <div class="hero-shell">
      <div class="hero-copy">
        <div class="hero-kicker">
          <span class="kicker-dot"></span>
          Dorian7Alden · Tech Notes
        </div>

        <h1 class="hero-name">
          记录工程实践，沉淀技术成长
        </h1>

        <p class="hero-tagline">
          这里整理 Java、后端工程、AI 工具和学习实践中的真实笔记，把零散经验沉淀成可复用的知识卡片。
        </p>

        <div class="hero-actions">
          <a :href="withBase('/categories')" class="btn btn-primary">
            浏览文章
            <svg viewBox="0 0 16 16" fill="none"><path d="M6 3.5L10.5 8 6 12.5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </a>
          <a :href="withBase('/about')" class="btn btn-ghost">关于我</a>
        </div>
      </div>

      <div class="hero-panel">
        <div class="avatar-ring">
          <img :src="withBase('/avatar.jpg')" alt="Dorian7Alden 头像" />
        </div>
        <div class="panel-name">Dorian Alden Dai</div>
        <div class="panel-desc">软件工程学生 · 后端开发 · 持续学习中</div>

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

        <div class="topic-pills">
          <span>Java</span>
          <span>Spring</span>
          <span>AI Tools</span>
          <span>Git</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  position: relative;
  padding: 72px 24px 64px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.grid-glow {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(rgba(92, 106, 196, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(92, 106, 196, 0.07) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(circle at 50% 35%, #000 0%, transparent 68%);
}

.blob,
.orb {
  position: absolute;
  border-radius: 999px;
}

.blob {
  filter: blur(70px);
  opacity: 0.35;
}

.blob-1 {
  width: 360px;
  height: 360px;
  background: var(--brand);
  top: -140px;
  right: 4%;
  animation: blob-float 14s ease-in-out infinite;
}

.blob-2 {
  width: 300px;
  height: 300px;
  background: var(--accent);
  bottom: -120px;
  left: 2%;
  opacity: 0.22;
  animation: blob-float 18s ease-in-out infinite reverse;
}

.orb {
  width: 10px;
  height: 10px;
  background: var(--brand-light);
  box-shadow: 0 0 0 8px var(--brand-soft);
}

.orb-1 {
  top: 22%;
  left: 13%;
}

.orb-2 {
  right: 16%;
  bottom: 28%;
  background: var(--accent);
  box-shadow: 0 0 0 8px var(--accent-soft);
}

@keyframes blob-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%      { transform: translate(28px, -18px) scale(1.04); }
  66%      { transform: translate(-18px, 12px) scale(0.96); }
}

.hero-shell {
  position: relative;
  z-index: 1;
  max-width: 1120px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) 360px;
  gap: 40px;
  align-items: center;
}

.hero-copy {
  max-width: 700px;
}

.hero-kicker {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 8px 14px;
  margin-bottom: 18px;
  color: var(--brand);
  background: color-mix(in srgb, var(--brand) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--brand) 18%, transparent);
  border-radius: var(--radius-full);
  font-size: 0.86rem;
  font-weight: 700;
}

.kicker-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--brand);
  box-shadow: 0 0 0 5px var(--brand-soft);
}

.hero-name {
  margin: 0;
  color: var(--text-heading);
  font-size: clamp(2.35rem, 6vw, 4.7rem);
  line-height: 1.02;
  letter-spacing: -0.08em;
  font-weight: 900;
}

.hero-tagline {
  max-width: 620px;
  margin: 24px 0 0;
  color: var(--vp-c-text-2);
  font-size: 1.1rem;
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 34px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 22px;
  border-radius: var(--radius-full);
  font-size: 0.96rem;
  font-weight: 750;
  text-decoration: none;
  transition: all var(--duration-normal) var(--ease-out);
}

.btn svg {
  width: 16px;
  height: 16px;
  transition: transform var(--duration-fast) var(--ease-out);
}

.btn:hover svg {
  transform: translateX(3px);
}

.btn-primary {
  background: linear-gradient(135deg, var(--brand), var(--brand-light));
  color: #fff;
  box-shadow: 0 14px 28px color-mix(in srgb, var(--brand) 28%, transparent);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 38px color-mix(in srgb, var(--brand) 34%, transparent);
}

.btn-ghost {
  background: color-mix(in srgb, var(--bg-card) 86%, transparent);
  color: var(--vp-c-text-1);
  border: 1px solid var(--vp-c-border);
  box-shadow: var(--shadow-xs);
}

.btn-ghost:hover {
  border-color: var(--brand-light);
  color: var(--brand);
  transform: translateY(-2px);
}

.hero-panel {
  position: relative;
  padding: 30px;
  text-align: center;
  border: 1px solid color-mix(in srgb, var(--vp-c-border) 78%, transparent);
  border-radius: 30px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--bg-card) 92%, transparent), color-mix(in srgb, var(--bg-card) 72%, transparent)),
    radial-gradient(circle at 30% 0%, var(--brand-soft), transparent 48%);
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(18px);
}

.hero-panel::before {
  content: '';
  position: absolute;
  inset: 12px;
  border-radius: 22px;
  border: 1px solid color-mix(in srgb, var(--brand) 10%, transparent);
  pointer-events: none;
}

.avatar-ring {
  position: relative;
  width: 116px;
  height: 116px;
  margin: 0 auto 18px;
  padding: 5px;
  border-radius: 30px;
  background: linear-gradient(135deg, var(--brand-light), var(--accent));
  box-shadow: 0 18px 38px color-mix(in srgb, var(--brand) 24%, transparent);
}

.avatar-ring img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: 25px;
  border: 4px solid var(--bg-card);
}

.panel-name {
  color: var(--text-heading);
  font-size: 1.25rem;
  font-weight: 850;
}

.panel-desc {
  margin-top: 6px;
  color: var(--vp-c-text-2);
  font-size: 0.92rem;
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 24px 0;
  padding: 18px;
  background: var(--vp-c-bg-soft);
  border-radius: 22px;
}

.stat {
  flex: 1;
  text-align: center;
}

.stat-number {
  display: block;
  color: var(--brand);
  font-size: 2rem;
  line-height: 1;
  font-weight: 900;
  letter-spacing: -0.04em;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  display: block;
  margin-top: 6px;
  color: var(--vp-c-text-3);
  font-size: 0.82rem;
  font-weight: 650;
}

.stat-divider {
  width: 1px;
  height: 42px;
  background: var(--vp-c-divider);
}

.topic-pills {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.topic-pills span {
  padding: 6px 10px;
  border-radius: var(--radius-full);
  color: var(--vp-c-text-2);
  background: var(--bg-card);
  border: 1px solid var(--vp-c-divider);
  font-size: 0.78rem;
  font-weight: 650;
}

@media (max-width: 900px) {
  .hero {
    padding: 48px 18px 44px;
  }

  .hero-shell {
    grid-template-columns: 1fr;
  }

  .hero-copy {
    text-align: center;
    margin: 0 auto;
  }

  .hero-actions {
    justify-content: center;
  }

  .hero-panel {
    max-width: 420px;
    margin: 0 auto;
  }
}
</style>
