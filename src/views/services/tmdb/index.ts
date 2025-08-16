import ITmdbProvider from './ITmdbProvider'
import MockTmdbProvider from './MockProvider'
import TmdbProvider from './TmdbProvider'

const useMock =
  import.meta.env.MODE === 'demo' ||
  import.meta.env.MODE === 'test' ||
  import.meta.env.VITE_USE_MOCK_TMDB === 'true'

const tmdb: ITmdbProvider = useMock ? MockTmdbProvider.getInstance() : TmdbProvider.getInstance()

export default tmdb
