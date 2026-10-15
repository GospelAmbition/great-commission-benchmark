import { Skeleton } from "@/components/ui/skeleton";
import { CategoriesHeader } from "./categories-header";

export default function CategoriesLoading() {
  return (
    <div className="flex flex-col">
      <CategoriesHeader />
      <div className="container py-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      </div>
    </div>
  );
}
