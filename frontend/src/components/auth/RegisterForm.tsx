"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import FormField from "@/components/auth/FormField";
import { type AuthErrors, type RegisterData, register } from "@/lib/auth";

const NO_ERRORS: AuthErrors = { fields: {} };

export default function RegisterForm({ next }: { next: string }) {
  const router = useRouter();
  const [values, setValues] = useState<RegisterData>({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
  });
  const [errors, setErrors] = useState<AuthErrors>(NO_ERRORS);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function update(field: keyof RegisterData) {
    return (value: string) => setValues({ ...values, [field]: value });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setErrors(NO_ERRORS);

    // Register also logs the user in: the API sets the auth cookies in the same response.
    const result = await register(values);
    if (result.ok) {
      // replace(): the back button should not return to the form. refresh(): Server Components see the new cookies.
      router.replace(next);
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

      <div className="grid gap-5 sm:grid-cols-2">
        <FormField
          label="First name"
          name="first_name"
          autoComplete="given-name"
          value={values.first_name}
          onChange={update("first_name")}
          error={errors.fields.first_name}
        />
        <FormField
          label="Last name"
          name="last_name"
          autoComplete="family-name"
          value={values.last_name}
          onChange={update("last_name")}
          error={errors.fields.last_name}
        />
      </div>
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
        autoComplete="new-password"
        value={values.password}
        onChange={update("password")}
        error={errors.fields.password}
        hint="At least 8 characters, not too common and not only numbers."
      />

      <button
        type="submit"
        disabled={isSubmitting}
        className="mt-2 rounded-full bg-brand py-3 font-detail text-sm font-semibold tracking-widest text-ink uppercase hover:bg-paper disabled:cursor-wait disabled:opacity-60"
      >
        {isSubmitting ? "Creating account..." : "Sign up"}
      </button>
    </form>
  );
}
