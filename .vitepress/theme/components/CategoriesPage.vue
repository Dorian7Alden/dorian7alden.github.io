<script setup lang="ts">
import { ref } from 'vue'
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

const modules = import.meta.glob('/content/categories.json', { eager: true })
const jsonModule = modules['/content/categories.json'] as { default: CategoriesData }
const data: CategoriesData = jsonModule.default
const categories = data.categories

const categoryIcons: Record<string, string> = {
  '卡片': '📝',
  '开发规范': '⚙️',
  '未分类': '📂',
}

function getIcon(name: string): string {
  return categoryIcons[name] || '📄'
}
</script>

<template>
  <div class="categories-page">
    <div v-if="!activeCat">
      <h1 class="page-title">文章分类</h1>
      <p class="page-desc">按分类浏览所有文章</p>

      <div class="category-grid">
        <div v-for="cat in categories" :key="cat.name" class="cat-card">
          <a :href="`?cat=${encodeURIComponent(cat.name)}`" class="cat-link">
            <span class="cat-icon">{{ getIcon(cat.name) }}</span>
            <div class="cat-info">
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-meta">{{ cat.count }} 篇文章</span>
            </div>
            <svg class="cat-arrow" width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M6.5 4l5 5-5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </a>
        </div>
      </div>
    </div>

    <div v-else class="category-posts">
      <a href="/categories" class="back-link">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 3L5 8l5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        返回全部分类
      </a>
      <h1 class="page-title">{{ activeCat }}</h1>
      <p class="page-desc">共 {{ categories.find(c => c.name === activeCat)?.count || 0 }} 篇文章</p>
      <PostList :category="activeCat" />
    </div>
  </div>
</template>

<style scoped>
.categories-page {
  max-width: 780px;
  margin: 0 auto;
  padding: 0 24px 48px;
}

.page-title {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: var(--text-heading);
  margin: 0 0 6px;
}

.page-desc {
  color: var(--vp-c-text-2);
  margin: 0 0 28px;
  font-size: 1rem;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.cat-card {
  background: var(--bg-card);
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  transition: all var(--duration-normal) var(--ease-out);
}

.cat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: transparent;
}

.cat-link {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 22px 20px;
  text-decoration: none;
  color: inherit;
}

.cat-icon {
  font-size: 2rem;
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--brand-soft);
  border-radius: var(--radius-md);
}

.cat-info {
  flex: 1;
}

.cat-name {
  display: block;
  font-size: 1.05rem;
  font-weight: 650;
  color: var(--text-heading);
  margin-bottom: 4px;
}

.cat-meta {
  font-size: 0.83rem;
  color: var(--vp-c-text-3);
}

.cat-arrow {
  color: var(--vp-c-text-3);
  flex-shrink: 0;
  transition: transform var(--duration-fast);
}

.cat-card:hover .cat-arrow {
  transform: translateX(3px);
  color: var(--brand);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--brand);
  font-weight: 500;
  font-size: 0.93rem;
  text-decoration: none;
  margin-bottom: 20px;
  transition: gap var(--duration-fast);
}

.back-link:hover {
  gap: 10px;
}
</style>
