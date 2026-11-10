import { cache } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export type MovieListItem = {
  id: number;
  title: string;
  poster_path: string;
  classification: string;
  runtime: number | null;
  genres: string[];
};

export type MovieDetail = MovieListItem & {
  synopsis: string;
  release_date: string | null;
  backdrop_path: string;
  trailer: string;
};

export type Showtime = {
  id: number;
  movie: number;
  auditorium: string;
  starts_at: string;
  ends_at: string;
  base_price: string;
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

// cache() shares one request between generateMetadata and the page: Next does not dedupe a fetch that has a signal.
export const getMovie = cache(async (id: string): Promise<MovieDetail | null> => {
  // Only digits reach the URL, so an id like "../health" cannot point to another endpoint.
  if (!/^\d+$/.test(id)) {
    return null;
  }

  const response = await fetch(`${API_URL}/api/movies/${id}/`, {
    signal: AbortSignal.timeout(5000),
  });
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`GET /api/movies/${id}/ failed with status ${response.status}`);
  }
  return response.json();
});

export async function getShowtimes(movieId: number): Promise<Showtime[]> {
  const response = await fetch(`${API_URL}/api/showtimes/?movie=${movieId}`, {
    signal: AbortSignal.timeout(5000),
  });
  if (!response.ok) {
    throw new Error(`GET /api/showtimes/?movie=${movieId} failed with status ${response.status}`);
  }
  return response.json();
}
