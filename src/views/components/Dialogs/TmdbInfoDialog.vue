<script setup lang="ts">
import { ref } from 'vue'
import { useDialog } from '@/composables'
import { useMaindataStore, useTagStore, useTorrentStore } from '@/stores'
import tmdb from '@/services/tmdb'
import type { TvSearchResult } from '@/types/tmdb'

const props = defineProps<{
  guid: string
  hash: string
  initialName?: string
}>()

const { isOpened } = useDialog(props.guid)
const torrentStore = useTorrentStore()
const maindataStore = useMaindataStore()
const tagStore = useTagStore()

// 注意：季数输入后续再开发，当前默认季数为 1
const DEFAULT_SEASON = 1

// 搜索相关
const keyword = ref('')
const searching = ref(false)
const results = ref<TvSearchResult[]>([])
const selectedId = ref<number | null>(null)

const cdnBase = 'https://image.tmdb.org/t/p'
const posterSize = 'w185'
function posterUrl(path: string | null) {
  return path ? `${cdnBase}/${posterSize}${path}` : ''
}

async function search() {
  const q = keyword.value.trim()
  if (!q) return
  searching.value = true
  try {
    const data = await tmdb.searchTv(q, 1, 'zh-CN')
    results.value = data.results
  } finally {
    searching.value = false
  }
}

function pick(item: TvSearchResult) {
  selectedId.value = item.id
}

async function submit() {
  if (!selectedId.value) return

  const id = selectedId.value
  const s = DEFAULT_SEASON
  const tag = `tmdb-${id}-s${s}`

  // 确保标签存在，再绑定到种子
  await tagStore.createTags([tag])
  await torrentStore.addTorrentTags([props.hash], [tag])
  maindataStore.forceMaindataSync()

  close()
}

function close() {
  isOpened.value = false
}
</script>

<template>
  <v-dialog v-model="isOpened" max-width="520">
    <v-card>
      <v-card-title>设定 TMDB 信息</v-card-title>
      <v-card-text>
        <div class="text-medium-emphasis mb-3">{{ initialName }}</div>

        <!-- 搜索区 -->
        <div class="d-flex align-center mb-2" style="gap: 8px">
          <v-text-field
            v-model="keyword"
            density="comfortable"
            hide-details
            placeholder="输入关键词，例如：凡人修仙传"
            label="搜索 TMDB"
            @keydown.enter.prevent="search" />
          <v-btn color="accent" :loading="searching" @click="search">搜索</v-btn>
        </div>
        <v-progress-linear v-if="searching" indeterminate color="accent" class="mb-2" />

        <!-- 结果区：卡片列表 -->
        <div class="results">
          <v-row dense class="ma-0">
            <v-col v-for="item in results" :key="item.id" cols="12" sm="6" md="4">
              <v-card class="cursor-pointer" :elevation="selectedId === item.id ? 8 : 2" @click="pick(item)">
                <v-img :src="posterUrl(item.poster_path)" height="200" cover />
                <v-card-title class="text-subtitle-2">{{ item.name }}</v-card-title>
                <v-card-subtitle>{{ item.first_air_date || '未知首播日期' }}</v-card-subtitle>
                <v-card-text>
                  <v-tooltip location="top" :text="item.overview || '暂无简介'">
                    <template #activator="{ props }">
                      <div v-bind="props" class="overview line-clamp-3">{{ item.overview || '暂无简介' }}</div>
                    </template>
                  </v-tooltip>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          <div v-if="!searching && results.length === 0 && keyword" class="text-medium-emphasis">没有匹配的结果</div>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="error" @click="close">取消</v-btn>
        <v-btn color="accent" :disabled="!selectedId" @click="submit">保存</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  
</template>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.overview {
  line-height: 1.3em;
  min-height: calc(1.3em * 3);
}
.results {
  max-height: 320px;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
