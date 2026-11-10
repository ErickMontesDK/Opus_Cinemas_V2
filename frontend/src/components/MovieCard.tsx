import Image from "next/image";
import Link from "next/link";

import type { MovieListItem, Showtime } from "@/lib/api";
import { formatRuntime, formatShowtimeTime } from "@/lib/format";
import { posterUrl } from "@/lib/tmdb";

// More chips would wrap onto several lines on small cards; the rest are on the movie page.
const MAX_TIMES = 4;

type MovieCardProps = {
  movie: MovieListItem;
  todayShowtimes: Showtime[];
  todayKey: string;
  isNew?: boolean;
  preload?: boolean;
};

export default function MovieCard({ movie, todayShowtimes, todayKey, isNew = false, preload = false }: MovieCardProps) {
  const poster = posterUrl(movie.poster_path);
  const runtime = formatRuntime(movie.runtime);
  const href = `/movies/${movie.id}`;
  const visibleTimes = todayShowtimes.slice(0, MAX_TIMES);
  const hiddenCount = todayShowtimes.length - visibleTimes.length;

  return (
    // Not one big link: the time chips are links too, and links cannot be nested.
    <article className="group flex h-full overflow-hidden rounded-2xl bg-ink text-paper shadow-lg transition duration-300 hover:-translate-y-1 hover:shadow-2xl motion-reduce:transition-none motion-reduce:hover:translate-y-0">
      <Link href={href} tabIndex={-1} aria-hidden className="relative w-32 shrink-0 sm:w-36">
        {poster ? (
          <Image
            src={poster}
            alt=""
            fill
            sizes="9rem"
            preload={preload}
            className="object-cover transition-transform duration-500 group-hover:scale-105 motion-reduce:transition-none"
          />
        ) : (
          <div className="flex h-full items-center justify-center bg-ink-soft p-2 text-center font-brand text-sm text-brand">
            {movie.title}
          </div>
        )}
      </Link>

      <div className="flex min-w-0 flex-1 flex-col gap-2 p-4">
        {isNew && (
          <p className="font-detail text-[0.65rem] font-semibold tracking-widest text-accent uppercase">New release</p>
        )}
        <h3 className="font-brand text-lg leading-tight">
          <Link href={href} className="hover:text-brand">
            {movie.title}
          </Link>
        </h3>

        <p className="flex flex-wrap items-center gap-2 text-xs text-paper/70">
          {movie.classification && (
            <span className="rounded border border-paper/30 px-1">{movie.classification}</span>
          )}
          {runtime && <span>{runtime}</span>}
        </p>
        <p className="line-clamp-1 text-xs text-paper/50">{movie.genres.join(", ")}</p>

        <div className="mt-auto pt-2">
          <p className="mb-2 font-detail text-[0.65rem] tracking-widest text-paper/50 uppercase">Today</p>
          {visibleTimes.length > 0 ? (
            <ul className="flex flex-wrap gap-2">
              {visibleTimes.map((showtime) => (
                <li key={showtime.id}>
                  <Link
                    href={{ pathname: href, query: { date: todayKey } }}
                    className="block rounded-full border border-brand/40 px-3 py-1 font-detail text-xs text-brand transition-colors hover:bg-brand hover:text-ink"
                  >
                    <time dateTime={showtime.starts_at}>{formatShowtimeTime(showtime.starts_at)}</time>
                  </Link>
                </li>
              ))}
              {hiddenCount > 0 && (
                <li>
                  <Link href={href} className="block px-1 py-1 font-detail text-xs text-paper/60 hover:text-brand">
                    +{hiddenCount} more
                  </Link>
                </li>
              )}
            </ul>
          ) : (
            <Link href={href} className="font-detail text-xs text-brand hover:underline">
              See upcoming showtimes
            </Link>
          )}
        </div>
      </div>
    </article>
  );
}
