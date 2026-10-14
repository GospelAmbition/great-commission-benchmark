import { Skeleton } from "@/components/ui/skeleton";

export default function CategoryLoading() {
  return (
    <div className="container py-8">
      <Skeleton className="h-12 w-64 mb-4" />
      <Skeleton className="h-8 w-96 mb-8" />
      <Skeleton className="h-96" />
    </div>
  );
}
