import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare, Mail, Github } from "lucide-react";

export default function ContactPage() {
  return (
    <div className="flex flex-col">
      {/* Page Header */}
      <div className="relative border-b border-white/[0.06] overflow-hidden">
        <div className="absolute inset-0 gradient-hero" />
        <div className="absolute top-1/2 right-0 w-96 h-96 gradient-red-glow opacity-20" />
        
        <div className="container relative py-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <MessageSquare className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">Contact</h1>
          </div>
          <p className="text-muted-foreground">
            Get in touch with the Great Commission Benchmark team
          </p>
        </div>
      </div>

      <div className="container py-6 max-w-4xl">
        <Card>
          <CardHeader>
            <CardTitle>Contact Us</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Have questions or feedback? Reach out to us:
            </p>
            <div className="grid gap-3">
              <a 
                href="mailto:contact@example.com" 
                className="flex items-center gap-3 p-4 rounded-lg bg-white/[0.02] border border-white/[0.06] hover:bg-white/[0.04] hover:border-primary/30 transition-colors"
              >
                <div className="p-2 rounded-lg bg-primary/10">
                  <Mail className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <span className="font-medium text-foreground">Email</span>
                  <p className="text-sm text-muted-foreground">contact@example.com</p>
                </div>
              </a>
              <a
                href="https://discord.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 p-4 rounded-lg bg-white/[0.02] border border-white/[0.06] hover:bg-white/[0.04] hover:border-primary/30 transition-colors"
              >
                <div className="p-2 rounded-lg bg-primary/10">
                  <MessageSquare className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <span className="font-medium text-foreground">Discord</span>
                  <p className="text-sm text-muted-foreground">Join our community server</p>
                </div>
              </a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 p-4 rounded-lg bg-white/[0.02] border border-white/[0.06] hover:bg-white/[0.04] hover:border-primary/30 transition-colors"
              >
                <div className="p-2 rounded-lg bg-primary/10">
                  <Github className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <span className="font-medium text-foreground">GitHub</span>
                  <p className="text-sm text-muted-foreground">View our repository and report issues</p>
                </div>
              </a>
            </div>
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Community Support</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              For technical questions about the GCB Runner, benchmark methodology discussions, or general 
              community support, our Discord server is the best place to connect with the team and other 
              community members.
            </p>
            <p className="text-muted-foreground">
              For private inquiries, partnership opportunities, or media requests, please use email.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
