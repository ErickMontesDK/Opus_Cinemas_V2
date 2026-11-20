import type { Metadata } from "next";
import Link from "next/link";

import AuthTicket from "@/components/auth/AuthTicket";
import RegisterForm from "@/components/auth/RegisterForm";

export const metadata: Metadata = { title: "Sign up" };

export default function RegisterPage() {
  return (
    <section className="flex w-full items-center justify-center px-4 py-10 sm:py-16">
      <AuthTicket
        label="New member"
        title="Create your account"
        stubColor="bg-secondary"
        footer={
          <>
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-brand hover:text-paper">
              Log in
            </Link>
          </>
        }
      >
        <RegisterForm />
      </AuthTicket>
    </section>
  );
}
