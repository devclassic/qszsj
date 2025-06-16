<template>
  <RouterView />
</template>

<script setup>
  import { onMounted } from 'vue'
  import { useEventListener } from '@vueuse/core'

  onMounted(() => {
    useEventListener(document, 'contextmenu', e => {
      e.preventDefault()
    })
  })
</script>

<style>
  * {
    margin: 0;
    box-sizing: border-box;
  }
</style>
