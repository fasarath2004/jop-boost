import React, { useEffect } from "react";
import { 
  FileText, 
  Upload, 
  Sparkles, 
  Check, 
  Trash2, 
  AlertCircle,
  RefreshCw,
  FileCheck
} from "lucide-react";

import Header from "./components/Header";
import OverallMatch from "./components/OverallMatch";
import SkillRadarChart from "./components/SkillRadarChart";
import SkillGapAnalysis from "./components/SkillGapAnalysis";
import LearningProgress from "./components/LearningProgress";
import CoverLetterViewer from "./components/CoverLetterViewer";

import { useAppDispatch, useAppSelector } from "./store/store";
import {
  toggleTheme,
  setCvText,
  setCvFileName,
  setCvBase64,
  setCvMimeType,
  setJobDesc,
  setIsDragOver,
  setErrorMsg,
  setSuccessMsg,
  editCoverLetter,
  clearAllAnalysis,
  clearCV,
  clearAllFields,
  runAnalysisThunk,
  generateCoverLetterThunk
} from "./store/analysisSlice";

export default function App() {
  const dispatch = useAppDispatch();
  
  // Extract all states from Redux Toolkit store
  const {
    theme,
    cvText,
    cvFileName,
    cvBase64,
    cvMimeType,
    jobDesc,
    isDragOver,
    isAnalyzing,
    analysisResult,
    isGeneratingLetter,
    coverLetter,
    errorMsg,
    successMsg
  } = useAppSelector((state) => state.analysis);

  // Sync theme changes
  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);



  // Automatically clear success notifications after a timeout
  useEffect(() => {
    if (successMsg) {
      const timer = setTimeout(() => {
        dispatch(setSuccessMsg(null));
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [successMsg, dispatch]);

  const handleToggleTheme = () => {
    dispatch(toggleTheme());
  };



  // Drag and drop events
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    dispatch(setIsDragOver(true));
  };

  const handleDragLeave = () => {
    dispatch(setIsDragOver(false));
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    dispatch(setIsDragOver(false));
    dispatch(setErrorMsg(null));

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      processSelectedFile(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(setErrorMsg(null));
    const files = e.target.files;
    if (files && files.length > 0) {
      processSelectedFile(files[0]);
    }
  };

  // Convert uploaded CV to readable txt or base64 PDF
  const processSelectedFile = (file: File) => {
    const isPDF = file.type === "application/pdf" || file.name.endsWith(".pdf");
    const isTXT = file.type === "text/plain" || file.name.endsWith(".txt") || file.name.endsWith(".md");

    dispatch(clearAllAnalysis());
    dispatch(setCvFileName(file.name));

    if (isPDF) {
      const reader = new FileReader();
      reader.onload = () => {
        const resultString = reader.result as string;
        dispatch(setCvBase64(resultString));
        dispatch(setCvMimeType("application/pdf"));
        dispatch(setCvText(`[PDF File Uploaded: ${file.name}]`));
        dispatch(setSuccessMsg(`"${file.name}" uploaded successfully. Ready for ATS evaluation.`));
      };
      reader.onerror = () => {
        dispatch(setErrorMsg("Failed to decode your PDF file."));
      };
      reader.readAsDataURL(file);
    } else if (isTXT) {
      const reader = new FileReader();
      reader.onload = () => {
        const textResult = reader.result as string;
        dispatch(setCvText(textResult));
        dispatch(setCvBase64(null));
        dispatch(setCvMimeType(null));
        dispatch(setSuccessMsg(`"${file.name}" read successfully.`));
      };
      reader.onerror = () => {
        dispatch(setErrorMsg("Failed to parse your text file content."));
      };
      reader.readAsText(file);
    } else {
      // General treatment for docx/other formats
      dispatch(setCvText(`Candidate Background details uploaded via doc: ${file.name}`));
      dispatch(setCvBase64(null));
      dispatch(setCvMimeType(null));
      dispatch(setSuccessMsg(`"${file.name}" recognized. Paste exact text below for precision or proceed with analysis.`));
    }
  };

  const handleClearCV = () => {
    dispatch(clearCV());
  };

  // 1. Analyze Action trigger dispatching Redux Thunk
  const runAnalysis = () => {
    if (!jobDesc || jobDesc.trim() === "") {
      dispatch(setErrorMsg("Please paste a target job description to verify. Job Description cannot be empty."));
      return;
    }
    dispatch(runAnalysisThunk({ cvText, cvBase64, cvMimeType, jobDesc }));
  };

  // 2. Clear All Inputs and reset
  const handleClearAllFields = () => {
    dispatch(clearAllFields());
  };

  // 3. Generate Cover letter trigger dispatching Redux Thunk
  const runCoverLetterGeneration = () => {
    if (!analysisResult) return;
    dispatch(
      generateCoverLetterThunk({
        cvText,
        jobDesc,
        analysisSummary: analysisResult.summary,
        matchPercentage: analysisResult.matchPercentage
      })
    );
  };

  // Save manual modifications to the generated letter text
  const handleSaveCoverLetterEdit = (newText: string) => {
    dispatch(editCoverLetter(newText));
  };

  return (
    <div 
      className={`${theme} min-h-screen flex flex-col bg-[#f8f9fa] text-neutral-800 dark:bg-[#121315] dark:text-[#e3e2e3] font-sans transition-colors duration-300`}
    >
      {/* 1. Navbar Top Header */}
      <Header theme={theme} toggleTheme={handleToggleTheme} />

      {/* 2. Main Content Body */}
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
        
        {/* Pitch Hero Heading */}
        <div className="text-center space-y-4 max-w-3xl mx-auto" id="pitch-hero">
          <h1 
            className="text-4xl sm:text-5xl font-extrabold font-sora tracking-tight leading-tight text-neutral-900 dark:text-white"
            id="main-title text"
          >
            Supercharge Your <span className="bg-gradient-to-r from-purple-600 via-indigo-500 to-cyan-500 dark:from-purple-400 dark:to-cyan-400 bg-clip-text text-transparent">Career Journey</span>
          </h1>
          <p className="text-sm sm:text-base leading-relaxed text-neutral-500 dark:text-neutral-400 font-sans">
            Paste your target job description and upload your CV. Our AI will instantly analyze
            your fit, identify skill gaps, and optimize your application for ATS systems.
          </p>
        </div>



        {/* Global Notifications Panel (Success or Warnings) */}
        {errorMsg && (
          <div className="p-3.5 border rounded-xl flex items-start space-x-3 bg-rose-500/10 border-rose-500/20 text-rose-700 dark:text-rose-400" id="error-toast">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div className="text-xs font-medium leading-relaxed">{errorMsg}</div>
          </div>
        )}

        {successMsg && (
          <div className="p-3.5 border rounded-xl flex items-start space-x-3 bg-emerald-500/10 border-emerald-500/20 text-emerald-700 dark:text-emerald-400 animate-pulse" id="success-toast">
            <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div className="text-xs font-medium leading-relaxed">{successMsg}</div>
          </div>
        )}

        {/* 3. Inputs Interactive Workstation Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" id="inputs-workstation-grid">
          
          {/* Card left: Drag and Drop Upload Resume */}
          <div 
            className={`flex flex-col p-6 rounded-2xl border transition-all duration-300 backdrop-blur-md bg-white border-neutral-200 dark:bg-white/[0.03] dark:border-white/[0.08] ${
              isDragOver ? "border-purple-600 ring-2 ring-purple-600/10 dark:border-cyan-400 dark:ring-cyan-500/10 scale-[1.01]" : ""
            }`}
            id="drag-drop-container"
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold font-sora text-neutral-500 dark:text-neutral-400 uppercase tracking-widest flex items-center">
                <FileText className="w-4 h-4 mr-1.5 text-purple-600 dark:text-cyan-400" />
                Upload Your CV
              </span>
              {cvFileName && (
                <button
                  onClick={handleClearCV}
                  className="text-xs text-rose-500 hover:text-rose-600 font-semibold flex items-center bg-transparent border-none outline-none focus:outline-none"
                  title="Clear Resume data"
                >
                  <Trash2 className="w-3.5 h-3.5 mr-1" />
                  Clear
                </button>
              )}
            </div>

            {/* Dropping box */}
            <div className="flex-grow flex flex-col justify-between">
              <div 
                className={`relative flex-grow min-h-[160px] border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-6 text-center transition-all ${
                  isDragOver 
                    ? "border-purple-500 bg-purple-500/5" 
                    : "border-neutral-200 bg-neutral-50/50 hover:bg-neutral-50 hover:border-neutral-300 dark:border-white/[0.05] dark:bg-white/[0.01] dark:hover:bg-white/[0.02]"
                }`}
              >
                <input
                  type="file"
                  id="cv-upload-input"
                  className="hidden"
                  accept=".txt,.pdf,.md"
                  onChange={handleFileInput}
                />
                
                {cvFileName ? (
                  <div className="space-y-3 p-4">
                    <div className="w-10 h-10 rounded-lg bg-emerald-500/10 text-emerald-500 dark:text-emerald-400 flex items-center justify-center mx-auto shadow-md">
                      <FileCheck className="w-6 h-6" />
                    </div>
                    <div className="space-y-1">
                      <p className="text-xs font-bold font-sora text-neutral-800 dark:text-white max-w-[280px] truncate mx-auto">
                        {cvFileName}
                      </p>
                      <p className="text-[10px] font-mono font-medium text-neutral-400 dark:text-neutral-400">
                        {cvBase64 ? "PDF Base64 format loaded" : "Text file processed"}
                      </p>
                    </div>
                  </div>
                ) : (
                  <label htmlFor="cv-upload-input" className="cursor-pointer space-y-3.5 group block w-full h-full p-4">
                    <div className="w-11 h-11 rounded-full bg-neutral-100 dark:bg-neutral-900 text-neutral-400 dark:text-neutral-400 group-hover:text-purple-600 dark:group-hover:text-cyan-400 group-hover:bg-purple-500/5 dark:group-hover:bg-cyan-500/5 flex items-center justify-center mx-auto shadow-sm transition">
                      <Upload className="w-5 h-5" />
                    </div>
                    <div className="space-y-1">
                      <p className="text-xs font-bold text-neutral-700 dark:text-neutral-300">
                        Drag & drop your PDF or Word doc
                      </p>
                      <p className="text-[10px] text-neutral-400 dark:text-neutral-400 font-sans">
                        or click to browse
                      </p>
                    </div>
                  </label>
                )}
              </div>

              {/* Text fallback display or raw resume manual entry option */}
              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-[10px] font-bold uppercase tracking-wide text-neutral-400 dark:text-neutral-400 font-mono">
                    Resume Text Summary / Raw Entry:
                  </label>
                  <span className="text-[10px] font-mono text-neutral-400 dark:text-neutral-500">
                    {cvText.length} chars
                  </span>
                </div>
                <textarea
                  value={cvText}
                  onChange={(e) => dispatch(setCvText(e.target.value))}
                  placeholder="Raw text from resume will automatically populate here once uploaded, or you can paste your biography details directly here..."
                  className="w-full text-xs font-sans p-3 rounded-xl border leading-relaxed bg-neutral-50/20 text-neutral-700 placeholder-neutral-400 border-neutral-200 outline-none focus:ring-1 focus:ring-purple-500/40 focus:border-purple-500 dark:bg-neutral-900/30 dark:text-neutral-300 dark:border-white/[0.06] dark:focus:ring-cyan-500/20 dark:focus:border-cyan-400 min-h-[110px]"
                  id="cv-raw-text-area"
                />
              </div>

            </div>
          </div>

          {/* Card Right: Paste Job Description */}
          <div 
            className="flex flex-col p-6 rounded-2xl border bg-white border-neutral-200 dark:bg-white/[0.03] dark:border-white/[0.08]"
            id="job-desc-container"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold font-sora text-neutral-500 dark:text-neutral-400 uppercase tracking-widest flex items-center">
                <FileText className="w-4 h-4 mr-1.5 text-indigo-500" />
                Paste Job Description
              </span>
              {jobDesc && (
                <button
                  onClick={() => dispatch(setJobDesc(""))}
                  className="text-xs text-neutral-400 hover:text-neutral-600 font-medium bg-transparent border-none focus:outline-none"
                >
                  Clear Description
                </button>
              )}
            </div>

            <div className="flex-grow flex flex-col justify-between">
              <textarea
                value={jobDesc}
                onChange={(e) => dispatch(setJobDesc(e.target.value))}
                placeholder="Paste the full job description here..."
                className="w-full text-xs font-sans p-4 rounded-xl border leading-relaxed bg-neutral-50/20 text-neutral-700 placeholder-neutral-400 border-neutral-200 outline-none focus:ring-1 focus:ring-indigo-500/30 focus:border-indigo-500 dark:bg-neutral-900/30 dark:text-neutral-300 dark:border-white/[0.06] dark:focus:ring-cyan-500/20 dark:focus:border-cyan-400 flex-grow min-h-[305px]"
                id="job-description-textarea"
              />
            </div>
          </div>

        </div>

        {/* 4. "Analyze Now" Action Button positioned between sections */}
        <div className="flex justify-center -my-3 relative z-10" id="analyze-action-wrapper">
          <button
            onClick={runAnalysis}
            disabled={isAnalyzing}
            className="px-8 py-3.5 rounded-xl font-bold font-sora text-xs uppercase tracking-widest flex items-center justify-center space-x-2 bg-gradient-to-r from-purple-600 to-cyan-500 text-white shadow-xl shadow-purple-500/10 hover:shadow-cyan-500/20 hover:scale-[1.02] active:scale-95 transition-all w-full sm:w-auto"
            id="analyze-now-btn"
          >
            {isAnalyzing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Running ATS Audit...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-white hover:animate-ping" />
                <span>Analyze Now</span>
              </>
            )}
          </button>
        </div>

        {/* 5. Comprehensive Analysis Reports Section (Revealed if loaded or analyzed) */}
        {analysisResult && (
          <div className="space-y-6 pt-6" id="dashboard-report-section">
            <h2 
              className="text-xl font-bold font-sora text-neutral-800 dark:text-neutral-300 flex items-center py-2 border-b border-neutral-200/50 dark:border-neutral-800/50"
              id="report-section-header"
            >
              <Sparkles className="w-5 h-5 mr-2.5 text-purple-600 dark:text-cyan-400 animate-pulse" />
              Comprehensive Analysis
            </h2>

            {/* Top Row: Overall Match and Skill Radar Comparison charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6" id="charts-bento-grid">
              
              {/* Overall Match Circle Gauge */}
              <OverallMatch 
                percentage={analysisResult.matchPercentage} 
                fitLevel={analysisResult.fitLevel} 
              />

              {/* SVG Radar Chart mapping Required vs Candidate */}
              <SkillRadarChart 
                data={analysisResult.skillsRadar} 
              />

            </div>

            {/* Bottom Row: Skill Gap Listing and Suggested Learning tracks */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6" id="details-bento-grid">
              
              {/* Matched vs Missing Skill Gap */}
              <SkillGapAnalysis 
                skills={analysisResult.skills} 
              />

              {/* Progress items for recommended topics list */}
              <LearningProgress 
                skillsLearn={analysisResult.skillsLearn} 
              />

            </div>

            {/* Dynamic summary report commentary card banner */}
            <div 
              className="p-5 rounded-2xl border glass-gradient leading-relaxed bg-white/50 border-neutral-100 dark:border-white/[0.05] dark:bg-white/[0.01]"
              id="summary-commentary-banner"
            >
              <h4 className="text-[11px] font-bold uppercase tracking-widest text-neutral-400 font-mono mb-2">
                🤖 AI EXECUTIVE SUMMARY ASSIGNMENT
              </h4>
              <p className="text-xs leading-relaxed text-neutral-600 dark:text-neutral-300">
                {analysisResult.summary}
              </p>
            </div>

            {/* 6. Cover Letter generator section nested inside main dashboard */}
            <CoverLetterViewer
              coverLetterText={coverLetter}
              isGenerating={isGeneratingLetter}
              onGenerate={runCoverLetterGeneration}
              onSaveEdit={handleSaveCoverLetterEdit}
            />

          </div>
        )}

      </main>

      {/* 3. Page Footer */}
      <footer className="py-6 border-t font-sans border-neutral-200/50 dark:border-neutral-800/40 text-center text-xs text-neutral-400 dark:text-neutral-500 space-y-1">
        <p>© 2026 CareerPulse AI. Crafted for the high-stakes environment of career growth.</p>
        <p className="text-[11px] font-medium text-neutral-500 dark:text-neutral-400">
          Designed & Developed by <span className="text-purple-600 dark:text-cyan-400 font-semibold">Group-9</span>
        </p>
      </footer>
    </div>
  );
}
