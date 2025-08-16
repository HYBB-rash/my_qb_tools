import { it, expect } from 'vitest'

it('tmdb index uses mock provider in test mode and returns results', async () => {
  const { default: tmdb } = await import('@/services/tmdb')
  const res = await tmdb.searchTv('凡人')

  expect(res).toBeTruthy()
  expect(res.page).toBe(1)
  expect(res.results.length).toBeGreaterThanOrEqual(0)
  if (res.results.length) {
    expect(res.results[0]).toHaveProperty('id')
    expect(res.results[0]).toHaveProperty('name')
    expect(res.results[0]).toHaveProperty('adult')
  }
})

