import React from "react";
import { CheckCircle2, ShieldAlert, Sparkles, AlertCircle } from "lucide-react";
import { SkillGap } from "../types";

interface SkillGapAnalysisProps {
  skills: SkillGap;
}

export default function SkillGapAnalysis({ skills }: SkillGapAnalysisProps) {
  return (
    <div 
      className="flex flex-col p-6 rounded-2xl border h-full transition-all duration-300 backdrop-blur-md bg-white border-neutral-200 hover:shadow-md dark:bg-white/[0.03] dark:border-white/[0.08] dark:hover:bg-white/[0.05]"
      id="skill-gap-card"
    >
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-sm font-semibold font-sora text-neutral-500 dark:text-neutral-400 uppercase tracking-widest flex items-center">
          <Sparkles className="w-4 h-4 mr-2 text-violet-500" />
          Skill Gap Analysis
        </h3>
        <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400">
          ATS GAP KEYWORDS
        </span>
      </div>

      <div className="space-y-6 flex-grow flex flex-col justify-between">
        {/* 1. Strong Match Skills */}
        <div>
          <div className="flex items-center text-emerald-600 dark:text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2.5">
            <CheckCircle2 className="w-4 h-4 mr-2" />
            Strong Match
          </div>
          {skills.possessed && skills.possessed.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {skills.possessed.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 text-xs font-medium font-sans rounded-full border border-emerald-500/20 bg-emerald-500/5 text-emerald-700 dark:text-emerald-400"
                >
                  {skill}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-neutral-400 italic">No direct matches identified yet.</p>
          )}
        </div>

        {/* 2. Missing Skills */}
        <div className="flex-grow pt-4 border-t border-neutral-100 dark:border-neutral-800/60">
          <div className="flex items-center text-rose-500 dark:text-rose-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <ShieldAlert className="w-4 h-4 mr-2 text-rose-500" />
            Missing Skills / Gaps
          </div>
          {skills.missing && skills.missing.length > 0 ? (
            <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
              {skills.missing.map((item, idx) => {
                const isPriorityOne = item.priority === "Priority 1";
                return (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2.5 rounded-lg border transition duration-2 border-neutral-100 bg-neutral-50/50 hover:bg-neutral-100/80 dark:border-white/[0.04] dark:bg-white/[0.01] dark:hover:bg-white/[0.03]"
                  >
                    <span className="text-xs font-medium text-neutral-800 dark:text-neutral-300 flex items-center">
                      <AlertCircle className={`w-3.5 h-3.5 mr-2 ${isPriorityOne ? "text-rose-500" : "text-neutral-400"}`} />
                      {item.skill}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] uppercase tracking-wider font-semibold font-mono ${
                        isPriorityOne
                          ? "bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20"
                          : "bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20"
                      }`}
                    >
                      {item.priority}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-emerald-500 font-sans italic font-medium">Excellent match! No high-priority skill gaps discovered.</p>
          )}
        </div>
      </div>
    </div>
  );
}
