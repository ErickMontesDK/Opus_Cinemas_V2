import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";

import MovieMetaTags from "@/components/movie/MovieMetaTags";
import ShowtimeTabs from "@/components/movie/ShowtimeTabs";
import TrailerEmbed from "@/components/movie/TrailerEmbed";
import { getMovie, getShowtimes } from "@/lib/api";
import { formatReleaseDate, groupShowtimesByDate } from "@/lib/format";
import { backdropUrl, posterUrl } from "@/lib/tmdb";

export async function generateMetadata({ params }: PageProps<"/movies/[id]">): Promise<Metadata> {
  const { id } = await params;
  const movie = await getMovie(id);
  if (!movie) {
    return { title: "Movie not found" };
  }
  return { title: movie.title, description: movie.synopsis || undefined };
}

export default async function MoviePage({ params, searchParams }: PageProps<"/movies/[id]">) {
  const { id } = await params;
  const movie = await getMovie(id);
  if (!movie) {
    notFound();
  }

  const [showtimes, { date }] = await Promise.all([getShowtimes(movie.id), searchParams]);
  const groups = groupShowtimesByDate(showtimes);
  const poster = posterUrl(movie.poster_path);
  const backdrop = backdropUrl(movie.backdrop_path);
  const releaseDate = formatReleaseDate(movie.release_date);

  return (
    // isolate keeps the -z-10 background layers behind this page only, not behind the header.
    <div className="relative isolate w-full overflow-hidden bg-ink text-paper">
      {backdrop && (
        <Image
          src={backdrop}
          alt=""
          fill
          sizes="100vw"
          className="-z-10 scale-110 object-cover blur-2xl brightness-40 saturate-125"
        />
      )}
      <div className="absolute inset-0 -z-10 bg-radial from-transparent to-ink/80" />

      <div className="container mx-auto grid gap-6 px-4 py-8 lg:grid-cols-[3fr_2fr] lg:items-start lg:gap-10 lg:py-12">
        <article className="flex flex-col gap-8 rounded-3xl border border-paper/10 bg-ink/60 p-5 shadow-2xl backdrop-blur-xl md:p-8">
          <div className="flex flex-col items-center gap-6 md:flex-row md:items-start">
            {poster ? (
              <Image
                src={poster}
                alt={`${movie.title} poster`}
                width={500}
                height={750}
                sizes="(min-width: 768px) 14rem, 12rem"
                preload
                className="aspect-2/3 h-auto w-48 shrink-0 rounded-2xl border border-paper/10 object-cover shadow-2xl md:w-56"
              />
            ) : (
              <div className="flex aspect-2/3 w-48 shrink-0 items-center justify-center rounded-2xl bg-ink p-4 font-brand text-brand md:w-56">
                {movie.title}
              </div>
            )}

            <div className="flex flex-col gap-6">
              <header className="flex flex-col gap-4 text-center md:text-left">
                <h1 className="font-brand text-3xl leading-tight md:text-5xl">{movie.title}</h1>
                <MovieMetaTags movie={movie} />
                {releaseDate && <p className="text-sm text-paper/60">Release date: {releaseDate}</p>}
              </header>

              {movie.synopsis && (
                <section className="flex flex-col gap-2">
                  <h2 className="font-detail text-sm tracking-widest text-brand uppercase">Synopsis</h2>
                  <p className="leading-relaxed text-paper/80">{movie.synopsis}</p>
                </section>
              )}
            </div>
          </div>

          <TrailerEmbed trailer={movie.trailer} title={movie.title} />
        </article>

        <section className="flex flex-col gap-6 rounded-3xl border border-paper/10 bg-ink/60 p-5 shadow-2xl backdrop-blur-xl md:p-8">
          <h2 className="font-brand text-2xl md:text-3xl">Showtimes</h2>
          <ShowtimeTabs
            movieId={movie.id}
            groups={groups}
            selectedDate={typeof date === "string" ? date : undefined}
          />
        </section>
      </div>
    </div>
  );
}
