<script setup lang="ts">
import { ref } from 'vue'
import { withBase } from 'vitepress'
import PostList from './PostList.vue'

interface Category {
  name: string
  count: number
}

interface CategoriesData {
  categories: Category[]
}

const params = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null
const activeCat = ref(params?.get('cat') || '')

const modules = import.meta.glob('/generated/notes/categories.json', { eager: true })
const jsonModule = modules['/generated/notes/categories.json'] as { default: CategoriesData }
const data: CategoriesData = jsonModule.default
const categories = data.categories
const total = categories.reduce((sum, cat) => sum + cat.count, 0)

const categoryIcons: Record<string, string> = {
  '卡片': '📝',
  '开发规范': '⚙️',
  'AI学习': '🤖',
  'Java学习': '☕',
  '小林coding': '📚',
  '工具使用': '🧰',
  '未分类': '📂',
}

function getIcon(name: string): string {
  return categoryIcons[name] || '📄'
}
</script>

<template>
  <div class="categories-page">
    <div v-if="!activeCat">
      <header class="page-hero">
        <span class="page-kicker">Knowledge Map</span>
        <h1 class="page-title">文章分类</h1>
        <p class="page-desc">共 {{ total }} 篇文章，按主题快速进入对应知识区。</p>
      </header>

      <div class="category-grid">
        <article v-for="cat in categories" :key="cat.name" class="cat-card">
          <a :href="withBase(`/categories?cat=${encodeURIComponent(cat.name)}`)" class="cat-link">
            <span class="cat-icon">{{ getIcon(cat.name) }}</span>
            <div class="cat-info">
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-meta">{{ cat.count }} 篇文章</span>
            </div>
            <span class="cat-action">
              查看
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M5.5 3.5L10 8l-4.5 4.5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </a>
        </article>
      </div>
    </div>

    <div v-else class="category-posts">
      <a :href="withBase('/categories')" class="back-link">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 3L5 8l5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        返回全部分类
      </a>

      <header class="page-hero compact">
        <span class="page-kicker">Category</span>
        <h1 class="page-title">{{ activeCat }}</h1>
        <p class="page-desc">共 {{ categories.find(c => c.name === activeCat)?.count || 0 }} 篇文章</p>
      </header>

      <PostList :category="activeCat" />
    </div>
  </div>
</template>

<style scoped>
.categories-page {
  max-width: 1040px;
  margin: 0 auto;
  padding: 10px 24px 64px;
}

.page-hero {
  position: relative;
  margin-bottom: 28px;
  padding: 34px;
  border-radius: 30px;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--bg-card) 95%, transparent), color-mix(in srgb, var(--bg-card) 78%, transparent)),
    radial-gradient(circle at 12% 10%, var(--brand-soft), transparent 42%),
    radial-gradient(circle at 88% 0%, var(--accent-soft), transparent 36%);
  border: 1px solid var(--vp-c-divider);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.page-hero.compact {
  margin-bottom: 20px;
  padding: 28px 30px;
}

.page-kicker {
  display: inline-flex;
  margin-bottom: 10px;
  color: var(--brand);
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.page-title {
  font-size: clamp(2rem, 5vw, 3.1rem);
  line-height: 1.05;
  font-weight: 900;
  letter-spacing: -0.07em;
  color: var(--text-heading);
  margin: 0;
}

.page-desc {
  color: var(--vp-c-text-2);
  margin: 12px 0 0;
  font-size: 1.02rem;
  line-height: 1.7;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.cat-card {
  position: relative;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--bg-card) 96%, transparent), color-mix(in srgb, var(--bg-card) 82%, transparent));
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-normal) var(--ease-out);
  overflow: hidden;
}

.cat-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 10% 0%, var(--brand-soft), transparent 42%);
  opacity: 0;
  transition: opacity var(--duration-normal) var(--ease-out);
}

.cat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: color-mix(in srgb, var(--brand) 26%, var(--vp-c-border));
}

.cat-card:hover::before {
  opacity: 1;
}

.cat-link {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 54px minmax(0, 1fr);
  gap: 14px;
  min-height: 132px;
  padding: 22px;
  text-decoration: none;
  color: inherit;
}

.cat-icon {
  font-size: 1.7rem;
  flex-shrink: 0;
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  background: var(--brand-soft);
  border: 1px solid color-mix(in srgb, var(--brand) 16%, transparent);
  border-radius: 18px;
}

.cat-info {
  min-width: 0;
}

.cat-name {
  display: block;
  color: var(--text-heading);
  font-size: 1.08rem;
  font-weight: 850;
  line-height: 1.35;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cat-meta {
  color: var(--vp-c-text-3);
  font-size: 0.84rem;
  font-weight: 650;
}

.cat-action {
  grid-column: 2;
  align-self: end;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  width: max-content;
  color: var(--brand);
  font-size: 0.84rem;
  font-weight: 800;
  transition: transform var(--duration-fast) var(--ease-out);
}

.cat-card:hover .cat-action {
  transform: translateX(4px);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: var(--brand);
  font-weight: 750;
  font-size: 0.93rem;
  text-decoration: none;
  margin: 0 0 16px;
  transition: gap var(--duration-fast);
}

.back-link:hover {
  gap: 11px;
}

@media (max-width: 640px) {
  .categories-page {
    padding: 0 16px 44px;
  }

  .page-hero {
    padding: 26px 22px;
  }

  .category-grid {
    grid-template-columns: 1fr;
  }
}
</style>
