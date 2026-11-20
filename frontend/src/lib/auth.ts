// Browser-only helpers (they read document.cookie): import them from Client Components only.

export type User = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
};

export type AuthErrors = {
  form?: string;
  fields: Record<string, string>;
};

export type AuthResult = { ok: true; user: User } | { ok: false; errors: AuthErrors };

export type RegisterData = {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
};

const CSRF_COOKIE = "csrftoken";
const NETWORK_ERROR = "Could not reach the server. Please try again.";
const SERVER_ERROR = "Something went wrong on our side. Please try again.";

function readCookie(name: string): string | null {
  const cookie = document.cookie.split("; ").find((c) => c.startsWith(`${name}=`));
  return cookie ? decodeURIComponent(cookie.slice(name.length + 1)) : null;
}

async function getCsrfToken(): Promise<string> {
  const existing = readCookie(CSRF_COOKIE);
  if (existing) {
    return existing;
  }
  await fetch("/api/auth/csrf/");
  const token = readCookie(CSRF_COOKIE);
  if (!token) {
    throw new Error("The CSRF cookie was not set.");
  }
  return token;
}

// DRF sends {"field": ["msg", ...]} for field errors and {"detail": "msg"} for general ones.
function toAuthErrors(data: Record<string, unknown>): AuthErrors {
  const errors: AuthErrors = { fields: {} };
  for (const [key, value] of Object.entries(data)) {
    const message = Array.isArray(value) ? value.join(" ") : String(value);
    if (key === "detail" || key === "non_field_errors") {
      errors.form = message;
    } else {
      errors.fields[key] = message;
    }
  }
  return errors;
}

async function postAuth(path: string, body: object): Promise<AuthResult> {
  let response: Response;
  try {
    const csrfToken = await getCsrfToken();
    // Relative URL: the request goes to Next.js, which forwards it to Django (rewrite in next.config.ts).
    response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
      body: JSON.stringify(body),
    });
  } catch {
    return { ok: false, errors: { form: NETWORK_ERROR, fields: {} } };
  }

  if (response.status >= 500) {
    return { ok: false, errors: { form: SERVER_ERROR, fields: {} } };
  }
  const data = await response.json();
  return response.ok ? { ok: true, user: data } : { ok: false, errors: toAuthErrors(data) };
}

export function login(email: string, password: string): Promise<AuthResult> {
  return postAuth("/api/auth/login/", { email, password });
}

export function register(data: RegisterData): Promise<AuthResult> {
  return postAuth("/api/auth/register/", data);
}

export async function logout(): Promise<boolean> {
  try {
    const csrfToken = await getCsrfToken();
    const response = await fetch("/api/auth/logout/", {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
    });
    return response.ok;
  } catch {
    return false;
  }
}
