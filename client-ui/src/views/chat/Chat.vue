<template>
  <div class="box">
    <div class="history" :class="{ show: state.showHistory }">
      <div class="items">
        <div
          v-for="item of state.historys"
          :key="item.id"
          class="item"
          @click="loadHistory(item.id)">
          <div class="icon"></div>
          <div class="text" :title="item.query">
            <el-text truncated>
              {{ item.query }}
            </el-text>
          </div>
        </div>
      </div>
      <div @click="closeHistory" class="close"></div>
    </div>
    <div class="btn-back" @click="back"></div>
    <div v-loading="state.isHistoryLoading" @click="showHistory" class="btn-history"></div>
    <div @click="newChat" class="btn-new"></div>
    <div v-loading="state.isContentLoading" ref="content" class="content">
      <template v-for="message of state.messages" :key="message.id">
        <div class="item" :class="message.type">
          <div class="item-box">
            <div v-if="message.type === 'left'" class="avatar"></div>
            <div class="message">
              <div v-if="message.content" v-html="message.content"></div>
              <div v-else class="loading"></div>
            </div>
          </div>
        </div>
      </template>
    </div>
    <input v-model="state.input" @keyup="inputKeyup" spellcheck="false" class="input" />
    <div v-show="state.isRecording" class="recording"></div>
    <div
      @mousedown="asrMouseDown"
      @mouseup="asrMouseUp"
      @mouseout="asrMouseUp"
      @touchstart="asrMouseDown"
      @touchend="asrMouseUp"
      class="btn-asr"></div>
    <div @click="sendMessage" class="btn-send"></div>
  </div>
</template>

<script setup>
  import { computed, reactive, useTemplateRef, nextTick, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useWindowSize } from '@vueuse/core'
  import { v4 as uuidv4 } from 'uuid'
  import { ElMessage } from 'element-plus'
  import { useSearchStore } from '../../stores/search'
  import asr from '../../utils/asr'
  import http from '../../utils/http'
  import markdownit from 'markdown-it'

  const md = markdownit()

  const state = reactive({
    input: '',
    isRecording: false,
    showHistory: false,
    isHistoryLoading: false,
    isContentLoading: false,
    /*
     * messages structure:
     * {
     *   id: unique identifier,
     *   type: 'left' | 'right',
     *   content: string (message text),
     * }
     */
    messages: [],
    historys: [],
  })

  const app_id = localStorage.getItem('app_id')
  const account_id = localStorage.getItem('account_id')
  let conversation_id = ''

  asr.ontext = text => {
    state.input = text
  }

  watch(
    () => state.isRecording,
    newVal => {
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

  const contentRef = useTemplateRef('content')

  const router = useRouter()
  const { width, height } = useWindowSize()

  const scale = computed(() => {
    return Math.min(width.value / 1920, height.value / 1080)
  })

  const back = () => {
    router.push('/home')
  }

  const showHistory = async () => {
    state.isHistoryLoading = true
    const res = await http.post('/client/conversations', { app_id, account_id })
    if (res.data.success) {
      state.historys = res.data.data
      console.log(res.data.data)
    }
    state.isHistoryLoading = false
    state.showHistory = true
  }

  const loadHistory = async id => {
    state.showHistory = false
    state.isContentLoading = true
    const res = await http.post('/client/messages', { app_id, account_id, conversation_id: id })
    if (res.data.success) {
      console.log(res.data.data)
      state.messages = []
      for (const item of res.data.data) {
        state.messages.push({ id: uuidv4(), type: 'right', content: item.query })
        state.messages.push({
          id: uuidv4(),
          type: 'left',
          content: md.render(item.answer.replace(/<think>[\s\S]*?<\/think>/g, '')),
        })
        conversation_id = item.conversation_id
      }
      await nextTick()
      contentRef.value.scrollTo({
        top: contentRef.value.scrollHeight,
        behavior: 'smooth',
      })
    }
    state.isContentLoading = false
  }

  const closeHistory = () => {
    state.showHistory = false
  }

  const newChat = () => {
    conversation_id = ''
    state.messages = []
    state.input = ''
  }

  const asrMouseDown = () => {
    state.isRecording = true
  }

  const asrMouseUp = () => {
    state.isRecording = false
  }

  let tempmsg = ''
  const setMessage = (id, message) => {
    state.messages = state.messages.map(item => {
      if (item.id === id) {
        tempmsg += message
        const reg = /<think>[\s\S]*?<\/think>/
        const match = tempmsg.match(reg)
        if (match) {
          const think = match[0]
          let tk = think.replace('<think>', '').replace('</think>', '')
          tk = md.render(tk)
          tk = `<div class="think-proc" onclick="$('think').is(':visible')?$('think').hide():$('think').show()">【思考过程】</div><think>${tk}</think>`
          item.content =
            tk + md.render(tempmsg.replace('```markdown', '').replace('```', '').replace(think, ''))
        } else {
          item.content = md.render(tempmsg.replace('```markdown', '').replace('```', ''))
        }
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
    const baseurl = import.meta.env.VITE_API_BASE_URL ?? ''
    const url = baseurl + '/client/chat'

    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ app_id, account_id, conversation_id, question }),
    })
    const reader = res.body.getReader()
    const decoder = new TextDecoder('utf-8')
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      try {
        const data = JSON.parse(chunk.trim())
        switch (data.event) {
          case 'message':
            setMessage(answer.id, data.answer)
            await nextTick()
            contentRef.value.scrollTo({
              top: contentRef.value.scrollHeight,
              behavior: 'smooth',
            })
            break
          case 'message_end':
            await http.post('/client/savechat', { account_id, app_id, question, answer: tempmsg })
            tempmsg = ''
            conversation_id = data.conversation_id
            break
        }
      } catch (e) {
        // 非 JSON 行忽略
      }
    }
  }

  const searchStore = useSearchStore()
  if (searchStore.value) {
    const question = { id: uuidv4(), type: 'right', content: searchStore.value }
    state.messages.push(question)
    processMessage(searchStore.value)
    searchStore.value = ''
  }

  const sendMessage = () => {
    if (state.input.trim()) {
      state.messages.push({ id: uuidv4(), type: 'right', content: state.input })
      processMessage(state.input)
      state.input = ''
    } else {
      ElMessage.error('请输入有效内容')
    }
  }

  const inputKeyup = e => {
    if (e.key === 'Enter') {
      sendMessage()
    }
  }
</script>

<style>
  .think-proc {
    margin-bottom: 10px;
    cursor: pointer;
    color: #777777;
  }

  think {
    color: #777777;
    display: none;
    margin-bottom: 10px;
  }
</style>

<style scoped>
  .box {
    width: 1920px;
    height: 1080px;
    background: url('../../assets/images/chat-bg.png') no-repeat center center / 100% 100%;
    margin: 0 auto;
    position: relative;
    zoom: v-bind(scale);
    overflow: hidden;
  }

  .history {
    width: 300px;
    height: 100%;
    background: #e5f3fb;
    position: absolute;
    transition: transform 0.3s ease;
    transform: translateX(-100%);
    z-index: 3000;
  }

  .history.show {
    transform: translateX(0);
  }

  .history .items {
    width: 235px;
    margin: 55px auto 0;
  }

  .history .item {
    width: 235px;
    height: 45px;
    background: #fffdfd;
    border: 1px solid #c5e7f6;
    border-radius: 25px;
    position: relative;
    cursor: pointer;
  }

  .history .item .icon {
    width: 20px;
    height: 20px;
    background: url('../../assets/images/history-item-icon.png') no-repeat center center / 100% 100%;
    position: absolute;
    top: 50%;
    left: 25px;
    transform: translateY(-50%);
  }

  .history .item .text {
    width: 160px;
    height: 100%;
    line-height: 42px;
    color: #3e3a39;
    position: absolute;
    left: 55px;
  }

  .history .close {
    width: 103px;
    height: 29px;
    background: url('../../assets/images/history-close.png') no-repeat center center / 100% 100%;
    position: absolute;
    bottom: 35px;
    left: 50%;
    transform: translateX(-50%);
    cursor: pointer;
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
    width: 180px;
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
    background: transparent;
    color: #3e3a39;
    position: absolute;
    left: 140px;
    bottom: 63px;
  }

  .recording {
    position: absolute;
    bottom: 180px;
    right: 256px;
    background-color: rgba(228, 244, 253, 0.8);
    background-image: url(../../assets/images/recording.gif);
    background-repeat: no-repeat;
    background-position: center;
    background-size: 100px 80px;
    border-radius: 10px;
    width: 246px;
    height: 130px;
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
