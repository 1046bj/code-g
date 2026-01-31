"use client";

import { useState, useEffect, useCallback } from "react";
import { Settings, ChevronLeft, ChevronRight, Plus, X } from "lucide-react";
import type { CompanyProfile } from "@/types";
import { DEFAULT_COMPANY_PROFILE } from "@/types";
import { loadCompanyProfile, saveCompanyProfile } from "@/lib/profile-storage";

const INDUSTRIES = [
  "",
  "AI/Vision",
  "Bio/Health",
  "SaaS",
  "Manufacturing",
  "Hardware",
  "Other",
] as const;

interface ProfileSettingsProps {
  onProfileChange?: (profile: CompanyProfile) => void;
}

export function ProfileSettings({ onProfileChange }: ProfileSettingsProps) {
  const [open, setOpen] = useState(false);
  const [profile, setProfile] = useState<CompanyProfile>(DEFAULT_COMPANY_PROFILE);
  const [keywordInput, setKeywordInput] = useState("");

  useEffect(() => {
    setProfile(loadCompanyProfile());
  }, []);

  const persist = useCallback(
    (next: CompanyProfile) => {
      setProfile(next);
      saveCompanyProfile(next);
      onProfileChange?.(next);
    },
    [onProfileChange]
  );

  const update = useCallback(
    (patch: Partial<CompanyProfile>) => {
      const next = { ...profile, ...patch };
      persist(next);
    },
    [profile, persist]
  );

  const addKeyword = () => {
    const tag = keywordInput.trim();
    if (!tag || profile.keywords.includes(tag)) return;
    update({ keywords: [...profile.keywords, tag] });
    setKeywordInput("");
  };

  const removeKeyword = (tag: string) => {
    update({ keywords: profile.keywords.filter((k) => k !== tag) });
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="fixed left-0 top-1/2 -translate-y-1/2 z-20 flex h-12 w-8 items-center justify-center rounded-r-lg border border-code-g-border border-l-0 bg-code-g-surface text-code-g-muted hover:bg-code-g-border hover:text-code-g-accent shadow-glow-sm"
        aria-label={open ? "Close profile settings" : "Open profile settings"}
      >
        {open ? (
          <ChevronLeft className="h-4 w-4" />
        ) : (
          <ChevronRight className="h-4 w-4" />
        )}
      </button>

      <aside
        className={`fixed left-0 top-0 z-10 h-full w-80 max-w-[90vw] border-r border-code-g-border bg-code-g-surface shadow-glow transition-transform duration-200 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="Profile Settings"
      >
        <div className="flex h-full flex-col p-4">
          <div className="flex items-center justify-between border-b border-code-g-border pb-3">
            <h2 className="font-mono text-sm font-semibold text-code-g-accent flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Profile Settings
            </h2>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="rounded p-1 text-code-g-muted hover:bg-code-g-border hover:text-code-g-text"
              aria-label="Close"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-4 flex flex-col gap-4 overflow-y-auto">
            <div>
              <label className="mb-1 block text-xs font-medium text-code-g-muted">
                Industry
              </label>
              <select
                value={profile.industry}
                onChange={(e) => update({ industry: e.target.value })}
                className="w-full rounded-lg border border-code-g-border bg-code-g-bg px-3 py-2 text-sm text-code-g-text focus:border-code-g-accent focus:outline-none focus:ring-1 focus:ring-code-g-accent"
              >
                {INDUSTRIES.map((opt) => (
                  <option key={opt || "empty"} value={opt}>
                    {opt || "— Select —"}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-code-g-muted">
                Year Established
              </label>
              <input
                type="number"
                min={1900}
                max={2100}
                placeholder="e.g. 2018"
                value={profile.year_established === "" ? "" : profile.year_established}
                onChange={(e) => {
                  const v = e.target.value;
                  update({
                    year_established: v === "" ? "" : Math.min(2100, Math.max(1900, parseInt(v, 10) || 0)),
                  });
                }}
                className="w-full rounded-lg border border-code-g-border bg-code-g-bg px-3 py-2 text-sm text-code-g-text placeholder-code-g-muted focus:border-code-g-accent focus:outline-none focus:ring-1 focus:ring-code-g-accent"
              />
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-code-g-muted">
                Revenue (Last Year, KRW)
              </label>
              <input
                type="number"
                min={0}
                placeholder="e.g. 500000000"
                value={profile.revenue_krw === "" ? "" : profile.revenue_krw}
                onChange={(e) => {
                  const v = e.target.value;
                  update({ revenue_krw: v === "" ? "" : Math.max(0, parseInt(v, 10) || 0) });
                }}
                className="w-full rounded-lg border border-code-g-border bg-code-g-bg px-3 py-2 text-sm text-code-g-text placeholder-code-g-muted focus:border-code-g-accent focus:outline-none focus:ring-1 focus:ring-code-g-accent"
              />
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-code-g-muted">
                Employees
              </label>
              <input
                type="number"
                min={0}
                placeholder="e.g. 15"
                value={profile.employees === "" ? "" : profile.employees}
                onChange={(e) => {
                  const v = e.target.value;
                  update({ employees: v === "" ? "" : Math.max(0, parseInt(v, 10) || 0) });
                }}
                className="w-full rounded-lg border border-code-g-border bg-code-g-bg px-3 py-2 text-sm text-code-g-text placeholder-code-g-muted focus:border-code-g-accent focus:outline-none focus:ring-1 focus:ring-code-g-accent"
              />
            </div>

            <div>
              <span className="mb-1 block text-xs font-medium text-code-g-muted">
                Focus
              </span>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 text-sm text-code-g-text">
                  <input
                    type="radio"
                    name="focus"
                    checked={profile.focus === "r_d"}
                    onChange={() => update({ focus: "r_d" })}
                    className="border-code-g-border text-code-g-accent focus:ring-code-g-accent"
                  />
                  R&D Focus
                </label>
                <label className="flex items-center gap-2 text-sm text-code-g-text">
                  <input
                    type="radio"
                    name="focus"
                    checked={profile.focus === "commercialization"}
                    onChange={() => update({ focus: "commercialization" })}
                    className="border-code-g-border text-code-g-accent focus:ring-code-g-accent"
                  />
                  Commercialization/Sales
                </label>
              </div>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-code-g-muted">
                Keywords (e.g. Vision, Unmanned, Smart Farm)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Add keyword..."
                  value={keywordInput}
                  onChange={(e) => setKeywordInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addKeyword())}
                  className="flex-1 rounded-lg border border-code-g-border bg-code-g-bg px-3 py-2 text-sm text-code-g-text placeholder-code-g-muted focus:border-code-g-accent focus:outline-none focus:ring-1 focus:ring-code-g-accent"
                />
                <button
                  type="button"
                  onClick={addKeyword}
                  className="rounded-lg border border-code-g-border bg-code-g-bg px-3 py-2 text-code-g-accent hover:bg-code-g-border"
                  aria-label="Add keyword"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>
              {profile.keywords.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {profile.keywords.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 rounded-full border border-code-g-border bg-code-g-bg px-2 py-0.5 text-xs text-code-g-text"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => removeKeyword(tag)}
                        className="rounded p-0.5 hover:bg-code-g-border hover:text-code-g-accent"
                        aria-label={`Remove ${tag}`}
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          <p className="mt-4 text-xs text-code-g-muted">
            Saved to this device. Used when running analysis.
          </p>
        </div>
      </aside>
    </>
  );
}
