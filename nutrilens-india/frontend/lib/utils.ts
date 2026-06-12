import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCalories(cal: number): string {
  return Math.round(cal).toLocaleString("en-IN");
}

export function formatNutrient(value: number, unit: string): string {
  return `${value.toFixed(1)}${unit}`;
}

export function getHealthScoreColor(score: number): string {
  if (score >= 75) return "#4CAF50";
  if (score >= 50) return "#E6B17E";
  if (score >= 25) return "#C96A3D";
  return "#DC2626";
}

export function getHealthScoreLabel(score: number): string {
  if (score >= 75) return "Excellent";
  if (score >= 50) return "Good";
  if (score >= 25) return "Fair";
  return "Poor";
}
