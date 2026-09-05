import Link from "next/link";
import { ExternalLink } from "lucide-react";
import type { RecentTestItem } from "@/lib/api";
import { formatProvider, getDisplayModelName } from "@/lib/model-utils";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface RecentTestsListProps {
  items: RecentTestItem[];
  loading?: boolean;
  error?: string | null;
}

function formatCompletedAt(value?: string): string {
  if (!value) return "Unknown";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(value));
}

function scoreClass(score: number): string {
  if (score >= 80) return "text-emerald-400";
  if (score >= 61) return "text-blue-400";
  if (score >= 40) return "text-amber-400";
  return "text-red-400";
}

function ModelDetails({ item }: { item: RecentTestItem }) {
  const modelHref = `/leaderboard/models/${encodeURIComponent(item.model.model_id)}`;
  return (
    <div className="min-w-0">
      <Link
        href={modelHref}
        className="font-semibold text-foreground transition-colors hover:text-primary"
      >
        {getDisplayModelName(item.model.name, item.model.model_id)}
      </Link>
      <div className="mt-1 flex flex-wrap items-center gap-2">
        <Badge variant="outline" className="border-white/10 text-xs text-muted-foreground">
          {formatProvider(item.model.provider)}
        </Badge>
        <span className="text-xs text-muted-foreground">{item.model.model_id}</span>
      </div>
      {item.model.description && (
        <p className="mt-2 line-clamp-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          {item.model.description}
        </p>
      )}
    </div>
  );
}

function Actions({ item }: { item: RecentTestItem }) {
  return (
    <div className="flex flex-wrap items-center gap-3 text-sm">
      <Link
        href={`/leaderboard/models/${encodeURIComponent(item.model.model_id)}`}
        className="font-medium text-primary hover:underline"
      >
        Model
      </Link>
      {item.article && (
        <Link
          href={`/insights/${encodeURIComponent(item.article.slug)}`}
          className="inline-flex items-center gap-1 font-medium text-foreground hover:text-primary"
          aria-label={`Read ${item.article.title}`}
        >
          Article
          <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
        </Link>
      )}
    </div>
  );
}

export function RecentTestsList({ items, loading = false, error = null }: RecentTestsListProps) {
  if (loading) {
    return (
      <div className="space-y-3" aria-label="Loading recent tests">
        {[1, 2, 3, 4, 5].map((row) => (
          <Skeleton key={row} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
        {error}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded-lg border border-white/[0.08] bg-card p-8 text-center text-muted-foreground">
        No completed tests are available yet.
      </div>
    );
  }

  return (
    <>
      <div className="hidden overflow-hidden rounded-lg border border-white/[0.08] bg-card md:block">
        <Table>
          <TableHeader>
            <TableRow className="border-white/[0.08] hover:bg-transparent">
              <TableHead className="w-20">Rank</TableHead>
              <TableHead>Model</TableHead>
              <TableHead className="w-28 text-right">Score</TableHead>
              <TableHead className="w-36">Tested</TableHead>
              <TableHead className="w-40">Links</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.model.id} className="border-white/[0.06] align-top">
                <TableCell className="pt-5 font-semibold tabular-nums text-muted-foreground">
                  #{item.rank}
                </TableCell>
                <TableCell className="py-4">
                  <ModelDetails item={item} />
                </TableCell>
                <TableCell className={`pt-5 text-right text-lg font-bold tabular-nums ${scoreClass(item.score)}`}>
                  {item.score.toFixed(1)}%
                </TableCell>
                <TableCell className="pt-5 text-sm text-muted-foreground">
                  {formatCompletedAt(item.test_run.completed_at)}
                </TableCell>
                <TableCell className="pt-5">
                  <Actions item={item} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="space-y-3 md:hidden">
        {items.map((item) => (
          <article key={item.model.id} className="rounded-lg border border-white/[0.08] bg-card p-4">
            <div className="mb-3 flex items-start justify-between gap-4">
              <span className="font-semibold tabular-nums text-muted-foreground">#{item.rank}</span>
              <span className={`text-lg font-bold tabular-nums ${scoreClass(item.score)}`}>
                {item.score.toFixed(1)}%
              </span>
            </div>
            <ModelDetails item={item} />
            <div className="mt-4 flex items-center justify-between gap-4 border-t border-white/[0.06] pt-3">
              <span className="text-xs text-muted-foreground">
                Tested {formatCompletedAt(item.test_run.completed_at)}
              </span>
              <Actions item={item} />
            </div>
          </article>
        ))}
      </div>
    </>
  );
}
