import Link from "next/link";

import { formatDayLabel, formatShowtimeTime, type ShowtimeGroup } from "@/lib/format";

type ShowtimeTabsProps = {
  movieId: number;
  groups: ShowtimeGroup[];
  selectedDate?: string;
};

export default function ShowtimeTabs({ movieId, groups, selectedDate }: ShowtimeTabsProps) {
  // A missing or unknown ?date= falls back to the first day with showtimes.
  const selectedGroup = groups.find((group) => group.date === selectedDate) ?? groups[0];

  if (!selectedGroup) {
    return <p className="py-8 text-center text-paper/60 italic">No upcoming showtimes for this movie.</p>;
  }

  return (
    <div className="flex flex-col gap-6">
      <nav aria-label="Showtime dates">
        <ul className="flex gap-2 overflow-x-auto rounded-2xl bg-ink/40 p-1">
          {groups.map((group) => {
            const isSelected = group.date === selectedGroup.date;
            return (
              <li key={group.date} className="shrink-0">
                {/* scroll={false} keeps the scroll position when the visitor switches days. */}
                <Link
                  href={{ pathname: `/movies/${movieId}`, query: { date: group.date } }}
                  scroll={false}
                  aria-current={isSelected ? "page" : undefined}
                  className={`block rounded-xl px-4 py-3 font-detail text-xs ${
                    isSelected ? "bg-brand text-ink shadow-md" : "text-paper hover:bg-paper/10"
                  }`}
                >
                  {formatDayLabel(group.date)}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {selectedGroup.showtimes.map((showtime) => (
          <li
            key={showtime.id}
            className="flex flex-col items-center gap-1 rounded-xl border border-paper/10 bg-paper/5 p-4"
          >
            <time dateTime={showtime.starts_at} className="font-detail font-bold">
              {formatShowtimeTime(showtime.starts_at)}
            </time>
            <span className="text-xs text-paper/60">{showtime.auditorium}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
