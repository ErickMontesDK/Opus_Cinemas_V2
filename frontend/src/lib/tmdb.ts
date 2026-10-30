const POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500";

export function posterUrl(path: string): string | null {
  return path ? `${POSTER_BASE_URL}${path}` : null;
}
