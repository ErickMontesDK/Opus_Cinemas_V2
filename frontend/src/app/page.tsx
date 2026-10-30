import { connection } from "next/server";

import MovieCard from "@/components/MovieCard";
import { getMovies } from "@/lib/api";

const PRELOADED_POSTERS = 4;

export default async function Home() {
  await connection();
  const movies = await getMovies();

  return (
    <section className="container mx-auto w-full px-4 py-8">
      <h1 className="mb-6 font-brand text-3xl md:text-4xl">Now showing</h1>

      {movies.length === 0 ? (
        <p>No movies showing right now. Please check back soon.</p>
      ) : (
        <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:gap-6 lg:grid-cols-4 xl:grid-cols-5">
          {movies.map((movie, index) => (
            <li key={movie.id}>
              <MovieCard movie={movie} preload={index < PRELOADED_POSTERS} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
