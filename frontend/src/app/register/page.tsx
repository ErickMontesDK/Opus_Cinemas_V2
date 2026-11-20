import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import AuthTicket from "@/components/auth/AuthTicket";
import RegisterForm from "@/components/auth/RegisterForm";
import { safeNextPath, withNext } from "@/lib/redirect";
import { getCurrentUser } from "@/lib/session";

export const metadata: Metadata = { title: "Sign up" };

export default async function RegisterPage({ searchParams }: PageProps<"/register">) {
  const next = safeNextPath((await searchParams).next);
  if (await getCurrentUser()) {
    redirect(next);
  }

  return (
    <section className="flex w-full items-center justify-center px-4 py-10 sm:py-16">
      <AuthTicket
        label="New member"
        title="Create your account"
        stubColor="bg-secondary"
        footer={
          <>
            Already have an account?{" "}
            <Link href={withNext("/login", next)} className="font-semibold text-brand hover:text-paper">
              Log in
            </Link>
          </>
        }
      >
        <RegisterForm next={next} />
      </AuthTicket>
    </section>
  );
}
