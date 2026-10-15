import { InsightsHeader, PostsSkeleton } from "./insights-content";

export default function InsightsLoading() {
  return (
    <div className="flex flex-col">
      <InsightsHeader />
      <div className="container py-8">
        <PostsSkeleton viewMode="grid" />
      </div>
    </div>
  );
}
