import { HomeHero } from "@/components/home/HomeHero";
import { Skeleton } from "@/components/ui/skeleton";

export default function HomeLoading() {
  return (
    <div className="flex flex-col">
      <HomeHero />
      <section className="container py-12">
        <Skeleton className="h-8 w-72 mb-2" />
        <Skeleton className="h-4 w-56 mb-6" />
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-14 w-full" />
          ))}
        </div>
      </section>
    </div>
  );
}
