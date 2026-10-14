import { Skeleton } from "@/components/ui/skeleton";

export default function ProviderLoading() {
  return (
    <div className="container py-8">
      <Skeleton className="h-8 w-48 mb-4" />
      <Skeleton className="h-12 w-64 mb-2" />
      <Skeleton className="h-6 w-96 mb-8" />
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="h-48" />
        ))}
      </div>
    </div>
  );
}
