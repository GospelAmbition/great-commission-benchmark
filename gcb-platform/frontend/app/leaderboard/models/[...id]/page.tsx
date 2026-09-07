import Link from "next/link";
import { ArrowRight, Archive } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { RelatedArticles } from "@/components/blog/RelatedArticles";
import { ProviderIcon } from "@/components/ui/provider-icon";
import { formatProvider, getDisplayModelName } from "@/lib/model-utils";
import ModelDetailPage from "../model-detail";
import { getModel, type ModelParams } from "../model-data";

export default async function ModelPage({ params }: ModelParams) {
  const { id } = await params;
  const model = await getModel(id.join("/"));
  if (model.is_active !== false) return <ModelDetailPage model={model} />;

  const name = getDisplayModelName(model.model_name || model.name || "", model.model_id);
  const alternatives = model.related_models || [];
  const groups = [
    { key: "family", title: "Other reviewed models in this family" },
    { key: "provider", title: `Other reviewed models from ${formatProvider(model.provider)}` },
    { key: "other", title: "Explore other reviewed models" },
  ];

  return (
    <div className="container max-w-5xl py-8 space-y-10">
      <section className="space-y-4">
        <Link href="/leaderboard" className="text-sm text-muted-foreground hover:underline">Leaderboard</Link>
        <div className="flex items-center gap-3">
          <ProviderIcon provider={model.provider} />
          <Badge variant="secondary"><Archive className="mr-1 h-3 w-3" />Archived model</Badge>
        </div>
        <h1 className="text-3xl font-bold break-words">{name}</h1>
        <p className="text-sm text-muted-foreground break-all">{model.model_id}</p>
        <p className="text-lg">This model has been removed from public use on OpenRouter.</p>
        <p className="text-muted-foreground max-w-3xl">
          Great Commission Benchmark archives models that are no longer available.
          This model&apos;s benchmark results are no longer included in the public leaderboard.
          Explore other reviewed models on the leaderboard to continue your research.
        </p>
      </section>
      {groups.map(group => {
        const models = alternatives.filter(item => item.relationship === group.key);
        if (!models.length) return null;
        return (
          <section key={group.key} className="space-y-3">
            <h2 className="text-xl font-semibold">{group.title}</h2>
            <ul className="divide-y border-y">
              {models.map(item => (
                <li key={item.model_id}>
                  <Link href={`/leaderboard/models/${encodeURIComponent(item.model_id)}`} className="flex items-center justify-between gap-4 py-4 hover:underline">
                    <span className="min-w-0 break-words">{getDisplayModelName(item.name, item.model_id)}</span>
                    <ArrowRight className="h-4 w-4 shrink-0" aria-hidden="true" />
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        );
      })}
      <Button asChild><Link href="/leaderboard">Explore the leaderboard<ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
      <RelatedArticles articles={model.related_articles || []} />
    </div>
  );
}
