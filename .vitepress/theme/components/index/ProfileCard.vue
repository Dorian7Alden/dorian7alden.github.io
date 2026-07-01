<template>
  <div class="sidebar-card card-profile">
    <img class="card-profile-avatar" :src="avatarUrl" alt="代双遥" />
    <div class="card-profile-name">代双遥</div>
    <div class="card-profile-desc">软件工程师</div>
    <div class="card-profile-links">
      <a href="https://github.com/dorian7alden" target="_blank" title="GitHub">
        <Icon icon="simple-icons:github" width="20" />
      </a>
      <a href="https://gitee.com/dorian7alden" target="_blank" title="Gitee">
        <Icon icon="simple-icons:gitee" width="20" />
      </a>
      <a href="https://b23.tv/mgdrLOu" target="_blank" title="Bilibili">
        <Icon icon="simple-icons:bilibili" width="20" />
      </a>
      <a href="mailto:dorian7alden@gmail.com" title="Email">
        <Icon icon="mdi:email" width="20" />
      </a>
    </div>
  </div>
</template>

<script setup>
import avatarUrl from '../../assets/avatar.jpg'
import { Icon } from '@iconify/vue'
</script>

<style scoped>
.card-profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.card-profile-avatar {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 12px;
  object-fit: cover;
}

.card-profile-name {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--color-text);
}

.card-profile-desc {
  font-size: 0.85rem;
  color: var(--color-muted);
}

.card-profile-links {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 4px;
}

.card-profile-links a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #e8f0fe;
  color: #4a90d9;
  transition: background 0.2s, color 0.2s;
}

.card-profile-links a:hover {
  background: #7ab8f5;
  color: #fff;
}
</style>
