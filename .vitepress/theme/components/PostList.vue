<script setup lang="ts">
import { computed } from 'vue'
import PostCard from './PostCard.vue'

interface Post {
  title: string
  date: string
  category: string
  order: number
  slug: string
  file: string
  url: string
}

interface Props {
  category?: string
}

const props = defineProps<Props>()

const data = import.meta.glob('/generated/notes/categories.json', { eager: true })
const jsonData = (data['/generated/notes/categories.json'] as { default: { posts: Post[] } }).default
const allPosts = jsonData.posts

const posts = computed(() => {
  if (props.category) {
    return allPosts.filter((p: Post) => p.category === props.category)
  }
  return allPosts
})
</script>

<template>
  <div class="post-list">
    <div v-if="posts.length === 0" class="empty">
      <svg class="empty-icon" viewBox="0 0 48 48" fill="none"><rect x="6" y="8" width="36" height="32" rx="3" stroke="currentColor" stroke-width="2"/><path d="M6 16h36" stroke="currentColor" stroke-width="2"/><circle cx="14" cy="12" r="1.5" fill="currentColor"/><circle cx="19" cy="12" r="1.5" fill="currentColor"/></svg>
      <p>暂无文章</p>
    </div>
    <div v-else class="posts-grid">
      <PostCard
        v-for="(post, idx) in posts"
        :key="post.url"
        :post="post"
        :index="idx"
      />
    </div>
  </div>
</template>

<style scoped>
.post-list {
  width: 100%;
}

.posts-grid {
  display: grid;
  gap: 16px;
}

.empty {
  text-align: center;
  padding: 70px 24px;
  color: var(--vp-c-text-3);
  border: 1px dashed var(--vp-c-divider);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
}

.empty-icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 12px;
  opacity: 0.42;
}

.empty p {
  font-size: 1rem;
  margin: 0;
}
</style>
