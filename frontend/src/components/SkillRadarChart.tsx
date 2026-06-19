import React from "react";
import { RadarData } from "../types";
import { Compass } from "lucide-react";

interface SkillRadarChartProps {
  data: RadarData[];
}

export default function SkillRadarChart({ data }: SkillRadarChartProps) {
  const numPoints = data.length;
  if (!data || numPoints === 0) return null;

  // Radar dimensions
  const size = 300;
  const center = size / 2;
  const maxRadius = 90; // Limit radius so text labels fit on 300x300 viewBox

  // Math helper to get Coordinates matching angle
  const getCoordinates = (index: number, value: number) => {
    // Subtract PI / 2 to start spokes pointing straight up
    const angle = (2 * Math.PI * index) / numPoints - Math.PI / 2;
    const radius = (value / 100) * maxRadius;
    const x = center + radius * Math.cos(angle);
    const y = center + radius * Math.sin(angle);
    return { x, y };
  };

  // 1. Grid Rings levels (20%, 40%, 60%, 80%, 100%)
  const gridLevels = [20, 40, 60, 80, 100];

  // 2. Compute Polygon Paths
  const requiredPoints = data.map((d, i) => getCoordinates(i, d.required));
  const youPoints = data.map((d, i) => getCoordinates(i, d.you));

  const requiredPath = requiredPoints.map(p => `${p.x},${p.y}`).join(" ");
  const youPath = youPoints.map(p => `${p.x},${p.y}`).join(" ");

  return (
    <div 
      className="flex flex-col items-center justify-between p-6 rounded-2xl h-full border transition-all duration-300 backdrop-blur-md bg-white border-neutral-200 hover:shadow-md dark:bg-white/[0.03] dark:border-white/[0.08] dark:hover:bg-white/[0.05]"
      id="skill-alignment-card"
    >
      <div className="w-full flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold font-sora text-neutral-500 dark:text-neutral-400 uppercase tracking-widest flex items-center">
          <Compass className="w-4 h-4 mr-2 text-cyan-500" />
          Skill Alignment
        </h3>
        <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400">
          PROFILE COMPARISON
        </span>
      </div>

      <div className="relative w-full flex items-center justify-center">
        {/* SVG Wrapper */}
        <svg viewBox={`0 0 ${size} ${size}`} className="w-full max-w-[260px] h-auto">
          {/* Grids */}
          {gridLevels.map((level, levelIdx) => {
            const levelPoints = data.map((_, i) => getCoordinates(i, level));
            const pathString = levelPoints.map(p => `${p.x},${p.y}`).join(" ");
            return (
              <polygon
                key={levelIdx}
                points={pathString}
                fill="none"
                className="stroke-neutral-200 dark:stroke-neutral-800"
                strokeWidth="0.75"
                strokeDasharray={level === 100 ? "0" : "2,2"}
              />
            );
          })}

          {/* Spokes (axis lines) */}
          {data.map((_, i) => {
            const outerPoint = getCoordinates(i, 100);
            return (
              <line
                key={i}
                x1={center}
                y1={center}
                x2={outerPoint.x}
                y2={outerPoint.y}
                className="stroke-neutral-200 dark:stroke-neutral-800"
                strokeWidth="0.75"
              />
            );
          })}

          {/* REQUIRED area (dashed violet border, empty overlay) */}
          <polygon
            points={requiredPath}
            fill="rgba(139, 92, 246, 0.03)"
            className="stroke-purple-600/60 dark:stroke-purple-500/50"
            strokeWidth="1.5"
            strokeDasharray="3,3"
          />

          {/* YOU area (cyan filled translucent overlay with solid border) */}
          <polygon
            points={youPath}
            fill="rgba(6, 182, 212, 0.15)"
            className="stroke-cyan-500 dark:stroke-cyan-400"
            strokeWidth="2"
          />

          {/* Vertex Nodes for YOU stats */}
          {youPoints.map((p, i) => (
            <circle
              key={i}
              cx={p.x}
              cy={p.y}
              r="3.5"
              className="fill-cyan-400 stroke-cyan-600 dark:fill-cyan-300 dark:stroke-cyan-500"
              strokeWidth="1"
            />
          ))}

          {/* Subject Labels */}
          {data.map((item, i) => {
            const textAngle = (2 * Math.PI * i) / numPoints - Math.PI / 2;
            const stretchRadius = maxRadius + 16; // stretch outward for text spacing
            const x = center + stretchRadius * Math.cos(textAngle);
            const y = center + stretchRadius * Math.sin(textAngle);

            // Anchor adjust based on position
            let textAnchor = "middle";
            if (Math.cos(textAngle) > 0.1) textAnchor = "start";
            else if (Math.cos(textAngle) < -0.1) textAnchor = "end";

            // Tiny vertical offset adjustment
            let dy = "0.35em";
            if (Math.sin(textAngle) < -0.9) dy = "-0.1em"; // straight up
            else if (Math.sin(textAngle) > 0.9) dy = "0.8em"; // straight down

            return (
              <text
                key={i}
                x={x}
                y={y}
                textAnchor={textAnchor}
                dy={dy}
                className="text-[10px] font-semibold tracking-wide font-sora fill-neutral-600 dark:fill-neutral-400"
              >
                {item.subject}
              </text>
            );
          })}
        </svg>
      </div>

      {/* Mini Legend Indicator */}
      <div className="mt-4 flex items-center justify-center gap-6 text-xs font-medium font-sans">
        <div className="flex items-center">
          <span className="w-3 h-3 rounded-full border border-dashed border-purple-500 bg-purple-500/5 mr-2" />
          <span className="text-neutral-500 dark:text-neutral-400">Required</span>
        </div>
        <div className="flex items-center">
          <span className="w-3 h-3 rounded-full border border-cyan-500 bg-cyan-500/20 mr-2" />
          <span className="text-neutral-500 dark:text-neutral-400">You</span>
        </div>
      </div>
    </div>
  );
}
