"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getAdminClientDetail, type AdminClientDetail } from "@/lib/api";
import { Loader2, ArrowLeft, CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const MEAL_ORDER = ["BREAKFAST", "LUNCH", "DINNER", "SNACK"];

export default function AdminClientPage() {
  const { clientId } = useParams<{ clientId: string }>();
  const [detail, setDetail] = useState<AdminClientDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminClientDetail(clientId)
      .then(setDetail)
      .finally(() => setLoading(false));
  }, [clientId]);

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
        </div>
      </AppShell>
    );
  }

  if (!detail) return null;

  const { client, audit, compliance, meal_timeline, report, payment_history } = detail;

  // Group timeline by cycle and day
  const byDay: Record<string, typeof meal_timeline> = {};
  for (const entry of meal_timeline || []) {
    const key = `${entry.challenge_cycle}_${entry.day}`;
    byDay[key] = byDay[key] || [];
    byDay[key].push(entry);
  }

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-3">
          <Link href="/admin">
            <Button variant="ghost" size="sm" className="p-2">
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </Link>
          <div>
            <h1 className="font-heading text-2xl font-bold text-dark">{client.name}</h1>
            <p className="font-body text-sm text-dark/60">{client.email} · {client.phone}</p>
          </div>
          <Badge className={cn(
            "ml-auto",
            client.status === "QUALIFIED" ? "bg-accent/20 text-accent" :
            client.status === "LOCKED" ? "bg-destructive/20 text-destructive" : "bg-muted text-dark/60"
          )}>
            {client.status}
          </Badge>
        </div>

        {/* Profile */}
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">Profile</CardTitle></CardHeader>
          <CardContent className="grid grid-cols-2 gap-2 text-sm font-body">
            {[
              ["Age", client.age],
              ["Gender", client.gender],
              ["Cycle", client.challenge_cycle],
              ["Audit", client.audit_completed ? "✓ Completed" : "Pending"],
            ].map(([l, v]) => (
              <div key={String(l)}>
                <p className="text-dark/50 text-xs">{l}</p>
                <p className="text-dark font-medium">{String(v ?? "—")}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Audit */}
        {audit && (
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-base">Lifestyle Audit</CardTitle></CardHeader>
            <CardContent className="grid grid-cols-2 gap-2 text-sm font-body">
              {[
                ["Sleep", audit.sleep_hours],
                ["Activity", audit.activity_level],
                ["Meals/Day", audit.meals_per_day],
                ["Outside Food", audit.outside_food_frequency],
                ["Stress", audit.stress_level],
              ].map(([l, v]) => (
                <div key={String(l)}>
                  <p className="text-dark/50 text-xs">{l}</p>
                  <p className="text-dark font-medium">{String(v ?? "—")}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Compliance */}
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">Compliance</CardTitle></CardHeader>
          <CardContent className="text-sm font-body space-y-1">
            <p>Completed Days: <strong>{compliance?.completed_days ?? 0} / 7</strong></p>
            <p>Compliance: <strong>{compliance?.compliance_pct ?? 0}%</strong></p>
            <p>Status: <strong>{compliance?.status}</strong></p>
          </CardContent>
        </Card>

        {/* Image Timeline */}
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">Meal Timeline</CardTitle></CardHeader>
          <CardContent>
            {meal_timeline?.length === 0 ? (
              <p className="font-body text-sm text-dark/40">No meals submitted yet.</p>
            ) : (
              <div className="space-y-4">
                {Object.entries(byDay).sort().map(([key, entries]) => {
                  const [cycle, day] = key.split("_");
                  return (
                    <div key={key}>
                      <p className="font-body text-xs text-dark/50 mb-2 uppercase tracking-wide">
                        Cycle {cycle} · Day {day}
                      </p>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {entries
                          .sort((a, b) => MEAL_ORDER.indexOf(a.meal_type) - MEAL_ORDER.indexOf(b.meal_type))
                          .map((entry) => (
                          <div key={entry.meal_type} className="border border-border rounded-xl overflow-hidden">
                            {entry.image_url && (
                              <div className="relative h-28">
                                <Image
                                  src={`${API_URL}${entry.image_url}`}
                                  alt={entry.meal_type}
                                  fill
                                  className="object-cover"
                                />
                              </div>
                            )}
                            <div className="p-3">
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-body text-xs font-semibold text-dark/60 uppercase">{entry.meal_type}</span>
                                {entry.image_url ? (
                                  <CheckCircle2 className="w-3.5 h-3.5 text-accent" />
                                ) : (
                                  <XCircle className="w-3.5 h-3.5 text-destructive/50" />
                                )}
                              </div>
                              <p className="font-body text-xs text-dark/70 leading-relaxed">{entry.meal_text}</p>
                              {entry.food_pattern_tags?.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-2">
                                  {entry.food_pattern_tags.map((tag: string) => (
                                    <span key={tag} className="text-[10px] bg-muted px-1.5 py-0.5 rounded-full text-dark/50">
                                      {tag.replace(/_/g, " ")}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Report */}
        {report && (
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-base">Challenge Report</CardTitle></CardHeader>
            <CardContent className="text-sm font-body space-y-1">
              <p>Status: <strong>{report.qualification_status}</strong></p>
              <p>Compliance: <strong>{report.compliance_score}%</strong></p>
              <p>Days: <strong>{report.completed_days}</strong></p>
              <p>Generated: <strong>{new Date(report.generated_at).toLocaleDateString()}</strong></p>
            </CardContent>
          </Card>
        )}

        {/* Payments */}
        {payment_history?.length > 0 && (
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-base">Payment History</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {payment_history.map((p) => (
                <div key={p.transaction_id} className="flex justify-between items-center py-2 border-b border-border/50 last:border-0 text-sm font-body">
                  <span className="text-dark/70">₹{p.amount_inr} · Cycle {p.cycle_unlocked}</span>
                  <Badge className={p.status === "PAID" ? "bg-accent/20 text-accent" : "bg-muted text-dark/60"}>
                    {p.status}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
