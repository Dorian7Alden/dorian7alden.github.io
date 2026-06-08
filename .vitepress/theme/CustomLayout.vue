<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import ReadingProgress from './components/ReadingProgress.vue'
import BackToTop from './components/BackToTop.vue'
import NoteTreePanel from './components/NoteTreePanel.vue'

const { Layout } = DefaultTheme
</script>

<template>
  <Layout>
    <template #layout-top>
      <ReadingProgress />
      <NoteTreePanel mode="doc" />
    </template>
    <template #layout-bottom>
      <BackToTop />
    </template>
  </Layout>
</template>
