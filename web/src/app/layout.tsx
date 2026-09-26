import { Coins } from "lucide-react";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Finkow — Learn finance by playing the market",
  description:
    "Finkow is an open-source AI-native financial learning sandbox. Start with $100,000 of virtual money, trade real market data, and build financial intuition.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="flex min-h-full flex-col">
        <header className="border-b border-border bg-background/95">
          <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
            <a
              href="/"
              className="inline-flex cursor-pointer items-center gap-2.5 transition-opacity duration-200 hover:opacity-80"
              aria-label="Finkow home"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent">
                <Coins className="h-5 w-5 text-on-accent" aria-hidden />
              </span>
              <span className="text-xl font-bold tracking-tight">Finkow</span>
            </a>
            <nav className="flex items-center gap-4 text-sm">
              <a
                href="/"
                className="cursor-pointer font-medium text-muted-foreground transition-colors duration-200 hover:text-accent"
              >
                Dashboard
              </a>
              <span className="rounded-full border border-accent/40 bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent">
                Virtual $100k sandbox
              </span>
            </nav>
          </div>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">{children}</main>

        <footer className="border-t border-border">
          <div className="mx-auto flex max-w-6xl flex-col gap-1 px-4 py-6 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-6">
            <p>Finkow — open-source financial learning sandbox.</p>
            <p>All money is virtual. Market data is delayed.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
