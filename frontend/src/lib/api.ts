const API_URL = process.env.NEXT_PUBLIC_API_URL;

export type MovieListItem = {
  id: number;
  title: string;
  poster_path: string;
  classification: string;
  runtime: number | null;
  genres: string[];
};


export async function getMovies(): Promise<MovieListItem[]> {
  const response = await fetch(`${API_URL}/api/movies/`, {

    signal: AbortSignal.timeout(5000),
  });
  if (!response.ok) {
    throw new Error(`GET /api/movies/ failed with status ${response.status}`);
  }
  return response.json();
}
