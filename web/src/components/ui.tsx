import { AlertTriangle, RefreshCw, ShieldCheck } from "lucide-react";
import type { ReactNode } from "react";
import { formatSignedMoney, formatSignedPercent } from "@/lib/format";

/* ------------------------------------------------------------------ */
/* Primitives                                                          */
/* ------------------------------------------------------------------ */

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <section className={`rounded-xl border border-border bg-card p-6 shadow-md ${className}`}>
      {children}
    </section>
  );
}

export function CardTitle({ children, action }: { children: ReactNode; action?: ReactNode }) {
  return (
    <div className="mb-4 flex items-center justify-between">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
        {children}
      </h2>
      {action}
    </div>
  );
}

export function PrimaryButton({
  children,
  onClick,
  disabled = false,
  type = "button",
  className = "",
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  type?: "button" | "submit";
  className?: string;
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`cursor-pointer rounded-lg bg-accent px-5 py-2.5 font-semibold text-on-accent transition-all duration-200 hover:-translate-y-px hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:translate-y-0 ${className}`}
    >
      {children}
    </button>
  );
}

export function GhostButton({
  children,
  onClick,
  className = "",
}: {
  children: ReactNode;
  onClick?: () => void;
  className?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`cursor-pointer rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground transition-colors duration-200 hover:border-accent hover:text-accent ${className}`}
    >
      {children}
    </button>
  );
}

/* ------------------------------------------------------------------ */
/* Badges + indicators                                                 */
/* ------------------------------------------------------------------ */

export function StaleBadge() {
  return (
    <span
      title="This price may be outdated — the market-data provider was unreachable."
      className="inline-flex cursor-help items-center gap-1 rounded-full border border-accent/40 bg-accent/10 px-2.5 py-0.5 text-xs font-medium text-accent"
    >
      <AlertTriangle className="h-3 w-3" aria-hidden />
      Stale price
    </span>
  );
}

export function GroundedBadge({ grounded }: { grounded: boolean }) {
  if (grounded) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full border border-success/40 bg-success/10 px-2.5 py-0.5 text-xs font-medium text-success">
        <ShieldCheck className="h-3 w-3" aria-hidden />
        Grounded in your portfolio data
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-border bg-muted px-2.5 py-0.5 text-xs font-medium text-muted-foreground">
      Ungrounded — treat as general information
    </span>
  );
}

/** Signed money value colored green/red. */
export function SignedMoney({
  value,
  className = "",
}: {
  value: string | null | undefined;
  className?: string;
}) {
  const n = value === null || value === undefined ? NaN : Number(value);
  const color =
    Number.isFinite(n) && n !== 0
      ? n > 0
        ? "text-success"
        : "text-destructive"
      : "text-muted-foreground";
  return (
    <span className={`tnum font-medium ${color} ${className}`}>{formatSignedMoney(value)}</span>
  );
}

/** Signed percent value colored green/red. */
export function SignedPercent({
  value,
  className = "",
}: {
  value: string | null | undefined;
  className?: string;
}) {
  const n = value === null || value === undefined ? NaN : Number(value);
  const color =
    Number.isFinite(n) && n !== 0
      ? n > 0
        ? "text-success"
        : "text-destructive"
      : "text-muted-foreground";
  return (
    <span className={`tnum font-medium ${color} ${className}`}>{formatSignedPercent(value)}</span>
  );
}

/* ------------------------------------------------------------------ */
/* Async states                                                        */
/* ------------------------------------------------------------------ */

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      className="flex items-center justify-center gap-2 py-16 text-muted-foreground"
      role="status"
      aria-live="polite"
    >
      <RefreshCw className="h-5 w-5 animate-spin" aria-hidden />
      <span>{label}</span>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div
      className="flex flex-col items-center gap-3 rounded-xl border border-destructive/40 bg-destructive/5 px-6 py-10 text-center"
      role="alert"
    >
      <AlertTriangle className="h-8 w-8 text-destructive" aria-hidden />
      <p className="max-w-md text-sm text-foreground">{message}</p>
      {onRetry && (
        <GhostButton onClick={onRetry}>
          <span className="inline-flex items-center gap-2">
            <RefreshCw className="h-4 w-4" aria-hidden />
            Try again
          </span>
        </GhostButton>
      )}
    </div>
  );
}

export function Field({
  label,
  children,
  hint,
}: {
  label: string;
  children: ReactNode;
  hint?: string;
}) {
  // Rendered as a div (not <label>) because the wrapped input carries its
  // own accessible name via aria-label.
  return (
    <div className="block">
      <span className="mb-1.5 block text-sm font-medium text-muted-foreground">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-xs text-muted-foreground">{hint}</span>}
    </div>
  );
}

export const inputClassName =
  "w-full rounded-lg border border-border bg-background px-4 py-2.5 text-foreground placeholder:text-muted-foreground/60 transition-colors duration-200 focus:border-accent";
