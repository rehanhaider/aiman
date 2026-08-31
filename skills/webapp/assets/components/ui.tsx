import { Loader2 } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
        {subtitle ? (
          <p className="mt-0.5 text-sm text-muted-foreground">{subtitle}</p>
        ) : null}
      </div>
      {actions ? (
        <div className="flex items-center gap-2">{actions}</div>
      ) : null}
    </div>
  );
}

export function EmptyState({
  title,
  hint,
  action,
  icon,
}: {
  title: string;
  hint?: string;
  action?: ReactNode;
  icon?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed py-14 text-center">
      {icon ?? <EmptyGlyph />}
      <p className="text-sm font-medium text-foreground/70">{title}</p>
      {hint ? (
        <p className="max-w-sm text-xs text-muted-foreground">{hint}</p>
      ) : null}
      {action ? <div className="mt-2">{action}</div> : null}
    </div>
  );
}

function EmptyGlyph() {
  return (
    <svg
      width="56"
      height="44"
      viewBox="0 0 56 44"
      fill="none"
      aria-hidden
      className="text-foreground/25"
    >
      <rect
        x="4"
        y="8"
        width="48"
        height="32"
        rx="6"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeDasharray="4 3"
      />
      <circle cx="20" cy="22" r="5" stroke="currentColor" strokeWidth="1.5" />
      <path
        d="M30 18h14M30 24h10"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <circle
        cx="46"
        cy="8"
        r="3.5"
        fill="var(--color-primary)"
        opacity="0.8"
      />
    </svg>
  );
}

export function Spinner({
  label,
  className,
}: {
  label?: string;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex items-center justify-center gap-2 py-12 text-muted-foreground",
        className,
      )}
    >
      <Loader2 className="size-4 animate-spin" />
      {label ? <span className="text-sm">{label}</span> : null}
    </div>
  );
}

export function ButtonSpinner() {
  return <Loader2 className="size-3.5 animate-spin" />;
}

export function SectionCard({
  title,
  subtitle,
  actions,
  children,
  className,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={cn("rounded-xl border bg-card", className)}>
      <header className="flex items-center justify-between gap-3 border-b px-4 py-2.5">
        <div className="min-w-0">
          <h2 className="text-xs font-semibold tracking-wider text-muted-foreground uppercase">
            {title}
          </h2>
          {subtitle ? (
            <p className="mt-0.5 text-xs text-muted-foreground/70">
              {subtitle}
            </p>
          ) : null}
        </div>
        {actions}
      </header>
      <div className="p-4">{children}</div>
    </section>
  );
}

export function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <div className="grid grid-cols-[120px_1fr] items-baseline gap-2 py-1 text-sm">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="min-w-0 break-words">
        {children}
        {hint ? (
          <span className="mt-0.5 block text-[11px] text-muted-foreground/70">
            {hint}
          </span>
        ) : null}
      </span>
    </div>
  );
}
