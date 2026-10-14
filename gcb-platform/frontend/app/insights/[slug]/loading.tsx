import { Skeleton } from "@/components/ui/skeleton";

export default function InsightLoading() {
  return (
    <div className="w-full py-8 max-w-[800px] mx-auto px-4">
      <Skeleton className="h-8 w-32 mb-8" />
      <Skeleton className="h-12 w-3/4 mb-4" />
      <Skeleton className="h-6 w-1/2 mb-8" />
      <Skeleton className="h-64 w-full mb-8" />
      <div className="space-y-4">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    </div>
  );
}
