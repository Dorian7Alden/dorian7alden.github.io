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
  // Estimate ~300 chars/min for Chinese
  return Math.max(1, Math.round(props.post.title.length / 6))
})

const formattedDate = computed(() => {
  const d = new Date(props.post.date)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
})

// Category color map for accent stripe
const categoryColors: Record<string, string> = {
  '卡片': '#5C6AC4',
  '开发规范': '#06B6D4',
  '未分类': '#8E94A0',
}

const accentColor = computed(() => categoryColors[props.post.category] || '#5C6AC4')
</script>

<template>
  <article
    class="post-card animate-fade-in-up"
    :class="`stagger-${Math.min(index + 1, 5)}`"
  >
    <div class="card-accent" :style="{ background: accentColor }"></div>
    <div class="card-body">
      <h2 class="card-title">
        <a :href="withBase(post.url)">{{ post.title }}</a>
      </h2>
      <div class="card-meta">
        <span class="meta-item meta-date">
          <svg class="meta-icon" viewBox="0 0 16 16" fill="none"><rect x="2" y="3" width="12" height="11" rx="1.5" stroke="currentColor" stroke-width="1.3"/><path d="M5 1v3M11 1v3M2 6h12" stroke="currentColor" stroke-width="1.3"/></svg>
          {{ formattedDate }}
        </span>
        <a :href="`/categories?cat=${encodeURIComponent(post.category)}`" class="meta-item meta-category">
          <svg class="meta-icon" viewBox="0 0 16 16" fill="none"><path d="M2 4.5A1.5 1.5 0 013.5 3h3l2 2h4A1.5 1.5 0 0114 6.5v5A1.5 1.5 0 0112.5 13h-9A1.5 1.5 0 012 11.5v-7z" stroke="currentColor" stroke-width="1.3"/></svg>
          {{ post.category }}
        </a>
        <span class="meta-item meta-read">
          <svg class="meta-icon" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.3"/><path d="M8 4.5V8l2.5 1.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
          ~{{ readingTime }} 分钟
        </span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.post-card {
  position: relative;
  display: flex;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  border: 1px solid var(--vp-c-divider);
  overflow: hidden;
  transition: all var(--duration-normal) var(--ease-out);
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: transparent;
}

.card-accent {
  width: 4px;
  flex-shrink: 0;
  transition: width var(--duration-normal) var(--ease-out);
  border-radius: 4px 0 0 4px;
}

.post-card:hover .card-accent {
  width: 6px;
}

.card-body {
  flex: 1;
  padding: 20px 24px;
  min-width: 0;
}

.card-title {
  margin: 0 0 10px;
  font-size: 1.1rem;
  font-weight: 650;
  line-height: 1.45;
}

.card-title a {
  color: var(--text-heading);
  text-decoration: none;
  transition: color var(--duration-fast) var(--ease-out);
}

.card-title a:hover {
  color: var(--brand);
}

.card-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px 16px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.83rem;
  color: var(--vp-c-text-3);
  text-decoration: none;
}

.meta-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  opacity: 0.7;
}

.meta-category {
  color: var(--brand);
  font-weight: 500;
  transition: opacity var(--duration-fast);
}

.meta-category:hover {
  opacity: 0.75;
}

@media (max-width: 600px) {
  .card-body {
    padding: 16px 18px;
  }

  .card-title {
    font-size: 1rem;
  }

  .card-meta {
    gap: 4px 12px;
  }
}
</style>
