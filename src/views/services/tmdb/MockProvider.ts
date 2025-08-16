import type ITmdbProvider from './ITmdbProvider'
import type { SearchTvResponse, TvDetails } from '@/types/tmdb'

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

  async getTvDetails(tmdbId: number, language: string = 'zh-CN', watchRegion: string = 'CN'): Promise<TvDetails> {
    // Return a small stable payload that matches the TvDetails type
    return {
      id: tmdbId,
      name: language === 'zh-CN' ? '示例剧集' : 'Sample Show',
      original_name: 'Sample Show',
      original_language: 'ja',
      overview: 'A mock tv details payload for testing.',
      adult: false,
      backdrop_path: null,
      poster_path: null,
      homepage: '',
      status: 'Returning Series',
      type: 'Scripted',
      in_production: true,
      first_air_date: '2022-01-01',
      last_air_date: '2022-02-01',
      last_episode_to_air: {
        id: 1,
        name: 'Ep1',
        overview: '',
        air_date: '2022-02-01',
        episode_number: 1,
        episode_type: 'standard',
        production_code: '',
        runtime: 24,
        season_number: 1,
        show_id: tmdbId,
        still_path: null,
      },
      next_episode_to_air: null,
      number_of_seasons: 1,
      number_of_episodes: 1,
      episode_run_time: [24],
      languages: ['ja'],
      origin_country: ['JP'],
      popularity: 1,
      vote_average: 7,
      vote_count: 1,
      genres: [{ id: 16, name: '动画' }],
      networks: [{ id: 1, name: 'Mock TV', logo_path: null, origin_country: 'JP' }],
      production_companies: [{ id: 1, name: 'Mock Studio', logo_path: null, origin_country: 'JP' }],
      production_countries: [{ iso_3166_1: 'JP', name: 'Japan' }],
      seasons: [
        {
          air_date: '2022-01-01',
          episode_count: 1,
          id: 10,
          name: 'Season 1',
          overview: '',
          poster_path: null,
          season_number: 1,
        },
      ],
      spoken_languages: [{ english_name: 'Japanese', iso_639_1: 'ja', name: '日本語' }],
      alternative_titles: { results: [] },
      credits: { cast: [], crew: [] },
      images: { backdrops: [], logos: [], posters: [] },
      keywords: { results: [] },
      content_ratings: { results: [{ iso_3166_1: 'US', rating: 'TV-14', descriptors: [] }] },
      recommendations: { page: 1, results: [] },
      similar: { page: 1, results: [] },
      videos: { results: [] },
      external_ids: {
        imdb_id: null,
        freebase_mid: null,
        freebase_id: null,
        tvdb_id: null,
        tvrage_id: null,
        wikidata_id: null,
        facebook_id: null,
        instagram_id: null,
        twitter_id: null,
      },
      ['watch/providers']: {
        results: {
          CN: {
            link: 'https://www.themoviedb.org/tv/' + tmdbId + '/watch?locale=CN',
            flatrate: [
              { logo_path: null, provider_id: 283, provider_name: 'Crunchyroll', display_priority: 1 },
            ],
          },
        },
      },
      translations: {
        translations: [
          {
            iso_3166_1: 'CN',
            iso_639_1: 'zh',
            name: '普通话',
            english_name: 'Mandarin',
            data: { name: '示例剧集', overview: '简介', homepage: '', tagline: '' },
          },
        ],
      },
    }
  }
}
