import { it, expect, vi, beforeEach } from 'vitest'

beforeEach(() => {
  // Ensure we don't go through index selector or use proxy in this unit test
  vi.stubEnv('VITE_USE_MOCK_TMDB', 'false')
  vi.stubEnv('VITE_TMDB_PROXY', 'false')
  vi.stubEnv('VITE_TMDB_API_TOKEN', 'FAKE_TOKEN')
})

it('TmdbProvider.searchTv calls axios with correct route and params', async () => {
  const h = vi.hoisted(() => {
    const payload = {
      page: 1,
      total_pages: 1,
      total_results: 1,
      results: [
        {
          adult: false,
          id: 123,
          name: 'Demo Show',
          original_name: 'Demo Show',
          original_language: 'en',
          overview: 'demo',
          first_air_date: '2020-01-01',
          poster_path: null,
          backdrop_path: null,
          popularity: 1,
          genre_ids: [18],
          origin_country: ['US'],
          vote_average: 8,
          vote_count: 10,
        },
      ],
    }
    const get = vi.fn(async () => ({ data: payload }))
    const create = vi.fn(() => ({ get }))
    return { get, create, payload }
  })

  vi.mock('axios', () => ({ default: { create: h.create } }))

  const { default: TmdbProvider } = await import('./TmdbProvider')
  const tmdb = TmdbProvider.getInstance()

  const res = await tmdb.searchTv('demo', 1, 'zh-CN')

  expect(res.total_results).toBe(1)
  expect(res.results[0].name).toBe('Demo Show')
  expect(h.get).toHaveBeenCalledTimes(1)
  const getCalls: any[] = h.get.mock.calls as any
  expect(getCalls[0][0]).toBe('/search/tv')
  expect(getCalls[0][1]).toMatchObject({ params: { query: 'demo', page: 1, language: 'zh-CN', include_adult: false } })
  expect(h.create).toHaveBeenCalledTimes(1)
  const createCalls: any[] = h.create.mock.calls as any
  const arg = createCalls[0][0]
  expect(arg.baseURL).toBe('https://api.themoviedb.org/3')
  expect(arg.headers.Accept).toBe('application/json')
  expect(arg.headers.Authorization).toBe('Bearer FAKE_TOKEN')
})
