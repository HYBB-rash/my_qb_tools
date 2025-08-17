<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useWindowSize } from '@vueuse/core'
import { useDialog } from '@/composables'
import { useMaindataStore, useTagStore, useTorrentStore } from '@/stores'
import tmdb from '@/services/tmdb'
import type { TvDetails, TvSearchResult } from '@/types/tmdb'

const props = defineProps<{
  guid: string
  hash?: string
  initialName?: string
}>()

const emit = defineEmits<{
  submit: [string[]]
}>()

const { isOpened } = useDialog(props.guid)
const torrentStore = useTorrentStore()
const maindataStore = useMaindataStore()
const tagStore = useTagStore()

// 搜索相关
const keyword = ref('')
const searching = ref(false)
const results = ref<TvSearchResult[]>([])
const selectedId = ref<number | null>(null)

// 详情相关
const detailsLoading = ref(false)
const details = ref<TvDetails | null>(null)
const selectedSeason = ref<number | null>(null)
const hasExistingInfo = ref(false)

const cdnBase = 'https://image.tmdb.org/t/p'
const posterThumbSize = 'w185' // 搜索结果列表缩略图
function posterUrlFor(size: string, path: string | null) {
  return path ? `${cdnBase}/${size}${path}` : ''
}

async function search() {
  const q = keyword.value.trim()
  if (!q) {
    results.value = []
    return
  }
  searching.value = true
  try {
    const data = await tmdb.searchTv(q, 1, 'zh-CN')
    results.value = data.results
  } finally {
    searching.value = false
  }
}

async function pick(item: TvSearchResult) {
  selectedId.value = item.id
  detailsLoading.value = true
  details.value = null
  selectedSeason.value = null
  try {
    const d = await tmdb.getTvDetails(item.id, 'zh-CN', 'CN')
    details.value = d
    // 默认选择第一个大于0的季，如果没有则选1
    const seasonList = (d.seasons || []).map(s => s.season_number).filter(n => n != null && n > 0)
    const defaultSeason = seasonList.length > 0 ? seasonList.sort((a, b) => a - b)[0] : 1
    selectedSeason.value = defaultSeason
  } finally {
    detailsLoading.value = false
  }
}

async function submit() {
  if (!selectedId.value || !selectedSeason.value) return

  const id = selectedId.value
  const s = selectedSeason.value
  const rawTitle = details.value?.name || props.initialName || ''
  const safeTitle = rawTitle.replace(/[\n\r,]/g, ' ').trim()
  const tmdbTag = `tmdb=${id}-${safeTitle}`
  const seasonTag = `season=${s}`

  // 如果提供了 hash，按原行为写入到种子；否则通过事件返回给调用方
  if (props.hash) {
    await tagStore.createTags([tmdbTag, seasonTag])
    await torrentStore.addTorrentTags([props.hash], [tmdbTag, seasonTag])
    maindataStore.forceMaindataSync()
  } else {
    emit('submit', [tmdbTag, seasonTag])
  }

  close()
}

function close() {
  isOpened.value = false
}

const showSearch = computed(() => !selectedId.value)
const firstAirDate = computed(() => details.value?.first_air_date || '')
const titleToShow = computed(() => details.value?.name || props.initialName || '')
const overview = computed(() => details.value?.overview || '')
// 详情使用最高分辨率 original；若带宽受限可改为 'w780'
const detailPoster = computed(() => posterUrlFor('original', details.value?.poster_path ?? null))
const seasonOptions = computed(() => (details.value?.seasons || []).filter(s => s.season_number > 0))
function backToResults() {
  selectedId.value = null
  details.value = null
  selectedSeason.value = null
}

// 当打开对话框时，如果已存在 tmdb=... 和 season=... 两个标签，则直接加载详情
onMounted(async () => {
  if (!props.hash) return
  const t = torrentStore.getTorrentByHash(props.hash)
  const tags = t?.tags ?? []
  const tmdbTag = tags.find(tag => tag.startsWith('tmdb='))
  const seasonTag = tags.find(tag => tag.startsWith('season='))
  if (!tmdbTag || !seasonTag) return
  hasExistingInfo.value = true

  // 解析 tmdb id；格式 tmdb=<id>-<title>
  const rest = tmdbTag.slice('tmdb='.length)
  const idPart = rest.split('-')[0]
  const id = Number.parseInt(idPart, 10)
  if (!Number.isFinite(id)) return

  const seasonPart = seasonTag.slice('season='.length)
  const seasonNum = Number.parseInt(seasonPart, 10)

  selectedId.value = id
  detailsLoading.value = true
  try {
    const d = await tmdb.getTvDetails(id, 'zh-CN', 'CN')
    details.value = d
    // 优先使用标签中的季；不合法则回退到默认季
    const seasonList = (d.seasons || []).map(s => s.season_number).filter(n => n != null && n > 0)
    const defaultSeason = seasonList.length > 0 ? seasonList.sort((a, b) => a - b)[0] : 1
    selectedSeason.value = seasonList.includes(seasonNum) ? seasonNum : defaultSeason
  } finally {
    detailsLoading.value = false
  }
})

// 不再自动监听输入框变更；改为点击按钮或回车触发搜索

async function clearExisting() {
  if (!props.hash) return
  const t = torrentStore.getTorrentByHash(props.hash)
  const tags = t?.tags ?? []
  const toRemove = tags.filter(tag => tag.startsWith('tmdb=') || tag.startsWith('season='))
  if (toRemove.length === 0) return
  await torrentStore.removeTorrentTags([props.hash], toRemove)
  maindataStore.forceMaindataSync()
  backToResults()
  hasExistingInfo.value = false
}
// Dialog size: width/height as 0.618 of viewport
const { width: winWidth, height: winHeight } = useWindowSize()
const dialogWidth = computed(() => Math.round(winWidth.value * 0.618))
const dialogHeight = computed(() => Math.round(winHeight.value * 0.618))
</script>

<template>
  <v-dialog v-model="isOpened" :width="dialogWidth">
    <v-card class="d-flex flex-column" :style="{ height: dialogHeight + 'px' }">
      <v-card-title>设定 TMDB 信息</v-card-title>
      <v-card-text style="flex: 1; overflow-y: auto">
        <div v-if="!hasExistingInfo" class="text-medium-emphasis mb-3">{{ props.initialName }}</div>

        <!-- 搜索视图 -->
        <template v-if="showSearch">
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
                  <v-img :src="posterUrlFor(posterThumbSize, item.poster_path)" height="200" cover />
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
        </template>

        <!-- 详情视图 -->
        <template v-else>
          <v-progress-linear v-if="detailsLoading" indeterminate color="accent" class="mb-2" />
          <div v-if="details">
            <!-- 剧名独占一行 -->
            <div class="text-h6 mb-3">{{ titleToShow }}</div>

            <!-- 第二行：首播在一行，海报放在首播日期下方，不与简介同行 -->
            <v-row dense class="ma-0 mb-2" align="start">
              <v-col cols="12">
                <div class="text-medium-emphasis mb-2"><strong>首播：</strong> {{ firstAirDate || '未知' }}</div>
                <div v-if="hasExistingInfo && props.initialName" class="text-medium-emphasis"><strong>源文件名：</strong> {{ props.initialName }}</div>
              </v-col>
              <v-col cols="12" class="d-flex mb-2">
                <v-img :src="detailPoster" :aspect-ratio="2/3" class="poster rounded" />
              </v-col>
              <v-col cols="12">
                <div style="white-space: pre-wrap">{{ overview || '暂无简介' }}</div>
              </v-col>
            </v-row>

            <!-- 选择季度独占一行 -->
            <div class="mb-1"><strong>选择季度：</strong></div>
            <v-radio-group v-model="selectedSeason" inline>
              <v-radio
                v-for="s in seasonOptions"
                :key="s.id"
                :label="`第 ${s.season_number} 季（${s.episode_count} 集）`"
                :value="s.season_number" />
            </v-radio-group>

            <!-- 规则预览 -->
            <div class="text-medium-emphasis mt-2">
              生成规则：tmdb-{{ selectedId || '' }}-s{{ selectedSeason || '' }} ({{ titleToShow }})
            </div>
          </div>
          <div v-else class="text-medium-emphasis">未能加载详情，请返回重试。</div>
        </template>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn v-if="!showSearch" variant="text" @click="backToResults">返回</v-btn>
        <v-btn v-if="props.hash" variant="text" color="warning" @click="clearExisting">清除 TMDB 信息</v-btn>
        <v-btn color="error" @click="close">取消</v-btn>
        <v-btn color="accent" :disabled="!selectedId || !selectedSeason" @click="submit">保存</v-btn>
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
.poster {
  width: 100%;
  aspect-ratio: 2 / 3;
}
/* Ensure the image itself uses contain to avoid cropping */
:deep(.poster .v-img__img),
:deep(.poster img) {
  object-fit: contain !important;
}
</style>
