import { it, expect, vi, beforeEach } from 'vitest'

beforeEach(() => {
  vi.stubEnv('VITE_USE_MOCK_TMDB', 'false')
  vi.stubEnv('VITE_TMDB_PROXY', 'false')
  vi.stubEnv('VITE_TMDB_API_TOKEN', 'FAKE_TOKEN')
})

it('TmdbProvider.getTvDetails calls axios with correct route and params and returns typed shape', async () => {
  const h = vi.hoisted(() => {
    const payload = {
      id: 123,
      name: 'Demo Show',
      original_name: 'Demo Show',
      original_language: 'ja',
      overview: 'overview',
      adult: false,
      backdrop_path: null,
      poster_path: null,
      homepage: '',
      status: 'Returning Series',
      type: 'Scripted',
      in_production: true,
      first_air_date: '2022-01-01',
      last_air_date: '2022-02-01',
      last_episode_to_air: null,
      next_episode_to_air: {
        id: 999,
        name: 'Next',
        overview: '',
        air_date: '2025-08-22',
        episode_number: 8,
        episode_type: 'standard',
        production_code: '',
        runtime: 24,
        season_number: 3,
        show_id: 123,
        still_path: null,
      },
      number_of_seasons: 3,
      number_of_episodes: 26,
      episode_run_time: [24],
      languages: ['ja'],
      origin_country: ['JP'],
      popularity: 10,
      vote_average: 6.7,
      vote_count: 26,
      genres: [{ id: 16, name: '动画' }],
      networks: [],
      production_companies: [],
      production_countries: [],
      seasons: [],
      spoken_languages: [],
      alternative_titles: { results: [] },
      credits: { cast: [], crew: [] },
      images: { backdrops: [], logos: [], posters: [] },
      keywords: { results: [] },
      content_ratings: { results: [{ iso_3166_1: 'US', rating: 'TV-14', descriptors: [] }] },
      recommendations: { page: 1, results: [] },
      similar: { page: 1, results: [] },
      videos: { results: [] },
      external_ids: {
        imdb_id: 'tt22443832',
        freebase_mid: null,
        freebase_id: null,
        tvdb_id: 411800,
        tvrage_id: null,
        wikidata_id: 'Q114565614',
        facebook_id: 'ArknightsGlobal',
        instagram_id: 'arknights_messenger_official',
        twitter_id: 'ArknightsStaff',
      },
      ['watch/providers']: {
        results: {
          US: {
            link: 'https://www.themoviedb.org/tv/123/watch?locale=US',
            flatrate: [
              { logo_path: '/fzN5Jok5Ig1eJ7gyNGoMhnLSCfh.jpg', provider_id: 283, provider_name: 'Crunchyroll', display_priority: 7 },
            ],
          },
        },
      },
      translations: { translations: [] },
    }
    const get = vi.fn(async () => ({ data: payload }))
    const create = vi.fn(() => ({ get }))
    return { get, create, payload }
  })

  vi.mock('axios', () => ({ default: { create: h.create } }))

  const { default: TmdbProvider } = await import('./TmdbProvider')
  const tmdb = TmdbProvider.getInstance()

  const res = await tmdb.getTvDetails(123, 'en-US', 'US')

  expect(res.id).toBe(123)
  expect(res.name).toBe('Demo Show')
  expect(h.get).toHaveBeenCalledTimes(1)
  const getCalls: any[] = h.get.mock.calls as any
  expect(getCalls[0][0]).toBe('/tv/123')
  const params = getCalls[0][1].params
  expect(params.language).toBe('en-US')
  expect(params.watch_region).toBe('US')
  expect(typeof params.append_to_response).toBe('string')
  // spot-check a few appends
  expect(params.append_to_response).toContain('credits')
  expect(params.append_to_response).toContain('watch/providers')

  expect(h.create).toHaveBeenCalledTimes(1)
  const createCalls: any[] = h.create.mock.calls as any
  const arg = createCalls[0][0]
  expect(arg.baseURL).toBe('https://api.themoviedb.org/3')
  expect(arg.headers.Accept).toBe('application/json')
  expect(arg.headers.Authorization).toBe('Bearer FAKE_TOKEN')

  // Validate typed nested bits from actual TMDB responses
  expect(res.next_episode_to_air && res.next_episode_to_air.season_number).toBe(3)
  expect(res.content_ratings && res.content_ratings.results[0].iso_3166_1).toBe('US')
  // watch/providers comes back under a slash key; use bracket notation
  const wp = res['watch/providers']
  expect(wp).toBeTruthy()
  expect(wp && 'US' in wp.results).toBe(true)
})
