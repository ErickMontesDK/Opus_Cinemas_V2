import type { Showtime } from "@/lib/api";

// The server may run in UTC (Vercel does), so showtimes are always formatted in the cinema's time zone.
const CINEMA_TIME_ZONE = "America/Vancouver";

export type ShowtimeGroup = {
    date: string;
    showtimes: Showtime[];
};

export const formatRuntime = (runtime: number | null): string => {
    if (runtime === null) {
        return "";
    }

    const hours = Math.floor(runtime / 60);
    const minutes = runtime % 60;
    let formattedRuntime = "";

    if (hours > 0) {
        formattedRuntime = `${hours}h`;
    }
    if (minutes > 0) {
        formattedRuntime += ` ${minutes}m`;
    }

    return formattedRuntime.trim();

};

// The en-CA locale writes dates as YYYY-MM-DD, the same format as the API's ?date= filter.
const dateKeyFormatter = new Intl.DateTimeFormat("en-CA", {
    timeZone: CINEMA_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
});

const timeFormatter = new Intl.DateTimeFormat("en-US", {
    timeZone: CINEMA_TIME_ZONE,
    hour: "numeric",
    minute: "2-digit",
});

// "2026-11-06" is a calendar day, not an instant: formatting it in UTC keeps it on the same day.
const calendarDayFormatter = new Intl.DateTimeFormat("en-US", {
    timeZone: "UTC",
    weekday: "short",
    month: "short",
    day: "numeric",
});

const releaseDateFormatter = new Intl.DateTimeFormat("en-US", {
    timeZone: "UTC",
    year: "numeric",
    month: "long",
    day: "numeric",
});

export const localDateKey = (dateTime: string): string => dateKeyFormatter.format(new Date(dateTime));

export const formatShowtimeTime = (dateTime: string): string => timeFormatter.format(new Date(dateTime));

export const formatDayLabel = (dateKey: string): string => calendarDayFormatter.format(new Date(dateKey));

export const formatReleaseDate = (releaseDate: string | null): string =>
    releaseDate ? releaseDateFormatter.format(new Date(releaseDate)) : "";

const NEW_RELEASE_DAYS = 14;
const MS_PER_DAY = 24 * 60 * 60 * 1000;

// Both dates are YYYY-MM-DD strings parsed as UTC midnight, so the difference is a whole number of days.
export const isNewRelease = (releaseDate: string | null, now: Date = new Date()): boolean => {
    if (!releaseDate) {
        return false;
    }
    const daysSinceRelease = (Date.parse(dateKeyFormatter.format(now)) - Date.parse(releaseDate)) / MS_PER_DAY;
    return daysSinceRelease >= 0 && daysSinceRelease < NEW_RELEASE_DAYS;
};

export const groupShowtimesByDate = (showtimes: Showtime[]): ShowtimeGroup[] => {
    const groupedShowtimes: Record<string, Showtime[]> = {};

    for (const showtime of showtimes) {
        const dateKey = localDateKey(showtime.starts_at);
        (groupedShowtimes[dateKey] ??= []).push(showtime);
    }

    // Sorted here so the days do not depend on the order the API returns.
    return Object.entries(groupedShowtimes)
        .map(([date, dayShowtimes]) => ({ date, showtimes: dayShowtimes }))
        .sort((a, b) => a.date.localeCompare(b.date));
};
