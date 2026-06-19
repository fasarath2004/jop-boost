import React from "react";
import { Sun, Moon, Activity, Code, ExternalLink } from "lucide-react";

interface HeaderProps {
  theme: "dark" | "light";
  toggleTheme: () => void;
}

export default function Header({ theme, toggleTheme }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b backdrop-blur-md bg-opacity-80 transition-colors duration-300 border-neutral-200/50 bg-[#f8f9fa] dark:border-neutral-800/50 dark:bg-[#121315]/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Logo and Brand Name */}
        <div className="flex items-center space-x-3" id="logo-container">
          <div className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-gradient-to-tr from-purple-600 to-cyan-500 shadow-lg shadow-purple-500/20">
            <Activity className="w-5 h-5 text-white animate-pulse" />
          </div>
          <span 
            className="text-xl font-bold font-sora tracking-tight bg-gradient-to-r from-purple-600 to-cyan-500 dark:from-purple-400 dark:to-cyan-400 bg-clip-text text-transparent"
            id="brand-name"
          >
            CareerPulse AI
          </span>
        </div>

        {/* Action Controls & External Badges */}
        <div className="flex items-center space-x-4">
         {/*  <a
            href="https://ai.studio/build"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:flex items-center space-x-1.5 px-3 h-8 text-[12px] font-medium font-mono rounded-full border border-neutral-200 text-neutral-600 bg-neutral-50/50 hover:bg-neutral-100 hover:text-black transition dark:border-neutral-800 dark:text-neutral-400 dark:bg-neutral-900/30 dark:hover:bg-neutral-800/50 dark:hover:text-white"
          >
            <Code className="w-3.5 h-3.5" />
            <span>AI Studio</span>
            <ExternalLink className="w-2.5 h-2.5" />
          </a> */}

          {/* Theme Selector Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg border transition duration-300 focus:outline-none border-neutral-200 hover:bg-neutral-100 hover:text-purple-700 bg-white dark:border-neutral-800 dark:bg-neutral-900 dark:hover:bg-neutral-800 dark:hover:text-cyan-400"
            id="theme-toggle-btn"
            aria-label="Toggle visual theme"
            title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {theme === "dark" ? (
              <Sun className="w-4 h-4 text-cyan-400 animate-spin-slow" />
            ) : (
              <Moon className="w-4 h-4 text-purple-700" />
            )}
          </button>
        </div>

      </div>
    </header>
  );
}
