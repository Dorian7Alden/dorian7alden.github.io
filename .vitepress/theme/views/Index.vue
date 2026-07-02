<template>
  <Layout>
    <template #left>
      <ProfileCard />

      <div class="sidebar-card">
        目录<br/><br/><br/><br/>
      </div>

      <div class="sidebar-card">
        其他信息<br/><br/><br/><br/>
      </div>
    </template>

    <template #right>
      <div class="sidebar-card">
        统计<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
      </div>

      <div class="sidebar-card">
        推荐<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
      </div>
    </template>
  </Layout>
</template>

<script setup>
import Layout from '../Layout.vue'
import ProfileCard from '../components/index/ProfileCard.vue'
</script>
