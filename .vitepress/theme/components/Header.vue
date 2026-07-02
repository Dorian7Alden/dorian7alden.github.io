<template>
  <header class="header">
    <div class="header-left">
      <a href="/" class="home-link" aria-label="回到首页">
        <Home class="home-icon" :size="20" />
        <span class="site-name">Dorian Alden</span>
      </a>
    </div>

    <nav class="header-center">
      <a href="/" class="nav-link"><Home class="nav-icon" :size="16" /><span>首页</span></a>
      <a href="/notes/" class="nav-link"><NotebookPen class="nav-icon" :size="16" /><span>笔记</span></a>
      <a href="/resources/" class="nav-link"><BookHeart class="nav-icon" :size="16" /><span>资源</span></a>
      <a href="/recommendations/" class="nav-link"><ThumbsUp class="nav-icon" :size="16" /><span>推荐</span></a>
      <a href="/projects/" class="nav-link"><CodeXmlIcon class="nav-icon" :size="16" /><span>项目</span></a>
      <a href="/aboutme" class="nav-link"><User class="nav-icon" :size="16" /><span>关于</span></a>
    </nav>

    <div class="header-right">
      <label class="search-box" for="header-search">
        <Search class="search-icon" :size="17" />
        <input
          id="header-search"
          type="text"
          class="search-input"
          placeholder="搜索"
          autocomplete="off"
        />
      </label>

      <button
        class="theme-toggle"
        @click="toggleTheme"
        :aria-label="isDark ? '切换到亮色模式' : '切换到暗色模式'"
        title="切换主题"
      >
        <Sun v-if="!isDark" class="toggle-icon" :size="18" />
        <Moon v-else class="toggle-icon" :size="18" />
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Home, NotebookPen, Wrench, FolderOpen, Sparkles, User, Search, Sun, Moon, BookHeart, ThumbsUp, CodeIcon, CodeXmlIcon } from '@lucide/vue'

const isDark = ref(false)

function applyTheme(dark) {
  isDark.value = dark
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
}

function toggleTheme() {
  const next = !isDark.value
  applyTheme(next)
  try { localStorage.setItem('theme', next ? 'dark' : 'light') } catch (_) {}
}

onMounted(() => {
  let stored
  try { stored = localStorage.getItem('theme') } catch (_) {}
  if (stored === 'dark' || stored === 'light') {
    applyTheme(stored === 'dark')
  } else {
    applyTheme(window.matchMedia('(prefers-color-scheme: dark)').matches)
  }
})
</script>

<style>
@import '../styles/header.css';
</style>
