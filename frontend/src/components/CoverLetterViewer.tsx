import React, { useState, useRef } from "react";
import { Sparkles, FileText, Copy, Check, Download, Edit2, CheckSquare, RefreshCw, ArrowRight } from "lucide-react";

interface CoverLetterViewerProps {
  coverLetterText: string;
  isGenerating: boolean;
  onGenerate: () => void;
  onSaveEdit: (newText: string) => void;
}

export default function CoverLetterViewer({
  coverLetterText,
  isGenerating,
  onGenerate,
  onSaveEdit
}: CoverLetterViewerProps) {
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState("");
  const editAreaRef = useRef<HTMLTextAreaElement>(null);

  // Markdown parsing helper for clean typography without external dependencies
  const parseMarkdownToJSX = (text: string) => {
    if (!text || text.trim() === "") return <p className="text-neutral-400 dark:text-neutral-500 italic text-xs">No content.</p>;
    
    return text.split("\n").map((line, idx) => {
      const trimmed = line.trim();
      
      // Headers
      if (trimmed.startsWith("### ")) {
        return (
          <h4 key={idx} className="text-base font-bold font-sora mt-4 mb-2 text-neutral-800 dark:text-neutral-100 first:mt-0">
            {trimmed.replace("### ", "")}
          </h4>
        );
      }
      if (trimmed.startsWith("## ")) {
        return (
          <h3 key={idx} className="text-lg font-bold font-sora mt-5 mb-2 text-neutral-800 dark:text-neutral-100">
            {trimmed.replace("## ", "")}
          </h3>
        );
      }
      if (trimmed.startsWith("# ")) {
        return (
          <h2 key={idx} className="text-xl font-extrabold font-sora mt-6 mb-3 text-neutral-800 dark:text-neutral-500">
            {trimmed.replace("# ", "")}
          </h2>
        );
      }
      
      // Bullets
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        return (
          <li key={idx} className="list-disc ml-5 mb-1.5 text-xs text-neutral-600 dark:text-neutral-300">
            {parseBolds(trimmed.substring(2))}
          </li>
        );
      }
      
      // Empty spaces
      if (trimmed === "") {
        return <div key={idx} className="h-3" />;
      }
      
      // Standard Paragraph
      return (
        <p key={idx} className="text-xs leading-relaxed mb-3 text-neutral-600 dark:text-neutral-300">
          {parseBolds(line)}
        </p>
      );
    });
  };

  // Nest bold string elements helper
  const parseBolds = (text: string) => {
    const parts = text.split(/\*\*([^*]+)\*\*/g);
    return parts.map((part, i) => 
      i % 2 === 1 ? (
        <strong key={i} className="font-bold text-neutral-900 dark:text-white">
          {part}
        </strong>
      ) : (
        part
      )
    );
  };

  // Copy to clipboard helper
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(coverLetterText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.warn("Failed to copy using clipboard API", err);
    }
  };

  // Download markdown helper
  const handleDownload = () => {
    const blob = new Blob([coverLetterText], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "Automated_Cover_Letter.md");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Edit states
  const beginEditing = () => {
    setEditedText(coverLetterText);
    setIsEditing(true);
  };

  const saveEditing = () => {
    onSaveEdit(editedText);
    setIsEditing(false);
  };

  return (
    <div 
      className="p-6 rounded-2xl border transition-all duration-300 backdrop-blur-md bg-white border-neutral-200 dark:bg-white/[0.03] dark:border-white/[0.08]"
      id="cover-letter-section"
    >
      {/* If Cover Letter has not been generated yet, show dynamic prompt banner */}
      {!coverLetterText && !isGenerating && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-2" id="prompt-generate-ctas">
          <div className="flex items-start space-x-3 text-center sm:text-left">
            <div className="p-2 h-10 w-10 flex items-center justify-center rounded-lg bg-purple-500/10 text-purple-600 dark:text-cyan-400">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">Ready to apply?</h4>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">
                Let AI craft a highly targeted cover letter based on this exact analysis.
              </p>
            </div>
          </div>
          <button
            onClick={onGenerate}
            disabled={isGenerating}
            className="w-full sm:w-auto px-5 py-2.5 rounded-lg font-semibold text-xs uppercase tracking-wider flex items-center justify-center space-x-2 bg-gradient-to-r from-purple-600 to-cyan-500 text-white shadow-xl shadow-purple-500/10 hover:shadow-cyan-500/20 active:scale-95 transition-all"
            id="cover-letter-generate-btn"
          >
            <span>Generate Cover Letter</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </button>
        </div>
      )}

      {/* Loading state showing smooth system progression */}
      {isGenerating && (
        <div className="flex flex-col items-center justify-center py-10 text-center space-y-4" id="loader-panel">
          <div className="relative p-1">
            <div className="w-12 h-12 rounded-full border-4 border-purple-500/15 border-t-purple-600 dark:border-cyan-500/20 dark:border-t-cyan-400 animate-spin" />
            <Sparkles className="absolute inset-0 m-auto w-5 h-5 text-purple-500 dark:text-cyan-400 animate-pulse" />
          </div>
          <div className="space-y-1">
            <h5 className="text-sm font-semibold font-sora text-neutral-800 dark:text-white">Crafting Tailored Alignment Cover Letter...</h5>
            <p className="text-xs text-neutral-400 dark:text-neutral-500 animate-pulse">Matching keywords, structuring benefits, and polishing tone</p>
          </div>
        </div>
      )}

      {/* Renders the Cover Letter in interactive viewer after completion */}
      {coverLetterText && !isGenerating && (
        <div className="space-y-4" id="loaded-letter-view">
          
          {/* Header Action controls */}
          <div className="flex items-center justify-between border-b pb-3.5 border-neutral-100 dark:border-neutral-800/60">
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-purple-600 dark:text-cyan-400" />
              <span className="text-sm font-semibold font-sora text-neutral-800 dark:text-white">Draft cover Letter</span>
            </div>
            
            <div className="flex items-center gap-1.5 sm:gap-2">
              {isEditing ? (
                <button
                  onClick={saveEditing}
                  className="px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider rounded border flex items-center bg-emerald-500/10 text-emerald-600 border-emerald-500/20 hover:bg-emerald-500/20 dark:text-emerald-400"
                  id="save-edit-btn"
                >
                  <CheckSquare className="w-3.5 h-3.5 mr-1" />
                  <span>Save</span>
                </button>
              ) : (
                <button
                  onClick={beginEditing}
                  className="px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider rounded border flex items-center bg-neutral-100 hover:bg-neutral-200/80 text-neutral-700 border-neutral-200 dark:bg-neutral-900 dark:border-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-800"
                  id="edit-letter-btn"
                >
                  <Edit2 className="w-3.5 h-3.5 mr-1" />
                  <span>Edit</span>
                </button>
              )}

              <button
                onClick={handleCopy}
                disabled={isEditing}
                className={`px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider rounded border flex items-center transition-all ${
                  copied 
                    ? "bg-emerald-500/10 text-emerald-600 border-emerald-500/20 dark:text-emerald-400" 
                    : "bg-neutral-100 hover:bg-neutral-200/80 text-neutral-700 border-neutral-200 dark:bg-neutral-900 dark:border-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-800"
                }`}
                id="copy-letter-btn"
              >
                {copied ? <Check className="w-3.5 h-3.5 mr-1" /> : <Copy className="w-3.5 h-3.5 mr-1" />}
                <span>{copied ? "Copied" : "Copy"}</span>
              </button>

              <button
                onClick={handleDownload}
                disabled={isEditing}
                className="px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider rounded border flex items-center bg-neutral-100 hover:bg-neutral-200/80 text-neutral-700 border-neutral-200 dark:bg-neutral-900 dark:border-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-800"
                id="download-letter-btn"
                title="Download as Markdown"
              >
                <Download className="w-3.5 h-3.5 mr-1" />
                <span>Format</span>
              </button>

              <button
                onClick={onGenerate}
                loading={isGenerating}
                className="p-1 px-2 rounded border bg-purple-500/5 hover:bg-purple-500/10 hover:text-purple-600 text-purple-500 border-purple-500/20 dark:hover:text-cyan-400 dark:hover:bg-cyan-500/5 dark:border-cyan-500/20"
                id="re-generate-btn"
                title="Regenerate Cover Letter"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Letter Body presentation */}
          <div className="relative rounded-xl overflow-hidden min-h-[160px] p-5 border border-dashed border-neutral-200/60 bg-neutral-50/20 dark:border-neutral-800/60 dark:bg-[#08090A]/20">
            {isEditing ? (
              <textarea
                ref={editAreaRef}
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
                className="w-full min-h-[250px] bg-transparent text-xs font-mono border-0 focus:ring-0 focus:outline-none leading-relaxed text-neutral-800 dark:text-neutral-200"
                id="letter-edit-textarea"
                rows={12}
              />
            ) : (
              <div className="prose prose-sm dark:prose-invert font-sans max-w-none text-left" id="letter-rendered-markdown">
                {parseMarkdownToJSX(coverLetterText)}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
