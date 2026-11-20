"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import FormField from "@/components/auth/FormField";
import { type AuthErrors, login } from "@/lib/auth";

const NO_ERRORS: AuthErrors = { fields: {} };

export default function LoginForm() {
  const router = useRouter();
  const [values, setValues] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState<AuthErrors>(NO_ERRORS);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function update(field: keyof typeof values) {
    return (value: string) => setValues({ ...values, [field]: value });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setErrors(NO_ERRORS);

    const result = await login(values.email, values.password);
    if (result.ok) {
      router.push("/");
      // Re-render the Server Components so they see the new cookies.
      router.refresh();
      return;
    }
    setErrors(result.errors);
    setIsSubmitting(false);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      {errors.form && (
        <p role="alert" className="rounded-lg border border-accent/60 bg-accent/15 px-3 py-2 text-sm">
          {errors.form}
        </p>
      )}

      <FormField
        label="Email"
        name="email"
        type="email"
        autoComplete="email"
        value={values.email}
        onChange={update("email")}
        error={errors.fields.email}
      />
      <FormField
        label="Password"
        name="password"
        type="password"
        autoComplete="current-password"
        value={values.password}
        onChange={update("password")}
        error={errors.fields.password}
      />

      <button
        type="submit"
        disabled={isSubmitting}
        className="mt-2 rounded-full bg-brand py-3 font-detail text-sm font-semibold tracking-widest text-ink uppercase hover:bg-paper disabled:cursor-wait disabled:opacity-60"
      >
        {isSubmitting ? "Logging in..." : "Log in"}
      </button>
    </form>
  );
}
