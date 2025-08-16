import type { SearchTvResponse } from '@/types/tmdb'

export default interface ITmdbProvider {
  /**
   * Search TV shows by name
   * @param query Search keywords
   * @param page Page number (default 1)
   * @param language Result language (default 'zh-CN')
   */
  searchTv(query: string, page?: number, language?: string): Promise<SearchTvResponse>
}

