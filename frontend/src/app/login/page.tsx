import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import AuthTicket from "@/components/auth/AuthTicket";
import LoginForm from "@/components/auth/LoginForm";
import { safeNextPath, withNext } from "@/lib/redirect";
import { getCurrentUser } from "@/lib/session";

export const metadata: Metadata = { title: "Log in" };

export default async function LoginPage({ searchParams }: PageProps<"/login">) {
  const next = safeNextPath((await searchParams).next);
  if (await getCurrentUser()) {
    redirect(next);
  }

  return (
    <section className="flex w-full items-center justify-center px-4 py-10 sm:py-16">
      <AuthTicket
        label="Admit one"
        title="Welcome back"
        stubColor="bg-accent"
        footer={
          <>
            New to Opus Cinemas?{" "}
            <Link href={withNext("/register", next)} className="font-semibold text-brand hover:text-paper">
              Sign up
            </Link>
          </>
        }
      >
        <LoginForm next={next} />
      </AuthTicket>
    </section>
  );
}
