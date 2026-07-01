<template>
  <div class="page">
    <Header class="page-header" />

    <main class="body">

      <aside class="col col-left">
        <div class="col-inner">
          <slot name="left" />

          <div class="sidebar-card">
            个人卡片<br/><br/><br/><br/>
          </div>

          <div class="sidebar-card">
            目录<br/><br/><br/><br/>
          </div>

          <div class="sidebar-card">
            其他信息<br/><br/><br/><br/>
          </div>

        </div>
      </aside>

      <section class="col col-center">
        <div class="col-inner">
          <slot />
          <Footer />
        </div>
      </section>

      <aside class="col col-right">
        <div class="col-inner">
          <slot name="right" />

          <div class="sidebar-card">
            统计<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
          </div>

          <div class="sidebar-card">
            推荐<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
          </div>

        </div>
      </aside>

    </main>
  </div>
</template>

<script setup>
import Header from '../components/Header.vue'
import Footer from '../components/Footer.vue'
</script>

<style>
@import '../styles/index.css';
</style>
