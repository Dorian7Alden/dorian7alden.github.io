<template>
  <div class="page">
    <Header class="page-header" />

    <main class="body">

      <aside class="col col-left">
        <div class="col-inner">
          <slot name="left" />
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
@import '../styles/layout.css';
</style>
