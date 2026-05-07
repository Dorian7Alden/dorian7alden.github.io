<script setup lang="ts">
interface Category {
  name: string
  count: number
}

const data = import.meta.glob('/content/categories.json', { eager: true })
const jsonData = (data['/content/categories.json'] as { default: { categories: Category[] } }).default
const categories: Category[] = jsonData.categories

// Icon mapping for categories
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
  <nav class="category-nav">
    <div class="nav-header">
      <h2>文章分类</h2>
      <span class="nav-total">{{ categories.reduce((s, c) => s + c.count, 0) }}</span>
    </div>
    <ul class="nav-list">
      <li v-for="cat in categories" :key="cat.name" class="nav-item">
        <a :href="`/categories?cat=${encodeURIComponent(cat.name)}`" class="nav-link">
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
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  border: 1px solid var(--vp-c-divider);
  padding: 0;
  overflow: hidden;
}

.nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--vp-c-divider);
}

.nav-header h2 {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-heading);
}

.nav-total {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--vp-c-text-3);
  background: var(--vp-c-bg-soft);
  padding: 3px 10px;
  border-radius: var(--radius-full);
}

.nav-list {
  list-style: none;
  padding: 8px;
  margin: 0;
}

.nav-item {
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  color: var(--vp-c-text-1);
  text-decoration: none;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 500;
  transition: all var(--duration-fast) var(--ease-out);
}

.nav-link:hover {
  background: var(--brand-soft);
  color: var(--brand);
}

.nav-link:hover .nav-count {
  background: var(--brand);
  color: #fff;
}

.nav-icon {
  font-size: 1.05rem;
  flex-shrink: 0;
}

.nav-name {
  flex: 1;
}

.nav-count {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--vp-c-text-3);
  background: var(--vp-c-bg-soft);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  transition: all var(--duration-fast) var(--ease-out);
}

.nav-empty {
  text-align: center;
  padding: 24px;
  color: var(--vp-c-text-3);
  font-size: 0.9rem;
}
</style>
