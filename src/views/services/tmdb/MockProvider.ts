import type ITmdbProvider from './ITmdbProvider'
import type { SearchTvResponse } from '@/types/tmdb'

export default class MockTmdbProvider implements ITmdbProvider {
  private static _instance: MockTmdbProvider

  private constructor() {}

  public static getInstance(): MockTmdbProvider {
    if (!this._instance) this._instance = new MockTmdbProvider()
    return this._instance
  }

  async searchTv(query: string, page: number = 1): Promise<SearchTvResponse> {
    const seed = [
      {
        adult: false,
        id: 243224,
        name: '凡人修仙传',
        original_name: '凡人修仙传',
        original_language: 'zh',
        overview: '一个凡人修仙的故事。',
        first_air_date: '2020-07-25',
        poster_path: null,
        backdrop_path: null,
        popularity: 10,
        genre_ids: [16, 10765],
        origin_country: ['CN'],
        vote_average: 8.6,
        vote_count: 1000,
      },
      {
        adult: false,
        id: 83095,
        name: 'The Expanse',
        original_name: 'The Expanse',
        original_language: 'en',
        overview: 'A thriller set two hundred years in the future.',
        first_air_date: '2015-12-14',
        poster_path: null,
        backdrop_path: null,
        popularity: 20,
        genre_ids: [18, 10765],
        origin_country: ['US'],
        vote_average: 8.5,
        vote_count: 5000,
      },
    ]

    const results = seed.filter(s => s.name.toLowerCase().includes(query.toLowerCase()))

    return {
      page,
      total_pages: 1,
      total_results: results.length,
      results,
    }
  }
}

