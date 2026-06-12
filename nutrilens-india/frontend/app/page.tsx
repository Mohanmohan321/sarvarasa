import { Navbar } from "@/components/layout/navbar";
import { BottomNav } from "@/components/layout/bottom-nav";
import { Hero } from "@/components/landing/hero";
import { HowItWorks } from "@/components/landing/how-it-works";
import { WhyDifferent } from "@/components/landing/why-different";
import { Features } from "@/components/landing/features";
import { CTASection } from "@/components/landing/cta-section";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="pb-20 md:pb-0">
        <Hero />
        <HowItWorks />
        <WhyDifferent />
        <Features />
        <CTASection />
        <footer className="py-8 text-center font-body text-sm text-dark/40 border-t border-border/50">
          <p>© 2025 Sarvarasa. Food awareness powered by INDB 2024.</p>
        </footer>
      </main>
      <BottomNav />
    </div>
  );
}
