<template>
  <RouterView />
</template>

<script setup>
  import { useEventListener } from '@vueuse/core'

  useEventListener('contextmenu', e => {
    e.preventDefault()
  })
</script>

<style>
  * {
    margin: 0;
    box-sizing: border-box;
  }
</style>
