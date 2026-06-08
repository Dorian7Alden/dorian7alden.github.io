<script setup lang="ts">
import { computed } from 'vue'
import { withBase } from 'vitepress'

interface Post {
  title: string
  date: string
  category: string
  slug: string
  url: string
}

const props = defineProps<{
  post: Post
  index: number
}>()

const readingTime = computed(() => {
  return Math.max(1, Math.round(props.post.title.length / 6))
})

const formattedDate = computed(() => {
  const d = new Date(props.post.date)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
})

const categoryColors: Record<string, string> = {
  '卡片': '#4F6DF5',
  '开发规范': '#12B8A6',
  'AI学习': '#8B5CF6',
  'Java学习': '#F97316',
  '小林coding': '#06B6D4',
  '未分类': '#8E94A0',
}

const accentColor = computed(() => categoryColors[props.post.category] || '#4F6DF5')
</script>

<template>
  <article
    class="post-card animate-fade-in-up"
    :class="`stagger-${Math.min(index + 1, 5)}`"
    :style="{ '--accent-color': accentColor }"
  >
    <a class="card-link" :href="withBase(post.url)" aria-label="阅读文章">
      <div class="card-topline">
        <span class="category-chip">{{ post.category }}</span>
        <span class="date-chip">{{ formattedDate }}</span>
      </div>

      <h2 class="card-title">{{ post.title }}</h2>

      <div class="card-footer">
        <span class="read-time">
          <svg class="meta-icon" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.3"/><path d="M8 4.5V8l2.5 1.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
          {{ readingTime }} 分钟阅读
        </span>
        <span class="arrow-pill">
          阅读
          <svg viewBox="0 0 16 16" fill="none"><path d="M5.5 3.5L10 8l-4.5 4.5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
      </div>
    </a>
  </article>
</template>

<style scoped>
.post-card {
  --accent-color: var(--brand);
  position: relative;
  border-radius: var(--radius-xl);
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--bg-card) 96%, transparent), color-mix(in srgb, var(--bg-card) 82%, transparent)),
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--accent-color) 14%, transparent), transparent 40%);
  border: 1px solid var(--vp-c-divider);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: transform var(--duration-normal) var(--ease-out), box-shadow var(--duration-normal) var(--ease-out), border-color var(--duration-normal) var(--ease-out);
}

.post-card::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 5px;
  background: linear-gradient(180deg, var(--accent-color), color-mix(in srgb, var(--accent-color) 35%, transparent));
  opacity: 0.9;
}

.post-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: color-mix(in srgb, var(--accent-color) 32%, var(--vp-c-border));
}

.card-link {
  display: block;
  padding: 22px 24px 22px 28px;
  color: inherit;
  text-decoration: none;
}

.card-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.category-chip,
.date-chip,
.read-time,
.arrow-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 700;
}

.category-chip {
  padding: 5px 10px;
  border-radius: var(--radius-full);
  color: var(--accent-color);
  background: color-mix(in srgb, var(--accent-color) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--accent-color) 18%, transparent);
}

.date-chip {
  color: var(--vp-c-text-3);
  white-space: nowrap;
}

.card-title {
  margin: 0;
  color: var(--text-heading);
  font-size: 1.18rem;
  line-height: 1.5;
  letter-spacing: -0.025em;
  font-weight: 820;
  transition: color var(--duration-fast) var(--ease-out);
}

.post-card:hover .card-title {
  color: var(--accent-color);
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid var(--vp-c-divider);
}

.read-time {
  color: var(--vp-c-text-3);
}

.meta-icon,
.arrow-pill svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.arrow-pill {
  color: var(--vp-c-text-2);
  transition: color var(--duration-fast), transform var(--duration-fast);
}

.post-card:hover .arrow-pill {
  color: var(--accent-color);
  transform: translateX(3px);
}

@media (max-width: 600px) {
  .card-link {
    padding: 18px 18px 18px 22px;
  }

  .card-topline,
  .card-footer {
    align-items: flex-start;
    flex-direction: column;
  }

  .card-title {
    font-size: 1.04rem;
  }
}
</style>
