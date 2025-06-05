<template>
  <div class="box">
    <div class="btn-back" @click="back"></div>
    <div class="btn-history"></div>
    <div @click="newChat" class="btn-new"></div>
    <div ref="content" class="content">
      <template v-for="message of state.messages" :key="message.id">
        <div class="item" :class="message.type">
          <div class="item-box">
            <div v-if="message.type === 'left'" class="avatar"></div>
            <div class="message">
              <template v-if="message.content">{{ message.content }}</template>
              <div v-else class="loading"></div>
            </div>
          </div>
        </div>
      </template>
    </div>
    <input v-model="state.input" @keyup="inputKeyup" spellcheck="false" class="input" />
    <div class="btn-asr"></div>
    <div @click="sendMessage" class="btn-send"></div>
  </div>
</template>

<script setup>
  import { computed, reactive, useTemplateRef, nextTick } from 'vue'
  import { useRouter } from 'vue-router'
  import { useWindowSize } from '@vueuse/core'
  import { v4 as uuidv4 } from 'uuid'

  const state = reactive({
    input: '',
    /*
     * messages structure:
     * {
     *   id: unique identifier,
     *   type: 'left' | 'right',
     *   content: string (message text),
     * }
     */
    messages: [],
  })

  const contentRef = useTemplateRef('content')

  const router = useRouter()
  const { width, height } = useWindowSize()

  const scale = computed(() => {
    return Math.min(width.value / 1920, height.value / 1080)
  })

  const back = () => {
    router.back()
  }

  const newChat = () => {
    state.messages = []
    state.input = ''
  }

  const setMessage = (id, message) => {
    state.messages = state.messages.map(item => {
      if (item.id === id) {
        item.content = message
      }
      return item
    })
  }

  const processMessage = async question => {
    const answer = { id: uuidv4(), type: 'left', content: '' }
    state.messages.push(answer)
    await nextTick()
    contentRef.value.scrollTo({
      top: contentRef.value.scrollHeight,
      behavior: 'smooth',
    })
    setTimeout(async () => {
      setMessage(answer.id, '我是机器人，你好！')
      await nextTick()
      contentRef.value.scrollTo({
        top: contentRef.value.scrollHeight,
        behavior: 'smooth',
      })
    }, 1000)
  }

  const sendMessage = () => {
    if (state.input.trim()) {
      state.messages.push({ id: uuidv4(), type: 'right', content: state.input })
      processMessage(state.input)
      state.input = ''
    }
  }

  const inputKeyup = e => {
    if (e.key === 'Enter') {
      sendMessage()
    }
  }
</script>

<style scoped>
  .box {
    width: 1920px;
    height: 1080px;
    background: url('../../assets/images/chat-bg.png') no-repeat center center / 100% 100%;
    margin: 0 auto;
    position: relative;
    zoom: v-bind(scale);
  }

  .btn-back {
    width: 153px;
    height: 42px;
    position: absolute;
    top: 45px;
    left: 49px;
    cursor: pointer;
  }

  .btn-history {
    width: 153px;
    height: 42px;
    position: absolute;
    top: 45px;
    left: 214px;
    cursor: pointer;
  }

  .btn-new {
    width: 153px;
    height: 42px;
    position: absolute;
    top: 45px;
    right: 53px;
    cursor: pointer;
  }

  .content {
    width: 1750px;
    height: 690px;
    overflow-y: auto;
    position: absolute;
    top: 165px;
    left: 50%;
    transform: translateX(-50%);
  }

  .item {
    display: flex;
    margin-bottom: 20px;
  }

  .item.left {
    justify-content: start;
  }

  .item.right {
    justify-content: end;
  }

  .item-box {
    display: flex;
  }

  .avatar {
    width: 80px;
    height: 80px;
    background: url('../../assets/images/avatar.png') no-repeat center center / cover;
  }

  .message {
    max-width: 730px;
    border-radius: 15px;
    position: relative;
    margin-top: 5px;
    color: #3e3a39;
    font-size: 20px;
  }

  .message .loading {
    width: 35px;
    height: 35px;
    background: url('../../assets/images/loading.png') no-repeat center center / 100% 100%;
    margin: 5px 50px;
  }

  .left .message {
    background: linear-gradient(to bottom, #ceebfb, transparent);
    margin-left: 23px;
    padding: 15px 20px 0;
  }

  .left .message::before {
    content: '';
    width: 13px;
    height: 18px;
    position: absolute;
    top: 15px;
    left: -13px;
    background: url('../../assets/images/arrow-left.png') no-repeat center center / 100% 100%;
  }

  .right .message {
    background: linear-gradient(to bottom, #caffec, transparent);
    margin-right: 23px;
    padding: 15px 20px 25px;
  }

  .right .message::before {
    content: '';
    width: 7px;
    height: 7px;
    position: absolute;
    top: 8px;
    right: -6px;
    background: url('../../assets/images/arrow-right.png') no-repeat center center / 100% 100%;
  }

  .input {
    width: 1230px;
    height: 40px;
    line-height: 40px;
    font-size: 26px;
    border: none;
    outline: none;
    color: #3e3a39;
    background: transparent;
    position: absolute;
    left: 140px;
    bottom: 63px;
  }

  .btn-asr {
    width: 246px;
    height: 82px;
    position: absolute;
    right: 256px;
    bottom: 40px;
    cursor: pointer;
  }

  .btn-send {
    width: 187px;
    height: 70px;
    position: absolute;
    right: 51px;
    bottom: 45px;
    cursor: pointer;
  }
</style>
