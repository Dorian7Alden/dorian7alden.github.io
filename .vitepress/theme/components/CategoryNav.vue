<script setup lang="ts">
import { withBase } from 'vitepress'

interface Category {
  name: string
  count: number
}

const data = import.meta.glob('/generated/notes/categories.json', { eager: true })
const jsonData = (data['/generated/notes/categories.json'] as { default: { categories: Category[] } }).default
const categories: Category[] = jsonData.categories
const total = categories.reduce((s, c) => s + c.count, 0)

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
  <nav class="category-nav">
    <div class="nav-header">
      <div>
        <span class="nav-kicker">Explore</span>
        <h2>文章分类</h2>
      </div>
      <span class="nav-total">{{ total }}</span>
    </div>

    <ul class="nav-list">
      <li v-for="cat in categories" :key="cat.name" class="nav-item">
        <a :href="withBase(`/categories?cat=${encodeURIComponent(cat.name)}`)" class="nav-link">
          <span class="nav-icon">{{ getIcon(cat.name) }}</span>
          <span class="nav-name">{{ cat.name }}</span>
          <span class="nav-count">{{ cat.count }}</span>
        </a>
      </li>
    </ul>

    <div v-if="categories.length === 0" class="nav-empty">
      暂无分类
    </div>
  </nav>
</template>

<style scoped>
.category-nav {
  position: sticky;
  top: 88px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--bg-card) 96%, transparent), color-mix(in srgb, var(--bg-card) 82%, transparent)),
    radial-gradient(circle at 0% 0%, var(--brand-soft), transparent 42%);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--vp-c-divider);
  padding: 10px;
  overflow: hidden;
  backdrop-filter: blur(14px);
}

.nav-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding: 16px 16px 14px;
  border-bottom: 1px solid var(--vp-c-divider);
}

.nav-kicker {
  display: block;
  margin-bottom: 3px;
  color: var(--brand);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.nav-header h2 {
  font-size: 1.08rem;
  line-height: 1.2;
  font-weight: 850;
  margin: 0;
  color: var(--text-heading);
  letter-spacing: -0.03em;
}

.nav-total {
  font-size: 0.82rem;
  font-weight: 800;
  color: var(--brand);
  background: var(--brand-soft);
  padding: 5px 11px;
  border-radius: var(--radius-full);
}

.nav-list {
  list-style: none;
  padding: 10px 4px 4px;
  margin: 0;
  max-height: 620px;
  overflow: auto;
}

.nav-item {
  margin: 0;
}

.nav-link {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  color: var(--vp-c-text-1);
  text-decoration: none;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 650;
  transition: all var(--duration-fast) var(--ease-out);
}

.nav-link:hover {
  background: var(--brand-soft);
  color: var(--brand);
  transform: translateX(2px);
}

.nav-icon {
  width: 28px;
  height: 28px;
  display: inline-grid;
  place-items: center;
  border-radius: 10px;
  background: var(--vp-c-bg-soft);
  font-size: 1rem;
}

.nav-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-count {
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--vp-c-text-3);
  background: var(--vp-c-bg-soft);
  padding: 3px 8px;
  border-radius: var(--radius-full);
  transition: all var(--duration-fast) var(--ease-out);
}

.nav-link:hover .nav-count {
  background: var(--brand);
  color: #fff;
}

.nav-empty {
  text-align: center;
  padding: 24px;
  color: var(--vp-c-text-3);
  font-size: 0.9rem;
}

@media (max-width: 960px) {
  .category-nav {
    position: relative;
    top: auto;
  }

  .nav-list {
    max-height: none;
  }
}
</style>
