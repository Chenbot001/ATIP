<template>
  <div id="app">
    <TheHeader />
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import TheHeader from './components/TheHeader.vue'
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
  padding: 20px 0;
}
</style> 