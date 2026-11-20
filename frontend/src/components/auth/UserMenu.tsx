import LoginLink from "@/components/auth/LoginLink";
import LogoutButton from "@/components/auth/LogoutButton";
import { getCurrentUser } from "@/lib/session";

export default async function UserMenu() {
  // If the API is down, show "Log in" instead of breaking the header on every page.
  const user = await getCurrentUser().catch(() => null);

  if (!user) {
    return (
      <LoginLink className="rounded-full border-2 border-brand px-4 py-1.5 font-detail text-xs font-semibold tracking-widest uppercase hover:bg-brand hover:text-ink" />
    );
  }

  const name = user.first_name || user.email;

  return (
    <div className="flex items-center gap-3 md:border-l md:border-brand/30 md:pl-4">
      <span
        aria-hidden="true"
        className="flex size-10 shrink-0 items-center justify-center rounded-full bg-brand font-detail text-lg font-bold text-ink"
      >
        {name.charAt(0).toUpperCase()}
      </span>
      <div className="flex min-w-0 flex-col items-start leading-tight">
        <span className="max-w-48 truncate font-detail text-base font-semibold text-paper">{name}</span>
        <LogoutButton />
      </div>
    </div>
  );
}
