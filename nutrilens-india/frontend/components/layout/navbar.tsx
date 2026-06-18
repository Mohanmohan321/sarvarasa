"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();
  const isLanding = pathname === "/";

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <div className="fixed top-0 left-0 right-0 z-50 h-1.5 bg-espresso" />
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        className={cn(
          "fixed left-0 right-0 z-40 transition-all duration-300",
          "top-1.5",
          scrolled || !isLanding
            ? "glass shadow-soft py-3"
            : "bg-transparent py-5"
        )}
      >
        <div className="max-w-6xl mx-auto px-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 cursor-pointer">
            <Image
              src="/logo-in-light-colour.png"
              alt="Sarvarasa"
              width={120}
              height={36}
              className="h-9 w-auto object-contain"
              priority
            />
          </Link>

          <nav className="hidden md:flex items-center gap-6">
            <Link href="/challenge" className="text-sm font-medium text-dark/70 hover:text-primary transition-colors cursor-pointer">
              My Challenge
            </Link>
            <Link href="/challenge/progress" className="text-sm font-medium text-dark/70 hover:text-primary transition-colors cursor-pointer">
              Progress
            </Link>
          </nav>

          <div className="hidden md:flex items-center gap-2">
            <Link href="/login">
              <Button size="sm" variant="ghost">Log In</Button>
            </Link>
            <Link href="/signup">
              <Button size="sm" className="bg-secondary hover:bg-secondary/90 text-white rounded-full px-5">Sign Up</Button>
            </Link>
          </div>
        </div>
      </motion.header>
    </>
  );
}
