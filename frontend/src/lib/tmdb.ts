const IMAGE_BASE_URL = "https://image.tmdb.org/t/p";

export function posterUrl(path: string): string | null {
  return path ? `${IMAGE_BASE_URL}/w500${path}` : null;
}

// The backdrop is shown blurred, so a medium size is enough.
export function backdropUrl(path: string): string | null {
  return path ? `${IMAGE_BASE_URL}/w780${path}` : null;
}
