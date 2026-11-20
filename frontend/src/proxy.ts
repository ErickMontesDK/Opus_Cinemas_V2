import { type NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL;

// Server Components cannot write cookies, so an expired access token is renewed here, before the page renders.
export async function proxy(request: NextRequest) {
  const { cookies } = request;
  const csrfToken = cookies.get("csrftoken")?.value;
  if (cookies.has("access") || !cookies.has("refresh") || !csrfToken) {
    return NextResponse.next();
  }

  let refreshed: Response;
  try {
    refreshed = await fetch(`${API_URL}/api/auth/refresh/`, {
      method: "POST",
      headers: {
        Cookie: request.headers.get("cookie") ?? "",
        "X-CSRFToken": csrfToken,
        // Django checks Origin against CSRF_TRUSTED_ORIGINS, as it does for browser requests.
        Origin: request.nextUrl.origin,
      },
      signal: AbortSignal.timeout(5000),
    });
  } catch {
    return NextResponse.next();
  }
  // Keep the cookies on failure: a parallel request may have rotated them already (docs/AUTH.md).
  if (!refreshed.ok) {
    return NextResponse.next();
  }

  const setCookies = refreshed.headers.getSetCookie();
  // The page in this same request must already see the new tokens.
  for (const setCookie of setCookies) {
    const [pair] = setCookie.split(";");
    const separator = pair.indexOf("=");
    request.cookies.set(pair.slice(0, separator), pair.slice(separator + 1));
  }

  const response = NextResponse.next({ request: { headers: request.headers } });
  for (const setCookie of setCookies) {
    response.headers.append("set-cookie", setCookie);
  }
  return response;
}

export const config = {
  matcher: [
    {
      // Pages only: not the /api rewrite, build output, optimized images or files such as favicon.ico.
      source: "/((?!api|_next/static|_next/image|.*\\..*).*)",
      // Link prefetches run in parallel and would race each other to rotate the same refresh token.
      missing: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },
  ],
};
