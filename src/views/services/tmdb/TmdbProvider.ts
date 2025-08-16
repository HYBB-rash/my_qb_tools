import axios, { type AxiosInstance } from 'axios'
import type ITmdbProvider from './ITmdbProvider'
import type { SearchTvResponse } from '@/types/tmdb'

export default class TmdbProvider implements ITmdbProvider {
  private static _instance: TmdbProvider
  private axios: AxiosInstance

  private constructor() {
    const useProxy = import.meta.env.VITE_TMDB_PROXY === 'true'

    const baseURL = useProxy ? '/backend/tmdb' : 'https://api.themoviedb.org/3'
    const headers: Record<string, string> = { Accept: 'application/json' }

    if (!useProxy) {
      const token = import.meta.env.VITE_TMDB_API_TOKEN as string | undefined
      if (token) {
        headers.Authorization = `Bearer ${token}`
      } else if (import.meta.env.PROD) {
        // In production without proxy and without token → warn clearly
        console.warn('[TMDB] Missing VITE_TMDB_API_TOKEN; requests will likely fail.')
      }
    }

    this.axios = axios.create({ baseURL, headers })
  }

  public static getInstance(): TmdbProvider {
    if (!this._instance) this._instance = new TmdbProvider()
    return this._instance
  }

  async searchTv(query: string, page: number = 1, language: string = 'zh-CN'): Promise<SearchTvResponse> {
    const params = {
      query,
      page,
      language,
      include_adult: false,
    }
    const { data } = await this.axios.get<SearchTvResponse>('/search/tv', { params })
    return data
  }
}

