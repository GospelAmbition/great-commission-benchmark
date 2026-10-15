import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";

export default function InsightNotFound() {
  return (
    <div className="w-full py-8 max-w-[800px] mx-auto px-4">
      <Link href="/insights">
        <Button variant="ghost" className="mb-8">
          <ChevronLeft className="h-4 w-4 mr-2" />
          Back to Insights
        </Button>
      </Link>
      <Card className="p-12 text-center">
        <CardContent>
          <h1 className="text-2xl font-bold mb-4">Post Not Found</h1>
          <p className="text-muted-foreground mb-6">
            The article you&apos;re looking for doesn&apos;t exist or has been removed.
          </p>
          <Link href="/insights">
            <Button>Browse All Articles</Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
