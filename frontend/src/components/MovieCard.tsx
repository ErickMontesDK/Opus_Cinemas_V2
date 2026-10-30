import Image from "next/image";

import type { MovieListItem } from "@/lib/api";
import { posterUrl } from "@/lib/tmdb";
import {formatRuntime} from "@/lib/format";

type MovieCardProps = {
  movie: MovieListItem;
  preload?: boolean;
};

export default function MovieCard({ movie, preload = false }: MovieCardProps) {
  const poster = posterUrl(movie.poster_path);
  const runtime = formatRuntime(movie.runtime);

  return (
    <article className="flex flex-col gap-2">
      {poster ? (
        <Image
          src={poster}
          alt={`${movie.title} poster`}
          width={500}
          height={750}
          sizes="(min-width: 1280px) 20vw, (min-width: 1024px) 25vw, (min-width: 640px) 33vw, 50vw"
          preload={preload}
          className="aspect-2/3 h-auto w-full rounded-md object-cover shadow-md"
        />
      ) : (
        <div className="flex aspect-2/3 w-full items-center justify-center rounded-md bg-ink p-4 text-center font-brand text-brand shadow-md">
          {movie.title}
        </div>
      )}

      <h2 className="font-detail text-sm leading-tight font-bold">{movie.title}</h2>

      <p className="flex flex-wrap items-center gap-2 text-xs text-ink-soft">
        {movie.classification && (
          <span className="rounded border border-ink-soft px-1">{movie.classification}</span>
        )}
        <span>{movie.genres.join(", ")}</span>
        {runtime && (
          <span>
            {runtime}
          </span>
        )}
      </p>
    </article>
  );
}
