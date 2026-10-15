import { Skeleton } from "@/components/ui/skeleton";

export default function AboutLoading() {
  return (
    <div className="container py-8">
      <Skeleton className="h-10 w-48 mb-3" />
      <Skeleton className="h-5 w-96 mb-8" />
      <Skeleton className="h-10 w-full max-w-xl mb-6" />
      <Skeleton className="h-96" />
    </div>
  );
}
