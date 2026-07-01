<template>
  <footer class="footer">
    <span class="footer-text">&copy; {{ year }} Dorian Alden</span>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
</script>

<style>
@import '../styles/footer.css';
</style>
