"use client";

// A Client Component: it needs state (the current slide) and effects (the timer), which only run in the browser.
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { FaChevronLeft, FaChevronRight } from "react-icons/fa6";

import MovieMetaTags from "@/components/movie/MovieMetaTags";
import type { MovieListItem } from "@/lib/api";
import { backdropUrl, posterUrl } from "@/lib/tmdb";

const SLIDE_INTERVAL_MS = 8000;

type HeroCarouselProps = {
  movies: MovieListItem[];
  // Computed on the server: deciding "new" with the browser clock could differ from the server render.
  newReleaseIds: number[];
};

export default function HeroCarousel({ movies, newReleaseIds }: HeroCarouselProps) {
  const [current, setCurrent] = useState(0);
  const [paused, setPaused] = useState(false);
  const count = movies.length;

  useEffect(() => {
    if (paused || count < 2) {
      return;
    }
    // People who turn off animations in their system settings do not get slides moving on their own.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }
    // Depends on `current`, so a manual change restarts the countdown.
    const timer = setTimeout(() => setCurrent((index) => (index + 1) % count), SLIDE_INTERVAL_MS);
    return () => clearTimeout(timer);
  }, [current, paused, count]);

  const goTo = (index: number) => setCurrent((index + count) % count);

  return (
    <section
      aria-roledescription="carousel"
      aria-label="Featured movies"
      className="relative isolate w-full overflow-hidden bg-ink text-paper"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={() => setPaused(false)}
    >
      {/* Every slide sits in the same grid cell, so the carousel is as tall as its tallest slide. */}
      <div className="grid">
        {movies.map((movie, index) => {
          const isActive = index === current;
          const backdrop = backdropUrl(movie.backdrop_path, "w1280");
          const poster = posterUrl(movie.poster_path);
          // Without a backdrop, the poster is used as a blurred background, like the movie page.
          const background = backdrop ?? poster;

          return (
            <div
              key={movie.id}
              role="group"
              aria-roledescription="slide"
              aria-label={`${index + 1} of ${count}`}
              // inert hides the slide from keyboard and screen readers while it is invisible.
              inert={!isActive}
              className={`relative col-start-1 row-start-1 transition-opacity duration-700 motion-reduce:transition-none ${
                isActive ? "opacity-100" : "opacity-0"
              }`}
            >
              {background && (
                <Image
                  src={background}
                  alt=""
                  fill
                  sizes="100vw"
                  preload={index === 0}
                  className={`-z-10 object-cover ${backdrop ? "brightness-50" : "scale-110 blur-2xl brightness-40"}`}
                />
              )}
              <div className="absolute inset-0 -z-10 bg-linear-to-t from-ink via-ink/60 to-ink/20 md:bg-linear-to-r" />

              <div className="container mx-auto flex flex-col items-center gap-6 px-4 pt-10 pb-16 md:flex-row md:gap-12 md:px-16 md:py-20">
                {poster && (
                  <Image
                    src={poster}
                    alt={`${movie.title} poster`}
                    width={500}
                    height={750}
                    sizes="(min-width: 1024px) 16rem, (min-width: 768px) 14rem, 10rem"
                    preload={index === 0}
                    className={`aspect-2/3 h-auto w-40 shrink-0 rounded-2xl border border-paper/10 object-cover shadow-2xl transition-transform duration-700 motion-reduce:transition-none md:w-56 lg:w-64 ${
                      isActive ? "translate-x-0" : "-translate-x-8"
                    }`}
                  />
                )}

                <div
                  className={`flex max-w-2xl flex-col items-center gap-5 rounded-3xl border border-paper/10 bg-paper/5 p-6 text-center backdrop-blur-md transition-transform duration-700 motion-reduce:transition-none md:items-start md:p-10 md:text-left ${
                    isActive ? "translate-y-0" : "translate-y-6"
                  }`}
                >
                  <p className="font-detail text-xs font-semibold tracking-[0.3em] text-brand uppercase md:text-sm">
                    {newReleaseIds.includes(movie.id) ? "New release" : "Now playing"}
                  </p>
                  <h2 className="font-brand text-3xl leading-tight [text-shadow:2px_2px_10px_rgb(0_0_0/0.5)] md:text-5xl lg:text-6xl">
                    {movie.title}
                  </h2>
                  <MovieMetaTags movie={movie} />
                  <Link
                    href={`/movies/${movie.id}`}
                    className="mt-2 rounded-full bg-brand px-8 py-3 font-brand text-lg text-ink shadow-lg shadow-brand/30 transition hover:-translate-y-1 hover:bg-paper motion-reduce:transition-none motion-reduce:hover:translate-y-0"
                  >
                    Get tickets
                  </Link>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {count > 1 && (
        <>
          <button
            type="button"
            onClick={() => goTo(current - 1)}
            aria-label="Previous movie"
            className="absolute top-1/2 left-3 hidden -translate-y-1/2 rounded-full bg-ink/50 p-3 text-paper hover:bg-ink/80 md:block"
          >
            <FaChevronLeft aria-hidden />
          </button>
          <button
            type="button"
            onClick={() => goTo(current + 1)}
            aria-label="Next movie"
            className="absolute top-1/2 right-3 hidden -translate-y-1/2 rounded-full bg-ink/50 p-3 text-paper hover:bg-ink/80 md:block"
          >
            <FaChevronRight aria-hidden />
          </button>

          <div className="absolute inset-x-0 bottom-5 flex justify-center gap-4">
            {movies.map((movie, index) => (
              <button
                key={movie.id}
                type="button"
                onClick={() => goTo(index)}
                aria-label={`Show ${movie.title}`}
                aria-current={index === current}
                className={`size-3 rounded-full border-2 border-brand transition ${
                  index === current ? "scale-125 bg-brand" : "opacity-60 hover:opacity-100"
                }`}
              />
            ))}
          </div>
        </>
      )}
    </section>
  );
}
