const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Mirrors the "Health" serializer of GET /api/health/ in the Django API
export type HealthStatus = "ok" | "error";

type HealthResponse = {
  status: HealthStatus;
};

/**
 * Ask the API whether it is up and can reach the database.
 * Returns "error" instead of throwing when the API is down or unreachable,
 * so the page can still render.
 */
export async function getApiHealth(): Promise<HealthStatus> {
  try {
    const response = await fetch(`${API_URL}/api/health/`, {
      // Do not let a hanging API block the page for too long
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) {
      return "error";
    }
    const data: HealthResponse = await response.json();
    return data.status;
  } catch {
    return "error";
  }
}
