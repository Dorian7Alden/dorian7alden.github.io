<template>
  <div class="sidebar-card card-profile">
    <img class="card-profile-avatar" :src="avatarUrl" :alt="profile.name" />
    <div class="card-profile-name">{{ profile.name }}</div>
    <div class="card-profile-desc">{{ profile.desc }}</div>
    <div class="card-profile-links">
      <a v-for="link in profile.links" :key="link.url" :href="link.url" target="_blank" :title="link.icon">
        <Icon :icon="link.icon" width="20" />
      </a>
    </div>
  </div>
</template>

<script setup>
import { useData } from 'vitepress'
import avatarUrl from '../../assets/avatar.jpg'
import { Icon } from '@iconify/vue'

const { theme } = useData()
const profile = theme.value.profile
</script>

<style>
@import '../../styles/index/profile-card.css';
</style>
