// Error boundaries rely on React state, which only exists in Client Components
"use client";

import { useEffect } from "react";

type ErrorPageProps = {
  error: unknown;
  retry: () => void;
};

export default function ErrorPage({ error, retry }: ErrorPageProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <section className="flex w-full flex-col items-center justify-center gap-4 px-4 py-16 text-center">
      <h1 className="font-brand text-3xl">Something went wrong</h1>
      <p>We could not load this page. Please try again in a moment.</p>
      <button
        type="button"
        onClick={() => retry()}
        className="rounded-md bg-ink px-4 py-2 font-detail text-brand hover:text-paper"
      >
        Try again
      </button>
    </section>
  );
}
