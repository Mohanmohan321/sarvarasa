import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,
});

// ─── Registration ─────────────────────────────────────────────────────────────

export interface RegisterRequest {
  name: string;
  email: string;
  phone?: string;
  age?: number;
  gender?: string;
  goal?: string;
  batch_id?: string;
}

export interface RegisterResponse {
  client_id: string;
  name: string;
  status: string;
  batch_id: string | null;
}

export async function registerClient(req: RegisterRequest): Promise<RegisterResponse> {
  const { data } = await api.post("/onboarding/register", req);
  return data;
}

// ─── Audit ───────────────────────────────────────────────────────────────────

export interface AuditPayload {
  client_id: string;
  city?: string;
  occupation?: string;
  cooking_at_home?: boolean;
  sleep_hours?: string;
  sleep_quality?: string;
  wake_time?: string;
  meals_per_day?: string;
  breakfast_habit?: string;
  water_intake?: string;
  outside_food_frequency?: string;
  sugary_beverage_frequency?: string;
  processed_food_frequency?: string;
  activity_level?: string;
  exercise_frequency?: string;
  stress_level?: string;
  stress_eating?: string;
  digestion_issues?: boolean;
  digestion_notes?: string;
  bowel_regularity?: string;
  health_goals?: string;
  dietary_restrictions?: string;
  completed?: boolean;
}

export interface AuditResponse {
  audit_id: string;
  client_id: string;
  completed: boolean;
  message: string;
}

export async function saveAudit(payload: AuditPayload): Promise<AuditResponse> {
  const { data } = await api.post("/audit/save", payload);
  return data;
}

export async function getAudit(clientId: string): Promise<AuditPayload & { completed: boolean }> {
  const { data } = await api.get(`/audit/${clientId}`);
  return data;
}

// ─── Challenge ───────────────────────────────────────────────────────────────

export interface ChallengeProgress {
  client_id: string;
  client_name: string;
  client_status: string;
  challenge_cycle: number;
  audit_completed: boolean;
  required_days: number;
  completed_days: number;
  compliance_pct: number;
  status: string;
  missed_days: number[];
  days_detail: Record<string, string[]>;
  submitted_meals: number;
  required_meals: number;
}

export interface SubmitMealParams {
  client_id: string;
  day_number: number;
  meal_type: string;
  meal_text: string;
  image: File;
}

export interface MealEntry {
  meal_type: string;
  meal_text: string;
  image_url?: string;
  food_pattern_tags: string[];
  submitted_at: string;
}

export interface DayMeals {
  day: number;
  challenge_cycle: number;
  is_complete: boolean;
  meals: MealEntry[];
}

export async function getChallengeProgress(clientId: string): Promise<ChallengeProgress> {
  const { data } = await api.get(`/challenge/progress/${clientId}`);
  return data;
}

export async function submitMeal(params: SubmitMealParams): Promise<{ log_id: string; image_url: string }> {
  const form = new FormData();
  form.append("client_id", params.client_id);
  form.append("day_number", String(params.day_number));
  form.append("meal_type", params.meal_type);
  form.append("meal_text", params.meal_text);
  form.append("image", params.image);
  const { data } = await api.post("/challenge/submit-meal", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getDayMeals(clientId: string, day: number): Promise<DayMeals> {
  const { data } = await api.get(`/challenge/day/${clientId}/${day}`);
  return data;
}

// ─── Reports ─────────────────────────────────────────────────────────────────

export interface ChallengeReport {
  client_name: string;
  compliance_score: number;
  completed_days: number;
  qualification_status: string;
  eligibility_band: string;
  band_label: string;
  food_observations: string[];
  strengths: string[];
  improvement_areas: string[];
  action_plan: string[];
  wholesome_plate_tips: string[];
  food_pattern_summary: Record<string, number>;
  generated_at: string;
}

export async function generateReport(clientId: string): Promise<ChallengeReport> {
  const { data } = await api.post(`/reports/generate/${clientId}`);
  return data;
}

export async function getReport(clientId: string): Promise<ChallengeReport> {
  const { data } = await api.get(`/reports/${clientId}`);
  return data;
}

// ─── Payment ─────────────────────────────────────────────────────────────────

export interface CreateOrderResponse {
  order_id: string;
  amount: number;
  currency: string;
  transaction_id: string;
  key_id: string;
}

export interface VerifyPaymentRequest {
  client_id: string;
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}

export async function createPaymentOrder(clientId: string): Promise<CreateOrderResponse> {
  const { data } = await api.post("/payment/create-order", { client_id: clientId });
  return data;
}

export async function verifyPayment(req: VerifyPaymentRequest): Promise<{ success: boolean }> {
  const { data } = await api.post("/payment/verify", req);
  return data;
}

// ─── Admin ───────────────────────────────────────────────────────────────────

export interface AdminDashboard {
  total: number;
  audit_completed: number;
  active: number;
  qualified: number;
  second_chance: number;
  locked: number;
  reactivated: number;
  revenue_inr: number;
}

export interface AdminClient {
  client_id: string;
  name: string;
  email: string;
  phone: string;
  status: string;
  audit_completed: boolean;
  challenge_cycle: number;
  compliance_pct: number;
  completed_days: number;
  submitted_meals?: number;
  compliance_status: string;
  qualification_status: string | null;
  joined_at: string;
}

export interface AdminClientDetail {
  client: {
    id: string;
    name: string;
    age: number;
    gender: string;
    weight_kg: number;
    goal: string;
    phone: string;
    email: string;
    status: string;
    audit_completed: boolean;
    challenge_cycle: number;
    joined_at: string;
  };
  audit: {
    completed: boolean;
    sleep_hours: string;
    activity_level: string;
    meals_per_day: string;
    outside_food_frequency: string;
    stress_level: string;
  } | null;
  compliance: {
    completed_days: number;
    compliance_pct: number;
    status: string;
  };
  meal_timeline: {
    day: number;
    meal_type: string;
    meal_text: string;
    image_url?: string;
    food_pattern_tags: string[];
    challenge_cycle: number;
    submitted_at: string;
  }[];
  report: {
    compliance_score: number;
    completed_days: number;
    qualification_status: string;
    eligibility_band: string;
    band_label: string;
    food_pattern_summary: Record<string, number>;
    generated_at: string;
  } | null;
  payment_history: {
    transaction_id: string;
    amount_inr: number;
    status: string;
    cycle_unlocked: number;
    paid_at: string;
  }[];
}

export async function getAdminDashboard(): Promise<AdminDashboard> {
  const { data } = await api.get("/admin/dashboard");
  return data;
}

export async function getAdminClients(): Promise<{ total: number; clients: AdminClient[] }> {
  const { data } = await api.get("/admin/clients");
  return data;
}

export async function getAdminClientDetail(clientId: string): Promise<AdminClientDetail> {
  const { data } = await api.get(`/admin/clients/${clientId}`);
  return data;
}

// ─── Legacy (kept for compatibility with existing food search) ────────────────

export async function foodAutocomplete(q: string): Promise<string[]> {
  const { data } = await api.get("/foods/autocomplete", { params: { q } });
  return data.suggestions as string[];
}

// ─── Legacy types kept for analysis routes (not used in Sarvarasa main flow) ──

export interface AnalyzeImageResponse {
  foods: { name: string; confidence: number; display_name: string }[];
  image_url: string;
  session_id: string;
}

export interface NutritionResult {
  meal_id: string;
  foods: string[];
  total_calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  image_url: string;
  created_at: string;
}
