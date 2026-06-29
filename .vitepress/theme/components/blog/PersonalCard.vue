<script setup lang="ts">
import { withBase, useData } from 'vitepress'
import { useCategories } from '../../composables/useCategories'
import ContributionHeatmap from './ContributionHeatmap.vue'

const { theme } = useData()
const blog = theme.value.blog
const author = blog.author

const { total: totalPosts, categories } = useCategories()
const totalCategories = categories.length
</script>

<template>
  <section id="personal-card" class="personal-card">
    <div class="card-left">
      <div class="avatar-wrap">
        <img :src="withBase(author.avatar)" :alt="author.name" />
      </div>

      <div class="card-name">{{ author.name }}</div>
      <div class="card-bio">{{ author.bio }}</div>

      <div class="card-stats">
        <div class="stat">
          <span class="stat-number">{{ totalPosts }}</span>
          <span class="stat-label">篇文章</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-number">{{ totalCategories }}</span>
          <span class="stat-label">个分类</span>
        </div>
      </div>
    </div>

    <div class="card-right">
      <div class="card-detail-placeholder">
        <div class="placeholder-line w-60"></div>
        <div class="placeholder-line w-80"></div>
        <div class="placeholder-line w-40"></div>
      </div>
      <ContributionHeatmap />
    </div>
  </section>
</template>

<style scoped>
.personal-card {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 32px;
  max-width: var(--page-width);
  margin: 0 auto;
  padding: 56px 24px 44px;
  align-items: start;
}

/* Left column */

.card-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 28px 20px;
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  border: 1px solid var(--vp-c-border);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.card-left::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 0%, var(--brand-soft), transparent 60%);
  pointer-events: none;
}

.avatar-wrap {
  width: 100px;
  height: 100px;
  padding: 4px;
  border-radius: 24px;
  background: linear-gradient(135deg, var(--brand-light), var(--accent));
  box-shadow: 0 12px 32px color-mix(in srgb, var(--brand) 22%, transparent);
  margin-bottom: 16px;
}

.avatar-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: 20px;
  border: 3px solid var(--bg-elevated);
}

.card-name {
  color: var(--text-heading);
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 4px;
}

.card-bio {
  color: var(--vp-c-text-2);
  font-size: 0.85rem;
  line-height: 1.5;
}

.card-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  padding: 14px 18px;
  width: 100%;
  background: var(--vp-c-bg-soft);
  border-radius: var(--radius-md);
}

.stat {
  flex: 1;
  text-align: center;
}

.stat-number {
  display: block;
  color: var(--brand);
  font-size: 1.5rem;
  line-height: 1;
  font-weight: 900;
  letter-spacing: -0.04em;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  display: block;
  margin-top: 4px;
  color: var(--vp-c-text-3);
  font-size: 0.76rem;
  font-weight: 600;
}

.stat-divider {
  width: 1px;
  height: 36px;
  background: var(--vp-c-divider);
}

/* Right column */

.card-right {
  min-width: 0;
  padding-top: 8px;
}

.card-detail-placeholder {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px 22px;
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border: 1px dashed var(--vp-c-border);
  margin-bottom: 20px;
}

.placeholder-line {
  height: 12px;
  border-radius: 6px;
  background: var(--vp-c-bg-soft);
}

.w-60 { width: 60%; }
.w-80 { width: 80%; }
.w-40 { width: 40%; }

/* Responsive */

@media (max-width: 768px) {
  .personal-card {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 40px 16px 32px;
  }

  .card-left {
    max-width: 320px;
    margin: 0 auto;
  }
}
</style>
