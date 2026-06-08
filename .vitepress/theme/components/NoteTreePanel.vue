<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, withBase } from 'vitepress'

interface TreeNode {
  name: string
  type: 'directory' | 'file'
  path: string
  count: number
  title?: string
  url?: string
  date?: string
  order?: number
  children?: TreeNode[]
}

interface PostSummary {
  title: string
  date: string
  category: string
  order: number
  slug: string
  file: string
  pathSegments: string[]
  url: string
}

type Mode = 'home' | 'page' | 'doc'

const props = withDefaults(defineProps<{ mode?: Mode }>(), {
  mode: 'home',
})

const route = useRoute()
const data = import.meta.glob('/generated/notes/categories.json', { eager: true })
const jsonData = data['/generated/notes/categories.json'] as {
  default: {
    total: number
    categories: Array<{ name: string; count: number }>
    tree: TreeNode[]
    posts: PostSummary[]
  }
}

const summary = jsonData.default
const tree = summary.tree
const posts = summary.posts
const totalPosts = summary.total
const totalDirectories = tree.length
const openDirs = ref<Set<string>>(new Set())

function normalize(path: string): string {
  return path
    .replace(/\\/g, '/')
    .replace(/\/index\.html$/, '/')
    .replace(/\.html$/, '')
    .replace(/\/$/, '')
}

const pathname = computed(() => normalize(route.path || (typeof window !== 'undefined' ? window.location.pathname : '')))
const currentNoteUrl = computed(() => {
  const index = pathname.value.indexOf('/generated/notes/')
  return index >= 0 ? pathname.value.slice(index) : ''
})

const currentPost = computed(() => {
  if (!currentNoteUrl.value) return null
  return posts.find((post) => normalize(post.url) === currentNoteUrl.value) || null
})

const currentFolderPath = computed(() => currentPost.value?.pathSegments.join('/') || '')
const isDocPage = computed(() => props.mode === 'doc' && !!currentPost.value)
const isVisible = computed(() => props.mode !== 'doc' || isDocPage.value)

function collectDirectoryPaths(nodes: TreeNode[], paths: string[] = []): string[] {
  for (const node of nodes) {
    if (node.type === 'directory') {
      paths.push(node.path)
      if (node.children?.length) {
        collectDirectoryPaths(node.children, paths)
      }
    }
  }
  return paths
}

function buildDefaultOpenSet(): Set<string> {
  const next = new Set<string>()

  if (props.mode === 'doc') {
    const segments = currentPost.value?.pathSegments || []
    let cursor = ''
    for (const segment of segments) {
      cursor = cursor ? `${cursor}/${segment}` : segment
      next.add(cursor)
    }
    return next
  }

  for (const path of collectDirectoryPaths(tree, [])) {
    next.add(path)
  }
  return next
}

function resetOpenState(): void {
  openDirs.value = buildDefaultOpenSet()
}

watch([() => currentNoteUrl.value, () => props.mode], resetOpenState, { immediate: true })

function toggleDir(path: string): void {
  const next = new Set(openDirs.value)
  if (next.has(path)) {
    next.delete(path)
  } else {
    next.add(path)
  }
  openDirs.value = next
}

interface TreeRow {
  node: TreeNode
  depth: number
}

function flattenNodes(nodes: TreeNode[], depth = 0): TreeRow[] {
  const rows: TreeRow[] = []

  for (const node of nodes) {
    rows.push({ node, depth })
    if (node.type === 'directory' && node.children?.length && openDirs.value.has(node.path)) {
      rows.push(...flattenNodes(node.children, depth + 1))
    }
  }

  return rows
}

const visibleRows = computed(() => flattenNodes(tree))

function isActiveFile(node: TreeNode): boolean {
  return node.type === 'file' && normalize(node.url || '') === currentNoteUrl.value
}

function isActiveDir(node: TreeNode): boolean {
  return node.type === 'directory' && node.path === currentFolderPath.value
}

function getRowState(node: TreeNode): string {
  if (isActiveFile(node)) return 'active-file'
  if (isActiveDir(node)) return 'active-dir'
  return ''
}

function getCurrentHeading(): string {
  if (props.mode === 'doc' && currentPost.value) {
    return currentPost.value.title
  }
  return props.mode === 'page' ? '目录总览' : '文件树目录'
}

function getCurrentDescription(): string {
  if (props.mode === 'doc') {
    return '文件树与当前文章目录并列展示，便于在层级笔记中快速定位。'
  }
  if (props.mode === 'page') {
    return '按文件夹结构浏览笔记，文件夹会被当成知识大纲逐层展开。'
  }
  return '把笔记文件夹当成知识地图，沿着目录层级直接打开对应文档。'
}

function getStats(): Array<{ label: string; value: string }> {
  if (props.mode === 'doc') {
    return [
      { label: '当前文档', value: currentPost.value?.title || '未命中' },
      { label: '目录深度', value: String(currentPost.value?.pathSegments.length || 0) },
    ]
  }

  return [
    { label: '文章总数', value: String(totalPosts) },
    { label: '一级目录', value: String(totalDirectories) },
  ]
}

const bodyClass = 'has-note-tree-sidebar'

function syncBodyClass(): void {
  if (typeof document === 'undefined') return
  if (isDocPage.value) {
    document.body.classList.add(bodyClass)
  } else {
    document.body.classList.remove(bodyClass)
  }
}

onMounted(syncBodyClass)
watch(isDocPage, syncBodyClass)
onBeforeUnmount(() => {
  if (typeof document !== 'undefined') {
    document.body.classList.remove(bodyClass)
  }
})
</script>

<template>
  <aside v-if="isVisible" :class="['note-tree-panel', `mode-${mode}`]">
    <div class="panel-shell">
      <header class="panel-header">
        <div>
          <span class="panel-kicker">Knowledge Map</span>
          <h2>{{ getCurrentHeading() }}</h2>
        </div>
        <span class="panel-badge">{{ totalPosts }} 篇</span>
      </header>

      <p class="panel-desc">{{ getCurrentDescription() }}</p>

      <div v-if="mode === 'doc' && currentPost" class="current-doc-card">
        <span class="current-doc-label">当前文档路径</span>
        <h3>{{ currentPost.title }}</h3>
        <div class="breadcrumb-path">
          <span v-for="segment in currentPost.pathSegments" :key="segment" class="breadcrumb-chip">{{ segment }}</span>
        </div>
      </div>

      <div class="panel-stats">
        <div v-for="stat in getStats()" :key="stat.label" class="stat-pill">
          <span>{{ stat.label }}</span>
          <strong>{{ stat.value }}</strong>
        </div>
      </div>

      <nav class="tree-nav" aria-label="笔记文件树目录">
        <ul class="tree-list">
          <li
            v-for="row in visibleRows"
            :key="`${row.node.type}-${row.node.path}`"
            class="tree-item"
            :style="{ '--depth': row.depth }"
          >
            <button
              v-if="row.node.type === 'directory'"
              class="tree-row tree-directory"
              :class="getRowState(row.node)"
              type="button"
              @click="toggleDir(row.node.path)"
            >
              <span class="tree-caret" :class="{ open: openDirs.has(row.node.path) }">
                <svg viewBox="0 0 16 16" fill="none">
                  <path d="M6 3.5L10.5 8 6 12.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
              <span class="tree-icon">📁</span>
              <span class="tree-name">{{ row.node.name }}</span>
              <span class="tree-count">{{ row.node.count }}</span>
            </button>

            <a
              v-else
              class="tree-row tree-file"
              :class="getRowState(row.node)"
              :href="withBase(row.node.url || '#')"
            >
              <span class="tree-caret spacer"></span>
              <span class="tree-icon file">📄</span>
              <span class="tree-name">{{ row.node.title || row.node.name }}</span>
              <span class="tree-meta">{{ row.node.date }}</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </aside>
</template>

<style scoped>
.note-tree-panel {
  color: var(--vp-c-text-1);
}

.panel-shell {
  position: relative;
  padding: 18px;
  border-radius: var(--radius-xl);
  border: 1px solid var(--vp-c-divider);
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--bg-card) 96%, transparent), color-mix(in srgb, var(--bg-card) 82%, transparent)),
    radial-gradient(circle at 0% 0%, var(--brand-soft), transparent 44%);
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.mode-home .panel-shell,
.mode-page .panel-shell {
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.panel-kicker {
  display: inline-flex;
  margin-bottom: 6px;
  color: var(--brand);
  font-size: 0.74rem;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.panel-header h2 {
  margin: 0;
  color: var(--text-heading);
  font-size: 1.2rem;
  line-height: 1.2;
  letter-spacing: -0.04em;
  font-weight: 900;
}

.panel-badge {
  flex-shrink: 0;
  padding: 6px 11px;
  border-radius: var(--radius-full);
  background: var(--brand-soft);
  color: var(--brand);
  font-size: 0.78rem;
  font-weight: 850;
}

.panel-desc {
  margin: 12px 0 16px;
  color: var(--vp-c-text-2);
  font-size: 0.94rem;
  line-height: 1.7;
}

.current-doc-card {
  margin-bottom: 14px;
  padding: 16px;
  border-radius: 22px;
  background: color-mix(in srgb, var(--vp-c-bg-soft) 76%, transparent);
  border: 1px solid var(--vp-c-divider);
}

.current-doc-label {
  display: inline-flex;
  margin-bottom: 6px;
  color: var(--brand);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.current-doc-card h3 {
  margin: 0;
  color: var(--text-heading);
  font-size: 1rem;
  line-height: 1.45;
  font-weight: 850;
}

.breadcrumb-path {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.breadcrumb-chip {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: var(--radius-full);
  font-size: 0.76rem;
  font-weight: 750;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
}

.panel-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 14px;
}

.stat-pill {
  display: grid;
  gap: 3px;
  padding: 10px 12px;
  border-radius: 18px;
  background: color-mix(in srgb, var(--vp-c-bg-soft) 78%, transparent);
  border: 1px solid var(--vp-c-divider);
}

.stat-pill span {
  color: var(--vp-c-text-3);
  font-size: 0.74rem;
  font-weight: 700;
}

.stat-pill strong {
  color: var(--text-heading);
  font-size: 0.88rem;
  font-weight: 850;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tree-nav {
  max-height: 68vh;
  overflow: auto;
  padding-right: 2px;
}

.tree-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.tree-item {
  margin: 0;
}

.tree-row {
  width: 100%;
  display: grid;
  grid-template-columns: 18px 18px minmax(0, 1fr) auto;
  align-items: center;
  gap: 8px;
  padding: 10px 12px 10px calc(12px + (var(--depth) * 16px));
  margin: 2px 0;
  border-radius: 14px;
  text-decoration: none;
  color: var(--vp-c-text-1);
  transition: all var(--duration-fast) var(--ease-out);
}

.tree-row:hover {
  background: var(--brand-soft);
  transform: translateX(2px);
}

.tree-row.active-dir,
.tree-row.active-file {
  background: color-mix(in srgb, var(--brand) 10%, transparent);
  color: var(--brand-dark);
}

.dark .tree-row.active-dir,
.dark .tree-row.active-file {
  color: var(--brand-light);
}

.tree-directory {
  cursor: pointer;
  border: 0;
  background: transparent;
  text-align: left;
  font: inherit;
}

.tree-caret {
  display: grid;
  place-items: center;
  width: 18px;
  height: 18px;
  color: var(--vp-c-text-3);
  transition: transform var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
}

.tree-caret svg {
  width: 14px;
  height: 14px;
}

.tree-caret.open {
  transform: rotate(90deg);
  color: var(--brand);
}

.tree-caret.spacer {
  opacity: 0;
}

.tree-icon {
  display: grid;
  place-items: center;
  width: 18px;
  height: 18px;
  font-size: 0.9rem;
}

.tree-icon.file {
  opacity: 0.72;
}

.tree-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.92rem;
  font-weight: 720;
}

.tree-count,
.tree-meta {
  flex-shrink: 0;
  font-size: 0.73rem;
  font-weight: 800;
  color: var(--vp-c-text-3);
}

.tree-row.active-dir .tree-count,
.tree-row.active-file .tree-meta {
  color: var(--brand);
}

.note-tree-panel.mode-doc {
  display: none;
}

@media (min-width: 1440px) {
  .note-tree-panel.mode-doc {
    display: block;
    position: fixed;
    top: 88px;
    left: 24px;
    width: 288px;
    z-index: 30;
  }

  .has-note-tree-sidebar .VPContent {
    padding-left: 324px;
  }
}

@media (max-width: 1439px) {
  .note-tree-panel.mode-doc {
    display: none;
  }
}

@media (max-width: 960px) {
  .panel-stats {
    grid-template-columns: 1fr;
  }

  .tree-nav {
    max-height: none;
  }
}
</style>
