import Image, { type StaticImageData } from "next/image";

import combo from "@/assets/promos/combo.png";
import popcornCart from "@/assets/promos/popcorn-cart.png";
import socialPost from "@/assets/promos/social-post.png";

type Promo = {
  label: string;
  title: string;
  text: string;
  note: string;
  image: StaticImageData;
  // Full class names: Tailwind only generates classes it can find written out in the source.
  stubColor: string;
};

// Static content: the cinema is fictional, so there is no promotions model in the database.
const PROMOS: Promo[] = [
  {
    label: "Combo deal",
    title: "Movie Night Combo",
    text: "A medium popcorn and drink for the price of a small one, Monday to Thursday.",
    note: "One per visit. Not valid on holidays.",
    image: combo,
    stubColor: "bg-accent",
  },
  {
    label: "Social media",
    title: "#OpusMovieNight",
    text: "Post your cinema selfie with this hashtag and get a free chocolate bar on your next visit.",
    note: "Tag @OpusCinemas to qualify.",
    image: socialPost,
    stubColor: "bg-muted",
  },
  {
    label: "Limited time",
    title: "Free Refill Fridays",
    text: "Buy any large popcorn on a Friday and enjoy unlimited refills during your movie.",
    note: "Excludes premium flavors.",
    image: popcornCart,
    stubColor: "bg-secondary",
  },
];

// Half circles in the section's background colour, centred on the tear line, look like the notches of a ticket.
const NOTCH = "absolute left-1/2 size-6 -translate-x-1/2 rounded-full bg-ink";

export default function PromoCards() {
  return (
    // A swipeable row on small screens; three columns on large ones.
    <ul className="scrollbar-brand -mx-4 flex snap-x snap-mandatory gap-4 overflow-x-auto px-4 pb-3 lg:mx-0 lg:grid lg:grid-cols-3 lg:gap-6 lg:overflow-visible lg:px-0">
      {PROMOS.map((promo) => (
        <li key={promo.title} className="w-[85%] shrink-0 snap-start sm:w-[60%] lg:w-auto">
          <article className="group flex h-full overflow-hidden rounded-2xl bg-brand text-ink shadow-xl">
            <div className={`flex w-28 shrink-0 items-center justify-center p-3 sm:w-32 ${promo.stubColor}`}>
              <Image
                src={promo.image}
                alt=""
                sizes="8rem"
                className="h-auto w-full object-contain drop-shadow-xl transition-transform duration-500 group-hover:scale-110 group-hover:-rotate-6 motion-reduce:transition-none"
              />
            </div>

            <div aria-hidden className="relative w-0 border-l-2 border-dashed border-ink/30">
              <span className={`${NOTCH} -top-3`} />
              <span className={`${NOTCH} -bottom-3`} />
            </div>

            <div className="flex flex-1 flex-col gap-1 p-4 pl-5">
              <p className="font-detail text-[0.65rem] font-semibold tracking-widest text-ink/60 uppercase">
                {promo.label}
              </p>
              <h3 className="font-brand text-xl leading-tight">{promo.title}</h3>
              <p className="text-sm leading-snug text-ink/80">{promo.text}</p>
              <p className="mt-auto pt-2 text-[0.7rem] text-ink/50">{promo.note}</p>
            </div>
          </article>
        </li>
      ))}
    </ul>
  );
}
