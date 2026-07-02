<template>
  <Layout v-if="frontmatter.layout !== false">
    <Content />
  </Layout>
  <Content v-else />
</template>

<script setup>
import { useData } from 'vitepress'
import { Content } from 'vitepress/dist/client/app/components/Content.js'
import Layout from './Layout.vue'
import { useMermaid } from './scripts/mermaid'

const { frontmatter } = useData()
useMermaid()
</script>
