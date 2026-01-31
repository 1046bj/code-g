import type { AnalysisResult, CompanyProfile } from "@/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

function profileToBody(profile: CompanyProfile | null) {
  if (!profile) return null;
  const industry = profile.industry || undefined;
  const year_established =
    profile.year_established === "" ? undefined : (profile.year_established as number);
  const revenue_krw =
    profile.revenue_krw === "" ? undefined : (profile.revenue_krw as number);
  const employees =
    profile.employees === "" ? undefined : (profile.employees as number);
  const focus =
    profile.focus === ""
      ? undefined
      : profile.focus === "r_d"
        ? "R&D Focus"
        : "Commercialization/Sales Focus";
  const keywords = profile.keywords?.length ? profile.keywords : undefined;
  if (
    industry === undefined &&
    year_established === undefined &&
    revenue_krw === undefined &&
    employees === undefined &&
    focus === undefined &&
    !keywords?.length
  ) {
    return null;
  }
  return {
    industry,
    year_established,
    revenue_krw,
    employees,
    focus,
    keywords: keywords ?? [],
  };
}

export async function runCodeGAnalysis(
  url: string,
  profile: CompanyProfile | null
): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/api/code-g/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url,
      profile: profileToBody(profile),
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail?: string }).detail || "Request failed");
  }
  return res.json();
}

export async function runDeepAnalysis(
  url: string,
  profile: CompanyProfile | null
): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/api/code-g/deep-analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url,
      profile: profileToBody(profile),
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail?: string }).detail || "Request failed");
  }
  return res.json();
}
