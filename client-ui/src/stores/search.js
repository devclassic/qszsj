import { defineStore } from 'pinia'
import { reactive } from 'vue'

export const useSearchStore = defineStore('counter', () => {
  const search = reactive({
    value: '',
  })
  return search
})
