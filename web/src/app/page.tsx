import { DashboardClient } from "@/components/dashboard";

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          Your virtual $100,000 sandbox. Trade, watch, and learn how markets move.
        </p>
      </div>
      <DashboardClient />
    </div>
  );
}
