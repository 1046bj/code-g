import type { CompanyProfile } from "@/types";
import { DEFAULT_COMPANY_PROFILE } from "@/types";

const STORAGE_KEY = "code-g-company-profile";

function safeJsonParse<T>(raw: string, fallback: T): T {
  try {
    const data = JSON.parse(raw) as T;
    return data ?? fallback;
  } catch {
    return fallback;
  }
}

export function loadCompanyProfile(): CompanyProfile {
  if (typeof window === "undefined") return DEFAULT_COMPANY_PROFILE;
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return DEFAULT_COMPANY_PROFILE;
  const parsed = safeJsonParse<Partial<CompanyProfile>>(raw, {});
  return {
    industry: parsed.industry ?? DEFAULT_COMPANY_PROFILE.industry,
    year_established:
      parsed.year_established !== undefined
        ? parsed.year_established
        : DEFAULT_COMPANY_PROFILE.year_established,
    revenue_krw:
      parsed.revenue_krw !== undefined
        ? parsed.revenue_krw
        : DEFAULT_COMPANY_PROFILE.revenue_krw,
    employees:
      parsed.employees !== undefined
        ? parsed.employees
        : DEFAULT_COMPANY_PROFILE.employees,
    focus:
      parsed.focus === "r_d" || parsed.focus === "commercialization"
        ? parsed.focus
        : DEFAULT_COMPANY_PROFILE.focus,
    keywords: Array.isArray(parsed.keywords) ? parsed.keywords : DEFAULT_COMPANY_PROFILE.keywords,
  };
}

export function saveCompanyProfile(profile: CompanyProfile): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
}
