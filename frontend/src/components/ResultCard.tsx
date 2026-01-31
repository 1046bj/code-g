"use client";

import { ChevronDown, ExternalLink, Sparkles } from "lucide-react";
import type { AnalysisResult } from "@/types";

function gScoreClass(score: number): string {
  if (score >= 70) return "g-score-high";
  if (score >= 40) return "g-score-mid";
  return "g-score-low";
}

interface ResultCardProps {
  result: AnalysisResult;
  isExpanded: boolean;
  onToggle: () => void;
  onDeepAnalyze?: (result: AnalysisResult) => void;
  deepLoading?: boolean;
}

export function ResultCard({
  result,
  isExpanded,
  onToggle,
  onDeepAnalyze,
  deepLoading = false,
}: ResultCardProps) {
  const { title, agency, date, g_score, summary, url } = result;

  return (
    <article
      className="rounded-xl border border-code-g-border bg-code-g-surface p-4 shadow-glow-sm transition hover:border-code-g-accent/50"
      data-testid="result-card"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h4 className="font-semibold text-code-g-text line-clamp-2">
            {title || "Untitled"}
          </h4>
          <p className="mt-1 text-xs text-code-g-muted">
            {agency} {date && ` · ${date}`}
          </p>
        </div>
        <div
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-lg border border-code-g-border font-mono text-lg font-bold ${gScoreClass(g_score)}`}
          title="G-Score"
        >
          {g_score}
        </div>
      </div>
      {summary && (
        <p className="mt-3 text-sm text-code-g-text-dim line-clamp-2">
          {summary}
        </p>
      )}
      <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-xs text-code-g-accent hover:underline"
        >
          <ExternalLink className="h-3 w-3" />
          Open notice
        </a>
        <div className="flex items-center gap-1">
          {onDeepAnalyze && (
            <button
              type="button"
              onClick={() => onDeepAnalyze(result)}
              disabled={deepLoading}
              className="inline-flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-code-g-accent hover:bg-code-g-border disabled:opacity-60"
              title="Deep Analyze with Company Profile"
            >
              <Sparkles className="h-3 w-3" />
              Deep Analyze
            </button>
          )}
          <button
            type="button"
            onClick={onToggle}
            className="inline-flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-code-g-muted hover:bg-code-g-border hover:text-code-g-text"
            aria-expanded={isExpanded}
          >
            Details
            <ChevronDown
              className={`h-3 w-3 transition-transform ${isExpanded ? "rotate-180" : ""}`}
            />
          </button>
        </div>
      </div>
    </article>
  );
}
