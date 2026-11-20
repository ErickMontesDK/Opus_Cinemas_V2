type AuthTicketProps = {
  label: string;
  title: string;
  // Full class name: Tailwind only generates classes it can find written out in the source.
  stubColor: string;
  footer: React.ReactNode;
  children: React.ReactNode;
};

// Circles in the page's background colour, centred on the tear line, look like the notches of a ticket.
const NOTCH = "absolute top-1/2 size-6 -translate-y-1/2 rounded-full bg-brand";

export default function AuthTicket({ label, title, stubColor, footer, children }: AuthTicketProps) {
  return (
    <article className="w-full max-w-md overflow-hidden rounded-2xl bg-ink text-paper shadow-xl">
      <header className={`px-6 py-5 ${stubColor}`}>
        <p className="font-detail text-[0.65rem] font-semibold tracking-widest uppercase opacity-80">
          {label}
        </p>
        <h1 className="font-brand text-3xl leading-tight">{title}</h1>
      </header>

      <div aria-hidden className="relative border-t-2 border-dashed border-paper/30">
        <span className={`${NOTCH} -left-3`} />
        <span className={`${NOTCH} -right-3`} />
      </div>

      <div className="px-6 pt-7 pb-6">{children}</div>

      <footer className="border-t border-paper/10 px-6 py-4 text-center text-sm text-paper/70">
        {footer}
      </footer>
    </article>
  );
}
