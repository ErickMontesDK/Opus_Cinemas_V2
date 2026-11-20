import "server-only";

import { cookies } from "next/headers";
import { cache } from "react";

import type { User } from "@/lib/auth";

const API_URL = process.env.API_URL;

// cache() shares one /api/me/ call per request between the header and the page.
export const getCurrentUser = cache(async (): Promise<User | null> => {
  const access = (await cookies()).get("access");
  if (!access) {
    return null;
  }

  // Server-to-server call: the browser's cookies are not sent automatically, so forward the token.
  const response = await fetch(`${API_URL}/api/me/`, {
    headers: { Cookie: `access=${access.value}` },
    signal: AbortSignal.timeout(5000),
  });
  if (response.status === 401) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`GET /api/me/ failed with status ${response.status}`);
  }
  return response.json();
});
