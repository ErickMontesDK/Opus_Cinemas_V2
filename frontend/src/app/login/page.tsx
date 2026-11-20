import type { Metadata } from "next";
import Link from "next/link";

import AuthTicket from "@/components/auth/AuthTicket";
import LoginForm from "@/components/auth/LoginForm";

export const metadata: Metadata = { title: "Log in" };

export default function LoginPage() {
  return (
    <section className="flex w-full items-center justify-center px-4 py-10 sm:py-16">
      <AuthTicket
        label="Admit one"
        title="Welcome back"
        stubColor="bg-accent"
        footer={
          <>
            New to Opus Cinemas?{" "}
            <Link href="/register" className="font-semibold text-brand hover:text-paper">
              Sign up
            </Link>
          </>
        }
      >
        <LoginForm />
      </AuthTicket>
    </section>
  );
}
