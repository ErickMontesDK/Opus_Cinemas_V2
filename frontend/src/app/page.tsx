import { connection } from "next/server";

import { getApiHealth } from "@/lib/api";

export default async function Home() {
  // Render on every request instead of once at build time,
  // so the status shown is the current one
  await connection();
  const health = await getApiHealth();
  const isOnline = health === "ok";

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6">
      <h1 className="text-5xl font-bold">
        Opus <span className="text-brand">Cinemas</span>
      </h1>
      <p className="flex items-center gap-2 text-sm text-muted">
        <span className={`size-2.5 rounded-full ${isOnline ? "bg-green-500" : "bg-brand"}`} />
        {isOnline ? "API online" : "API offline"}
      </p>
    </main>
  );
}
