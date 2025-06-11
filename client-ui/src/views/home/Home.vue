<template>
  <div class="box">
    <input v-model="state.input" @keyup="inputKeyup" class="input" />
    <div v-show="state.isRecording" class="recording"></div>
    <div @mousedown="asrMouseDown" @mouseup="asrMouseUp" @mouseout="asrMouseUp" class="asr"></div>
    <div @click="submit" class="submit"></div>
  </div>
</template>

<script setup>
  import { reactive, computed, watch } from 'vue'
  import { useWindowSize } from '@vueuse/core'
  import { ElMessage } from 'element-plus'
  import { useRouter } from 'vue-router'
  import asr from '../../utils/asr'
  import { useSearchStore } from '../../stores/search'

  const state = reactive({
    isRecording: false,
    input: '',
  })

  const searchStore = useSearchStore()
  const router = useRouter()

  const { width, height } = useWindowSize()

  const scale = computed(() => {
    return Math.min(width.value / 1920, height.value / 1080)
  })

  asr.ontext = text => {
    state.input = text
  }

  watch(
    () => state.isRecording,
    newVal => {
      console.log('isRecording', newVal)
      if (newVal) {
        asr.start(
          () => {},
          e => {
            console.log('开启录音失败', e)
            ElMessage.error('开启录音失败')
          },
        )
      } else {
        asr.stop()
      }
    },
  )

  const asrMouseDown = () => {
    state.isRecording = true
  }

  const asrMouseUp = () => {
    state.isRecording = false
  }

  const submit = () => {
    if (!state.input.trim()) {
      ElMessage.error('请输入有效内容')
      return
    }
    searchStore.value = state.input
    router.push('/chat')
  }

  const inputKeyup = e => {
    if (e.key === 'Enter') {
      submit()
    }
  }
</script>

<style scoped>
  .box {
    width: 1920px;
    height: 1080px;
    background: url('../../assets/images/home-bg.png') no-repeat center center / 100% 100%;
    position: relative;
    margin: 0 auto;
    zoom: v-bind(scale);
  }

  .input {
    width: 620px;
    height: 50px;
    line-height: 50px;
    font-size: 20px;
    border: none;
    outline: none;
    background: transparent;
    color: #000000;
    position: absolute;
    top: 562px;
    left: 593px;
  }

  .recording {
    position: absolute;
    top: 410px;
    right: 565px;
    background-color: rgba(228, 244, 253, 0.8);
    background-image: url(../../assets/images/recording.gif);
    background-repeat: no-repeat;
    background-position: center;
    background-size: 100px 80px;
    border-radius: 10px;
    width: 246px;
    height: 130px;
  }

  .asr {
    width: 30px;
    height: 30px;
    position: absolute;
    top: 572px;
    right: 669px;
    cursor: pointer;
  }

  .submit {
    width: 107px;
    height: 50px;
    position: absolute;
    top: 562px;
    right: 554px;
    cursor: pointer;
  }
</style>
