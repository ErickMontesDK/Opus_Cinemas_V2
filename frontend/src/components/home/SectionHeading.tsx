type SectionHeadingProps = {
  id: string;
  children: React.ReactNode;
};

export default function SectionHeading({ id, children }: SectionHeadingProps) {
  return (
    <h2
      id={id}
      className="relative mb-8 pl-5 font-brand text-3xl md:text-4xl before:absolute before:inset-y-0 before:left-0 before:w-1.5 before:rounded-full before:bg-brand before:shadow-[0_0_15px_var(--color-brand)]"
    >
      {children}
    </h2>
  );
}
