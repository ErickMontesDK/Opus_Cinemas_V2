import type { MovieListItem } from "@/lib/api";
import { formatRuntime } from "@/lib/format";

type MovieMetaTagsProps = {
  movie: MovieListItem;
};

export default function MovieMetaTags({ movie }: MovieMetaTagsProps) {
  const runtime = formatRuntime(movie.runtime);
  const tags = [movie.classification, runtime, ...movie.genres].filter(Boolean);

  return (
    <ul className="flex flex-wrap justify-center gap-2 md:justify-start">
      {tags.map((tag) => (
        <li
          key={tag}
          className="rounded-full border border-brand/20 bg-paper/10 px-3 py-1 font-detail text-xs font-semibold text-brand"
        >
          {tag}
        </li>
      ))}
    </ul>
  );
}
