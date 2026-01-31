"use client";

import { X, FileCheck, Scale, MessageSquare } from "lucide-react";
import type { AnalysisResult } from "@/types";

interface DetailViewProps {
  result: AnalysisResult;
  isOpen: boolean;
  onClose: () => void;
}

export function DetailView({ result, isOpen, onClose }: DetailViewProps) {
  if (!isOpen) return null;

  const { title, agency, date, summary, eligibility, g_score, reasoning } =
    result;

  return (
    <div
      className="rounded-xl border border-code-g-border bg-code-g-surface p-6 shadow-glow"
      role="dialog"
      aria-label="Analysis detail"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-code-g-text">{title}</h3>
          <p className="text-sm text-code-g-muted">
            {agency} {date && ` · ${date}`}
          </p>
        </div>
        <button
          onClick={onClose}
          className="rounded p-1 text-code-g-muted hover:bg-code-g-border hover:text-code-g-text"
          aria-label="Close"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="mt-6 grid gap-6 sm:grid-cols-2">
        <div className="rounded-lg border border-code-g-border bg-code-g-bg/50 p-4">
          <div className="flex items-center gap-2 text-code-g-accent font-mono text-sm font-medium mb-2">
            <Scale className="h-4 w-4" />
            G-Score
          </div>
          <p className="text-2xl font-bold text-code-g-accent">{g_score}</p>
          <p className="text-xs text-code-g-muted mt-1">0–100 suitability</p>
        </div>

        {summary && (
          <div className="rounded-lg border border-code-g-border bg-code-g-bg/50 p-4">
            <div className="flex items-center gap-2 text-code-g-accent font-mono text-sm font-medium mb-2">
              <FileCheck className="h-4 w-4" />
              Summary
            </div>
            <p className="text-sm text-code-g-text-dim">{summary}</p>
          </div>
        )}
      </div>

      <div className="mt-6 space-y-4">
        <div className="rounded-lg border border-code-g-border bg-code-g-bg/50 p-4">
          <div className="flex items-center gap-2 text-code-g-accent font-mono text-sm font-medium mb-2">
            <FileCheck className="h-4 w-4" />
            Eligibility check
          </div>
          <p className="text-sm text-code-g-text-dim whitespace-pre-wrap">
            {eligibility || "—"}
          </p>
        </div>

        <div className="rounded-lg border border-code-g-border bg-code-g-bg/50 p-4">
          <div className="flex items-center gap-2 text-code-g-accent font-mono text-sm font-medium mb-2">
            <MessageSquare className="h-4 w-4" />
            Reasoning
          </div>
          <p className="text-sm text-code-g-text-dim whitespace-pre-wrap">
            {reasoning || "—"}
          </p>
        </div>
      </div>
    </div>
  );
}
