import { connection } from "next/server";

import MovieCard from "@/components/MovieCard";
import HeroCarousel from "@/components/home/HeroCarousel";
import PromoCards from "@/components/home/PromoCards";
import SectionHeading from "@/components/home/SectionHeading";
import { getMovies, getShowtimesOn, type Showtime } from "@/lib/api";
import { isNewRelease, localDateKey } from "@/lib/format";

const FEATURED_MOVIES = 3;
const PRELOADED_POSTERS = 3;

export default async function Home() {
  await connection();
  const todayKey = localDateKey(new Date().toISOString());
  // Both requests are independent, so they run at the same time instead of one after the other.
  const [movies, todayShowtimes] = await Promise.all([getMovies(), getShowtimesOn(todayKey)]);

  // The most recent releases are featured; movies without a date go last.
  const featured = [...movies]
    .sort((a, b) => (b.release_date ?? "").localeCompare(a.release_date ?? ""))
    .slice(0, FEATURED_MOVIES);
  const newReleaseIds = movies.filter((movie) => isNewRelease(movie.release_date)).map((movie) => movie.id);

  const showtimesByMovie: Record<number, Showtime[]> = {};
  for (const showtime of todayShowtimes) {
    (showtimesByMovie[showtime.movie] ??= []).push(showtime);
  }

  return (
    <div className="flex w-full flex-col">
      <h1 className="sr-only">Opus Cinemas: movies now playing in Vancouver</h1>

      {featured.length > 0 && <HeroCarousel movies={featured} newReleaseIds={newReleaseIds} />}

      <section aria-labelledby="promotions-heading" className="bg-ink text-paper">
        <div className="container mx-auto px-4 pt-4 pb-12 md:pb-16">
          <SectionHeading id="promotions-heading">Enjoy the experience</SectionHeading>
          <PromoCards />
        </div>
      </section>

      {/* flex-1 lets the last section fill tall screens, so no strip of the yellow body shows above the footer. */}
      <section aria-labelledby="now-playing-heading" className="flex-1 bg-paper text-ink">
        <div className="container mx-auto px-4 py-12 md:py-16">
          <SectionHeading id="now-playing-heading">Now playing</SectionHeading>

          {movies.length === 0 ? (
            <p>No movies showing right now. Please check back soon.</p>
          ) : (
            <ul className="grid gap-4 md:grid-cols-2 md:gap-6 xl:grid-cols-3">
              {movies.map((movie, index) => (
                <li key={movie.id}>
                  <MovieCard
                    movie={movie}
                    todayShowtimes={showtimesByMovie[movie.id] ?? []}
                    todayKey={todayKey}
                    isNew={newReleaseIds.includes(movie.id)}
                    preload={index < PRELOADED_POSTERS}
                  />
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}
