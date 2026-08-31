import * as React from "react";

import { cn } from "@/lib/utils";

export function MarketingContainer({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      className={cn("mx-auto w-full max-w-7xl px-5 sm:px-6 lg:px-8", className)}
      {...props}
    />
  );
}

export function MarketingSection({
  className,
  ...props
}: React.ComponentProps<"section">) {
  return <section className={cn("py-20 md:py-24", className)} {...props} />;
}

export function MarketingEyebrow({
  className,
  ...props
}: React.ComponentProps<"span">) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 font-mono text-xs font-medium tracking-[0.18em] text-primary uppercase",
        className,
      )}
      {...props}
    />
  );
}

export function MarketingSectionHeading({
  title,
  subtitle,
  eyebrow,
  align = "left",
  className,
}: {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  eyebrow?: React.ReactNode;
  align?: "left" | "center";
  className?: string;
}) {
  return (
    <div
      className={cn(
        "mb-12 max-w-3xl md:mb-16",
        align === "center" && "mx-auto text-center",
        className,
      )}
    >
      {eyebrow ? (
        <MarketingEyebrow className="mb-4">{eyebrow}</MarketingEyebrow>
      ) : null}
      <h2 className="text-3xl font-semibold leading-[1.1] tracking-tight text-balance md:text-5xl">
        {title}
      </h2>
      {subtitle ? (
        <p
          className={cn(
            "mt-6 max-w-2xl text-lg leading-relaxed text-muted-foreground",
            align === "center" && "mx-auto",
          )}
        >
          {subtitle}
        </p>
      ) : null}
    </div>
  );
}

export function Reveal({
  children,
  delay = 0,
  className,
  as: Tag = "div",
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
  as?: "div" | "section" | "li" | "span";
}) {
  const ref = React.useRef<HTMLElement | null>(null);
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    document.documentElement.classList.add("reveal-ready");
    const element = ref.current;
    if (!element || typeof IntersectionObserver === "undefined") {
      setVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: "0px 0px -10% 0px" },
    );
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  return (
    <Tag
      ref={ref as React.Ref<never>}
      className={cn("reveal", visible && "reveal-visible", className)}
      style={{ "--reveal-delay": `${delay}ms` } as React.CSSProperties}
    >
      {children}
    </Tag>
  );
}
