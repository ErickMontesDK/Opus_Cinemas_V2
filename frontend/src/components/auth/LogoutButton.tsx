"use client";

import { useState } from "react";

import { logout } from "@/lib/auth";

export default function LogoutButton() {
  const [isPending, setIsPending] = useState(false);

  async function handleClick() {
    setIsPending(true);
    if (await logout()) {
      // Full reload, so leaving the session is visible and no client state of the user survives.
      window.location.reload();
      return;
    }
    setIsPending(false);
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={isPending}
      className="text-xs text-paper/60 underline-offset-2 hover:text-brand hover:underline disabled:cursor-wait"
    >
      {isPending ? "Logging out..." : "Log out"}
    </button>
  );
}
