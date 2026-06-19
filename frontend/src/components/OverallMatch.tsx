import React from "react";
import { CheckCircle, AlertTriangle, XCircle, Award } from "lucide-react";

interface OverallMatchProps {
  percentage: number;
  fitLevel: 'Strong Fit' | 'Moderate Fit' | 'Development Needed';
}

export default function OverallMatch({ percentage, fitLevel }: OverallMatchProps) {
  // SVG configuration
  const radius = 60;
  const strokeWidth = 12;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  // Badge configuration based on fitLevel
  const getBadgeStyle = () => {
    switch (fitLevel) {
      case "Strong Fit":
        return {
          bg: "bg-emerald-500/10 text-emerald-500 dark:text-emerald-400 border-emerald-500/30",
          ring: "stroke-emerald-500 dark:stroke-emerald-400",
          icon: <CheckCircle className="w-4 h-4 mr-1.5" />,
          colorText: "text-emerald-500"
        };
      case "Moderate Fit":
        return {
          bg: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30",
          ring: "stroke-amber-500 dark:stroke-amber-400",
          icon: <AlertTriangle className="w-4 h-4 mr-1.5" />,
          colorText: "text-amber-500"
        };
      case "Development Needed":
        return {
          bg: "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30",
          ring: "stroke-rose-500 dark:stroke-rose-400",
          icon: <XCircle className="w-4 h-4 mr-1.5" />,
          colorText: "text-rose-500"
        };
      default:
        return {
          bg: "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/30",
          ring: "stroke-purple-500 dark:stroke-purple-400",
          icon: <Award className="w-4 h-4 mr-1.5" />,
          colorText: "text-purple-500"
        };
    }
  };

  const currentStyles = getBadgeStyle();

  return (
    <div 
      className="relative flex flex-col items-center justify-between p-6 rounded-2xl h-full border transition-all duration-300 backdrop-blur-md bg-white border-neutral-200 hover:shadow-md dark:bg-white/[0.03] dark:border-white/[0.08] dark:hover:bg-white/[0.05]"
      id="overall-match-card"
    >
      <div className="w-full flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold font-sora text-neutral-500 dark:text-neutral-400 uppercase tracking-widest flex items-center">
          <Award className="w-4 h-4 mr-2 text-purple-500 dark:text-purple-400" />
          Overall Match
        </h3>
        <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400">
          ATS SCORE
        </span>
      </div>

      <div className="relative py-6 flex items-center justify-center">
        {/* SVG Progress Gauge */}
        <svg className="w-36 h-36 transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="72"
            cy="72"
            r={radius}
            strokeWidth={strokeWidth}
            className="stroke-neutral-100 dark:stroke-neutral-800"
            fill="transparent"
          />
          {/* Animated Foreground circle */}
          <circle
            cx="72"
            cy="72"
            r={radius}
            strokeWidth={strokeWidth}
            className={`transition-all duration-1000 ease-out ${currentStyles.ring}`}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>

        {/* Big percentage text centered inside progress circle */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-extrabold font-sora text-neutral-800 dark:text-white flex items-baseline">
            {percentage}
            <span className="text-lg font-bold text-neutral-400 dark:text-neutral-500 ml-0.5">%</span>
          </span>
        </div>
      </div>

      {/* Fit Level Pill Indicator */}
      <div className="mt-2 w-full flex justify-center">
        <div 
          className={`flex items-center px-4 py-1.5 rounded-full border text-sm font-semibold font-sans uppercase tracking-wider ${currentStyles.bg} transition-transform hover:scale-105`}
          id="fit-level-badge"
        >
          {currentStyles.icon}
          {fitLevel}
        </div>
      </div>
    </div>
  );
}
