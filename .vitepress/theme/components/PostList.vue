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

const data = import.meta.glob('/content/categories.json', { eager: true })
const jsonData = (data['/content/categories.json'] as { default: { posts: Post[] } }).default
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
  max-width: 780px;
  margin: 0 auto;
}

.posts-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.empty {
  text-align: center;
  padding: 64px 0;
  color: var(--vp-c-text-3);
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  opacity: 0.4;
}

.empty p {
  font-size: 1rem;
  margin: 0;
}
</style>
