export type TvSearchResult = {
  adult: boolean
  id: number
  name: string
  original_name: string
  original_language: string
  overview: string
  first_air_date?: string
  poster_path: string | null
  backdrop_path: string | null
  popularity: number
  genre_ids: number[]
  origin_country: string[]
  vote_average: number
  vote_count: number
}

export type SearchTvResponse = {
  page: number
  total_pages: number
  total_results: number
  results: TvSearchResult[]
}
