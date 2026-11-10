const IMAGE_BASE_URL = "https://image.tmdb.org/t/p";

export function posterUrl(path: string): string | null {
  return path ? `${IMAGE_BASE_URL}/w500${path}` : null;
}

// w780 is enough for a blurred background; the home hero shows it sharp and full width, so it asks for w1280.
export function backdropUrl(path: string, size: "w780" | "w1280" = "w780"): string | null {
  return path ? `${IMAGE_BASE_URL}/${size}${path}` : null;
}
