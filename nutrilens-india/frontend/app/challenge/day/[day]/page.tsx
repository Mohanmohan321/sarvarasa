"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/lib/use-toast";
import { getDayMeals, submitMeal, type DayMeals } from "@/lib/api";
import {
  Loader2, Camera, CheckCircle2, Upload, ArrowLeft, ArrowRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";

const CLIENT_ID_KEY = "sarvarasa_client_id";

const MEAL_ORDER = ["BREAKFAST", "LUNCH", "DINNER", "SNACK"];
const MEAL_INFO: Record<string, { label: string; emoji: string; hint: string }> = {
  BREAKFAST: { label: "Breakfast", emoji: "🌅", hint: "Idli, dosa, upma, poha, paratha..." },
  LUNCH: { label: "Lunch", emoji: "☀️", hint: "Rice, sambar, dal, roti, sabzi..." },
  DINNER: { label: "Dinner", emoji: "🌙", hint: "Dinner meal, soup, khichdi..." },
  SNACK: { label: "Snack (Optional)", emoji: "🍎", hint: "Fruits, nuts, tea, biscuits..." },
};
const REQUIRED_MEALS = ["BREAKFAST", "LUNCH", "DINNER"];

interface MealFormState {
  text: string;
  imageFile: File | null;
  imagePreview: string | null;
  submitting: boolean;
  submitted: boolean;
  existingImageUrl?: string;
}

function MealForm({
  mealType,
  dayNumber,
  clientId,
  existing,
  onSubmitted,
}: {
  mealType: string;
  dayNumber: number;
  clientId: string;
  existing?: { meal_text: string; image_url?: string };
  onSubmitted: (type: string) => void;
}) {
  const { toast } = useToast();
  const fileRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<MealFormState>({
    text: existing?.meal_text || "",
    imageFile: null,
    imagePreview: null,
    submitting: false,
    submitted: !!existing,
    existingImageUrl: existing?.image_url,
  });

  const info = MEAL_INFO[mealType];
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleFile = (file: File) => {
    const preview = URL.createObjectURL(file);
    setState((s) => ({ ...s, imageFile: file, imagePreview: preview }));
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) handleFile(file);
  };

  const handleSubmit = async () => {
    if (!state.text.trim()) {
      toast({ title: "Description required", description: "Please describe what you ate.", variant: "destructive" });
      return;
    }
    if (!state.imageFile && !state.existingImageUrl) {
      toast({ title: "Image required", description: "Please upload a photo of your meal.", variant: "destructive" });
      return;
    }

    setState((s) => ({ ...s, submitting: true }));
    try {
      await submitMeal({
        client_id: clientId,
        day_number: dayNumber,
        meal_type: mealType,
        meal_text: state.text,
        image: state.imageFile!,
      });
      setState((s) => ({ ...s, submitting: false, submitted: true }));
      onSubmitted(mealType);
      toast({ title: `${info.label} logged!`, description: "Your meal has been saved." });
    } catch {
      setState((s) => ({ ...s, submitting: false }));
      toast({ title: "Error", description: "Could not save meal. Please try again.", variant: "destructive" });
    }
  };

  if (state.submitted) {
    return (
      <div className="flex items-center gap-3 p-4 bg-accent/5 border border-accent/20 rounded-2xl">
        <CheckCircle2 className="w-6 h-6 text-accent shrink-0" />
        <div>
          <p className="font-body text-sm font-medium text-dark">{info.label} logged</p>
          <p className="font-body text-xs text-dark/50 truncate max-w-[220px]">{state.text}</p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setState((s) => ({ ...s, submitted: false }))}
          className="ml-auto text-dark/40 hover:text-dark text-xs"
        >
          Edit
        </Button>
      </div>
    );
  }

  const imageDisplayUrl = state.imagePreview ||
    (state.existingImageUrl ? `${API_URL}${state.existingImageUrl}` : null);

  return (
    <Card>
      <CardContent className="p-5 space-y-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">{info.emoji}</span>
          <h3 className="font-heading text-base font-semibold text-dark">{info.label}</h3>
        </div>

        {/* Image Upload */}
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => fileRef.current?.click()}
          className="relative cursor-pointer rounded-xl border-2 border-dashed border-border hover:border-primary/40 transition-colors overflow-hidden"
        >
          {imageDisplayUrl ? (
            <div className="relative h-32">
              <Image src={imageDisplayUrl} alt="Meal" fill className="object-cover" />
              <div className="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                <Camera className="w-6 h-6 text-white" />
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-28 gap-2 text-dark/40">
              <Upload className="w-6 h-6" />
              <p className="font-body text-sm">Tap to upload a photo</p>
              <p className="font-body text-xs">Required — drag & drop or click</p>
            </div>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
        </div>

        {/* Text Description */}
        <div>
          <textarea
            rows={3}
            value={state.text}
            onChange={(e) => setState((s) => ({ ...s, text: e.target.value }))}
            placeholder={`Describe your ${info.label.toLowerCase()}: ${info.hint}`}
            className="w-full px-4 py-3 rounded-xl border border-border bg-card font-body text-sm text-dark placeholder:text-dark/40 resize-none focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
          <p className="font-body text-xs text-dark/40 mt-1">Be descriptive — e.g. "2 idli with sambar and coconut chutney"</p>
        </div>

        <Button
          onClick={handleSubmit}
          disabled={state.submitting}
          className="w-full"
        >
          {state.submitting ? (
            <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Saving…</>
          ) : (
            <>Save {info.label}</>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}

export default function DayPage() {
  const params = useParams();
  const router = useRouter();
  const dayNumber = parseInt(params.day as string);
  const [dayMeals, setDayMeals] = useState<DayMeals | null>(null);
  const [loading, setLoading] = useState(true);
  const [submittedTypes, setSubmittedTypes] = useState<Set<string>>(new Set());

  const clientId = typeof window !== "undefined" ? localStorage.getItem(CLIENT_ID_KEY) || "" : "";

  useEffect(() => {
    if (!clientId) { router.push("/onboarding"); return; }
    if (isNaN(dayNumber) || dayNumber < 1 || dayNumber > 7) { router.push("/challenge"); return; }
    getDayMeals(clientId, dayNumber)
      .then((data) => {
        setDayMeals(data);
        const done = new Set(data.meals.map((m) => m.meal_type));
        setSubmittedTypes(done);
      })
      .finally(() => setLoading(false));
  }, [clientId, dayNumber, router]);

  const handleSubmitted = (type: string) => {
    setSubmittedTypes((prev) => new Set([...prev, type]));
  };

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
        </div>
      </AppShell>
    );
  }

  const requiredDone = REQUIRED_MEALS.every((t) => submittedTypes.has(t));
  const existingByType = Object.fromEntries(
    (dayMeals?.meals || []).map((m) => [m.meal_type, m])
  );

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-5">
        {/* Header */}
        <div className="flex items-center gap-3">
          <Link href="/challenge">
            <Button variant="ghost" size="sm" className="p-2">
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </Link>
          <div>
            <h1 className="font-heading text-2xl font-bold text-dark">Day {dayNumber}</h1>
            <p className="font-body text-sm text-dark/60">Log your meals for today</p>
          </div>
        </div>

        {/* Completion Badge */}
        {requiredDone && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-3 p-4 bg-accent/10 border border-accent/30 rounded-2xl"
          >
            <CheckCircle2 className="w-6 h-6 text-accent" />
            <div>
              <p className="font-heading text-sm font-semibold text-dark">Day {dayNumber} Complete!</p>
              <p className="font-body text-xs text-dark/60">All 3 required meals submitted.</p>
            </div>
          </motion.div>
        )}

        {/* Required Meals */}
        <div>
          <p className="font-body text-xs text-dark/50 uppercase tracking-wide font-semibold mb-3">Required</p>
          <div className="space-y-3">
            {REQUIRED_MEALS.map((mealType) => (
              <AnimatePresence key={mealType}>
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: REQUIRED_MEALS.indexOf(mealType) * 0.1 }}
                >
                  <MealForm
                    mealType={mealType}
                    dayNumber={dayNumber}
                    clientId={clientId}
                    existing={existingByType[mealType]}
                    onSubmitted={handleSubmitted}
                  />
                </motion.div>
              </AnimatePresence>
            ))}
          </div>
        </div>

        {/* Optional Snack */}
        <div>
          <p className="font-body text-xs text-dark/50 uppercase tracking-wide font-semibold mb-3">Optional</p>
          <MealForm
            mealType="SNACK"
            dayNumber={dayNumber}
            clientId={clientId}
            existing={existingByType["SNACK"]}
            onSubmitted={handleSubmitted}
          />
        </div>

        {/* Navigation */}
        <div className="flex gap-3 pt-2">
          {dayNumber > 1 && (
            <Link href={`/challenge/day/${dayNumber - 1}`} className="flex-1">
              <Button variant="outline" className="w-full">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Day {dayNumber - 1}
              </Button>
            </Link>
          )}
          {dayNumber < 7 && (
            <Link href={`/challenge/day/${dayNumber + 1}`} className="flex-1">
              <Button variant="outline" className="w-full">
                Day {dayNumber + 1}
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          )}
          <Link href="/challenge" className={cn("flex-1", dayNumber === 1 || dayNumber === 7 ? "" : "flex-none w-auto")}>
            <Button className="w-full">
              View Progress
            </Button>
          </Link>
        </div>
      </div>
    </AppShell>
  );
}
