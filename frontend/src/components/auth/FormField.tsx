type FormFieldProps = {
  label: string;
  name: string;
  type?: "text" | "email" | "password";
  autoComplete: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  hint?: string;
};

export default function FormField({
  label,
  name,
  type = "text",
  autoComplete,
  value,
  onChange,
  error,
  hint,
}: FormFieldProps) {
  const errorId = `${name}-error`;

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={name} className="font-detail text-xs tracking-wider uppercase">
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        autoComplete={autoComplete}
        required
        value={value}
        onChange={(event) => onChange(event.target.value)}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? errorId : undefined}
        className="rounded-lg border border-paper/20 bg-ink-soft px-3 py-2.5 text-base text-paper focus:border-brand focus:ring-2 focus:ring-brand/40 focus:outline-none aria-invalid:border-accent"
      />
      {error ? (
        <p id={errorId} className="text-sm text-accent">
          {error}
        </p>
      ) : (
        hint && <p className="text-xs text-paper/60">{hint}</p>
      )}
    </div>
  );
}
