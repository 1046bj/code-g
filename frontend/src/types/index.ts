export interface CompanyProfile {
  industry: string;
  year_established: number | "";
  revenue_krw: number | "";
  employees: number | "";
  focus: "r_d" | "commercialization" | "";
  keywords: string[];
}

export const DEFAULT_COMPANY_PROFILE: CompanyProfile = {
  industry: "",
  year_established: "",
  revenue_krw: "",
  employees: "",
  focus: "",
  keywords: [],
};

export interface AnalysisResult {
  url: string;
  title: string;
  date: string;
  agency: string;
  passed_filter: boolean;
  summary: string;
  eligibility: string;
  g_score: number;
  reasoning: string;
}
