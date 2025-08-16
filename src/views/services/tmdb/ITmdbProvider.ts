import type { SearchTvResponse, TvDetails } from '@/types/tmdb'

export default interface ITmdbProvider {
  /**
   * Search TV shows by name
   * @param query Search keywords
   * @param page Page number (default 1)
   * @param language Result language (default 'zh-CN')
  */
  searchTv(query: string, page?: number, language?: string): Promise<SearchTvResponse>

  /**
   * Get TV show full details by tmdb id
   * @param tmdbId TMDB tv id
   * @param language Result language (default 'zh-CN')
   * @param watchRegion Watch region for providers (default 'CN')
   */
  getTvDetails(tmdbId: number, language?: string, watchRegion?: string): Promise<TvDetails>
}
