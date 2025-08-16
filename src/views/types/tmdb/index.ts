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

// Minimal TV details shape; TMDB returns many fields, keep open-ended
// Common small shapes
export type TvGenre = { id: number; name: string }
export type TvNetwork = { id: number; name: string; logo_path: string | null; origin_country: string }
export type ProductionCompany = { id: number; name: string; logo_path: string | null; origin_country: string }
export type ProductionCountry = { iso_3166_1: string; name: string }
export type SpokenLanguage = { english_name: string; iso_639_1: string; name: string }

export type TvEpisode = {
  id: number
  name: string
  overview: string
  air_date: string | null
  episode_number: number
  episode_type: string
  production_code: string
  runtime: number | null
  season_number: number
  show_id: number
  still_path: string | null
  vote_average?: number
  vote_count?: number
}

export type TvSeasonSummary = {
  air_date: string | null
  episode_count: number
  id: number
  name: string
  overview: string
  poster_path: string | null
  season_number: number
  vote_average?: number
}

export type CreditCast = {
  adult: boolean
  gender: number | null
  id: number
  known_for_department?: string
  name: string
  original_name?: string
  popularity?: number
  profile_path: string | null
  character?: string
  credit_id?: string
  order?: number
}

export type CreditCrew = {
  adult: boolean
  gender: number | null
  id: number
  known_for_department?: string
  name: string
  original_name?: string
  popularity?: number
  profile_path: string | null
  credit_id?: string
  department?: string
  job?: string
}

export type Credits = { cast: CreditCast[]; crew: CreditCrew[] }

export type ImageItem = {
  aspect_ratio: number
  height: number
  iso_639_1: string | null
  file_path: string
  vote_average: number
  vote_count: number
  width: number
}
export type Images = { backdrops: ImageItem[]; logos: ImageItem[]; posters: ImageItem[] }

export type Keyword = { id: number; name: string }
export type Keywords = { results: Keyword[] }

export type ContentRating = { iso_3166_1: string; rating: string; descriptors?: string[] }
export type ContentRatings = { results: ContentRating[] }

export type Recommendation = TvSearchResult & { media_type?: string }
export type Recommendations = { page: number; results: Recommendation[]; total_pages?: number; total_results?: number }

export type Video = {
  id: string
  key: string
  name: string
  site: string
  size: number
  type: string
  official?: boolean
  published_at?: string
}

export type ExternalIds = {
  imdb_id: string | null
  freebase_mid: string | null
  freebase_id: string | null
  tvdb_id: number | null
  tvrage_id: number | null
  wikidata_id: string | null
  facebook_id: string | null
  instagram_id: string | null
  twitter_id: string | null
}

export type WatchProviderEntry = { logo_path: string | null; provider_id: number; provider_name: string; display_priority: number }
export type WatchProviderCountry = {
  link?: string
  flatrate?: WatchProviderEntry[]
  buy?: WatchProviderEntry[]
  rent?: WatchProviderEntry[]
  ads?: WatchProviderEntry[]
  free?: WatchProviderEntry[]
}
export type WatchProviders = { results: Record<string, WatchProviderCountry> }

export type AlternativeTitle = { iso_3166_1: string; title: string; type: string }
export type AlternativeTitles = { results: AlternativeTitle[] }

export type TranslationData = { name: string; overview: string; homepage: string; tagline: string }
export type TranslationEntry = {
  iso_3166_1: string
  iso_639_1: string
  name: string
  english_name: string
  data: TranslationData
}
export type Translations = { translations: TranslationEntry[] }

// Full(er) TV details shape. Some fields left optional to accommodate API variance.
export type TvDetails = {
  // Core
  id: number
  name: string
  original_name: string
  original_language: string
  overview: string
  adult: boolean
  backdrop_path: string | null
  poster_path: string | null
  homepage: string | null
  status: string
  type: string
  in_production: boolean
  first_air_date: string | null
  last_air_date: string | null
  last_episode_to_air: TvEpisode | null
  next_episode_to_air: TvEpisode | null
  number_of_seasons: number
  number_of_episodes: number
  episode_run_time: number[]
  languages: string[]
  origin_country: string[]
  popularity: number
  vote_average: number
  vote_count: number
  genres: TvGenre[]
  networks: TvNetwork[]
  production_companies: ProductionCompany[]
  production_countries: ProductionCountry[]
  seasons: TvSeasonSummary[]
  spoken_languages: SpokenLanguage[]

  // Appended
  alternative_titles?: AlternativeTitles
  credits?: Credits
  images?: Images
  keywords?: Keywords
  content_ratings?: ContentRatings
  recommendations?: Recommendations
  similar?: Recommendations
  videos?: { results: Video[] }
  external_ids?: ExternalIds
  ['watch/providers']?: WatchProviders
  translations?: Translations
}
