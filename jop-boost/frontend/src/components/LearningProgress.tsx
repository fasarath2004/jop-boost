import React from "react";
import { GraduationCap, BookOpen, Clock, ChevronRight } from "lucide-react";
import { SuggestedSkill } from "../types";

interface LearningProgressProps {
  skillsLearn: SuggestedSkill[];
}

export default function LearningProgress({ skillsLearn }: LearningProgressProps) {
  return (
    <div 
      className="flex flex-col p-6 rounded-2xl border h-full transition-all duration-300 backdrop-blur-md bg-white border-neutral-200 hover:shadow-md dark:bg-white/[0.03] dark:border-white/[0.08] dark:hover:bg-white/[0.05]"
      id="suggested-skills-card"
    >
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-sm font-semibold font-sora text-neutral-500 dark:text-neutral-400 uppercase tracking-widest flex items-center">
          <GraduationCap className="w-4 h-4 mr-2 text-indigo-500" />
          Suggested Skills to Learn
        </h3>
        <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400">
          LEARNING PATHS
        </span>
      </div>

      <div className="space-y-4">
        {skillsLearn && skillsLearn.length > 0 ? (
          skillsLearn.map((item, idx) => (
            <div
              key={idx}
              className="group p-3.5 rounded-xl border transition-all duration-300 border-neutral-100 bg-neutral-50/50 hover:bg-neutral-100/50 dark:border-white/[0.04] dark:bg-white/[0.01] dark:hover:bg-white/[0.03]"
            >
              {/* Header: Title and Hours */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold font-sora text-neutral-800 dark:text-white group-hover:text-purple-600 dark:group-hover:text-cyan-400 transition-colors flex items-center">
                  <BookOpen className="w-3.5 h-3.5 mr-2 text-neutral-400 dark:text-neutral-500" />
                  {item.name}
                </span>
                <span className="text-[10px] font-mono font-medium text-neutral-400 dark:text-neutral-500 flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {item.hours}h est.
                </span>
              </div>

              {/* Progress Slider (Track & Fill) */}
              <div className="relative w-full h-1.5 bg-neutral-100 dark:bg-neutral-800 rounded-full overflow-hidden mb-2">
                <div
                  className="absolute left-0 top-0 h-full rounded-full transition-all duration-1000 bg-gradient-to-r from-purple-500 to-cyan-400"
                  style={{ width: `${item.progress}%` }}
                />
              </div>

              {/* Progress text metadata and Impact comments */}
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-neutral-500 dark:text-neutral-400">{item.impact}</span>
                <span className="font-mono font-semibold text-neutral-600 dark:text-neutral-300">
                  {item.progress}% Familiar
                </span>
              </div>
            </div>
          ))
        ) : (
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <p className="text-xs text-neutral-400 italic">No recommendations required. Great fit!</p>
          </div>
        )}
      </div>
    </div>
  );
}
