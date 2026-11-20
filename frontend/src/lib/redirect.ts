// Only paths on this site: "//evil.com" or "/\evil.com" would send the user to another site (open redirect).
export function safeNextPath(next: unknown): string {
  if (typeof next === "string" && next.startsWith("/") && !next.startsWith("//") && !next.startsWith("/\\")) {
    return next;
  }
  return "/";
}

// Adds ?next= to an auth page link, so the user comes back to the same page after logging in.
export function withNext(path: string, next: string): string {
  return next === "/" ? path : `${path}?next=${encodeURIComponent(next)}`;
}
