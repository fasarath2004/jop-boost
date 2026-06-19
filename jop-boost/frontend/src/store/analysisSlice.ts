import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../utils/api';
import { AnalysisResponse, SkillGap, SuggestedSkill, RadarData } from '../types';
import { SAMPLES } from '../utils/samples';

// API Response type additions
interface ExtendedAnalysisResponse extends AnalysisResponse {
  isMock?: boolean;
  errorMessage?: string;
}

export interface AnalysisState {
  // Theme state
  theme: 'dark' | 'light';

  // Resume / Job Description form states
  cvText: string;
  cvFileName: string | null;
  cvBase64: string | null;
  cvMimeType: string | null;
  jobDesc: string;
  isDragOver: boolean;

  // Analysis result states
  isAnalyzing: boolean;
  analysisResult: AnalysisResponse | null;
  
  // Cover letter generation states
  isGeneratingLetter: boolean;
  coverLetter: string;

  // User notifications
  errorMsg: string | null;
  successMsg: string | null;
}

const getInitialTheme = (): 'dark' | 'light' => {
  const saved = localStorage.getItem('careerpulse-theme');
  return (saved as 'dark' | 'light') || 'dark';
};

const initialState: AnalysisState = {
  theme: getInitialTheme(),
  cvText: '',
  cvFileName: null,
  cvBase64: null,
  cvMimeType: null,
  jobDesc: '',
  isDragOver: false,
  isAnalyzing: false,
  analysisResult: null,
  isGeneratingLetter: false,
  coverLetter: '',
  errorMsg: null,
  successMsg: null,
};

// Async Thunk for CV Analysis
export const runAnalysisThunk = createAsyncThunk<
  ExtendedAnalysisResponse,
  { cvText: string; cvBase64: string | null; cvMimeType: string | null; jobDesc: string },
  { rejectValue: string }
>(
  'analysis/runAnalysis',
  async (payload, { rejectWithValue }) => {
    try {
      const res = await api.post<ExtendedAnalysisResponse>('/analyze', payload);
      return res.data;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'An unexpected error occurred during CV fit matching.';
      return rejectWithValue(msg);
    }
  }
);

// Async Thunk for Cover Letter Generation
export const generateCoverLetterThunk = createAsyncThunk<
  string,
  { cvText: string; jobDesc: string; analysisSummary: string; matchPercentage: number },
  { rejectValue: string }
>(
  'analysis/generateCoverLetter',
  async (payload, { rejectWithValue }) => {
    try {
      const res = await api.post<{ coverLetter: string; errorMessage?: string }>('/generate-cover-letter', payload);
      return res.data.coverLetter;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to draft custom cover letter.';
      return rejectWithValue(msg);
    }
  }
);

const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    toggleTheme(state) {
      state.theme = state.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('careerpulse-theme', state.theme);
    },
    setCvText(state, action: PayloadAction<string>) {
      state.cvText = action.payload;
    },
    setCvFileName(state, action: PayloadAction<string | null>) {
      state.cvFileName = action.payload;
    },
    setCvBase64(state, action: PayloadAction<string | null>) {
      state.cvBase64 = action.payload;
    },
    setCvMimeType(state, action: PayloadAction<string | null>) {
      state.cvMimeType = action.payload;
    },
    setJobDesc(state, action: PayloadAction<string>) {
      state.jobDesc = action.payload;
    },
    setIsDragOver(state, action: PayloadAction<boolean>) {
      state.isDragOver = action.payload;
    },
    setErrorMsg(state, action: PayloadAction<string | null>) {
      state.errorMsg = action.payload;
    },
    setSuccessMsg(state, action: PayloadAction<string | null>) {
      state.successMsg = action.payload;
    },
    editCoverLetter(state, action: PayloadAction<string>) {
      state.coverLetter = action.payload;
    },
    clearCV(state) {
      state.cvText = '';
      state.cvFileName = null;
      state.cvBase64 = null;
      state.cvMimeType = null;
      state.errorMsg = null;
    },
    clearAllAnalysis(state) {
      state.analysisResult = null;
      state.coverLetter = '';
    },
    clearAllFields(state) {
      state.cvText = '';
      state.cvFileName = null;
      state.cvBase64 = null;
      state.cvMimeType = null;
      state.jobDesc = '';
      state.analysisResult = null;
      state.coverLetter = '';
      state.errorMsg = null;
      state.successMsg = null;
    },
    loadPresetSample(state, action: PayloadAction<number>) {
      const index = action.payload;
      if (index >= 0 && index < SAMPLES.length) {
        const sample = SAMPLES[index];
        state.cvText = sample.cv;
        state.jobDesc = sample.jd;
        state.cvFileName = `Preset_CV_${sample.title.replace(/\s+/g, '_')}.txt`;
        state.cvBase64 = null;
        state.cvMimeType = null;
        state.errorMsg = null;
        state.coverLetter = '';

        // Default mock structures matching Alex Rivera vs Taylor Brooks presets
        if (index === 0) {
          state.analysisResult = {
            matchPercentage: 85,
            fitLevel: 'Strong Fit',
            summary: "Based on an automated ATS assessment of Alex Rivera's qualifications against the Senior Fullstack Engineer specs, client alignment is evaluated at 85%. You present robust credentials in React.js, Node.js, and Agile methodologies, which align closely with primary prerequisites. However, addressing knowledge gaps in GraphQL and AWS cloud will bypass traditional ATS constraints.",
            skills: {
              possessed: ["React.js", "Node.js", "Agile / Scrum", "TypeScript", "Tailwind CSS"],
              missing: [
                { skill: "GraphQL", priority: "Priority 1" },
                { skill: "AWS (EC2/S3)", priority: "Priority 1" },
                { skill: "Docker", priority: "Nice to have" }
              ]
            },
            skillsLearn: [
              { name: "GraphQL Fundamentals", progress: 0, impact: "High impact for this role. Est. 10 hours for core proficiency.", hours: 10 },
              { name: "AWS Cloud Practitioner", progress: 20, impact: "Foundational knowledge required. Est. 15 hours.", hours: 15 },
              { name: "Docker Basics", progress: 50, impact: "Good to have for containerization. Est. 5 hours.", hours: 5 }
            ],
            skillsRadar: [
              { subject: "React", required: 90, you: 88 },
              { subject: "Python", required: 40, you: 10 },
              { subject: "Cloud", required: 85, you: 20 },
              { subject: "Leadership", required: 80, you: 75 },
              { subject: "Node.js", required: 85, you: 80 }
            ]
          };
        } else {
          state.analysisResult = {
            matchPercentage: 42,
            fitLevel: 'Development Needed',
            summary: "Based on an automated ATS assessment, Taylor Brooks presents substantial expertise in Python data automation, NumPy, and databases, but lacks React or modern frontend state knowledge requested by PixelStudio.",
            skills: {
              possessed: ["SQL / PostgreSQL", "System Design"],
              missing: [
                { skill: "React.js", priority: "Priority 1" },
                { skill: "TypeScript", priority: "Priority 1" },
                { skill: "Tailwind CSS", priority: "Priority 1" },
                { skill: "Docker", priority: "Nice to have" }
              ]
            },
            skillsLearn: [
              { name: "React.js Essentials", progress: 5, impact: "High impact. Est. 25 hours for core coding proficiency.", hours: 25 },
              { name: "TypeScript BootCamp", progress: 10, impact: "High impact. Est. 12 hours.", hours: 12 },
              { name: "Tailwind CSS Layouts", progress: 15, impact: "Good to have. Est. 4 hours.", hours: 4 }
            ],
            skillsRadar: [
              { subject: "React", required: 95, you: 10 },
              { subject: "Python", required: 20, you: 85 },
              { subject: "Cloud", required: 50, you: 15 },
              { subject: "Leadership", required: 60, you: 30 },
              { subject: "TypeScript", required: 85, you: 12 }
            ]
          };
        }
      }
    }
  },
  extraReducers: (builder) => {
    // runAnalysisThunk Reducers
    builder.addCase(runAnalysisThunk.pending, (state) => {
      state.isAnalyzing = true;
      state.errorMsg = null;
      state.coverLetter = '';
    });
    builder.addCase(runAnalysisThunk.fulfilled, (state, action) => {
      state.isAnalyzing = false;
      state.analysisResult = action.payload;
      if (action.payload.errorMessage) {
        state.errorMsg = `Simulation Alert: ${action.payload.errorMessage}`;
      } else if (action.payload.isMock) {
        state.successMsg = 'Analysis completed securely via adaptive mock pipeline.';
      } else {
        state.successMsg = 'Success! ATS Career Analysis completed via Gemini.';
      }
    });
    builder.addCase(runAnalysisThunk.rejected, (state, action) => {
      state.isAnalyzing = false;
      state.analysisResult = null;
      state.errorMsg = action.payload || 'An error occurred during matching.';
    });

    // generateCoverLetterThunk Reducers
    builder.addCase(generateCoverLetterThunk.pending, (state) => {
      state.isGeneratingLetter = true;
      state.errorMsg = null;
    });
    builder.addCase(generateCoverLetterThunk.fulfilled, (state, action) => {
      state.isGeneratingLetter = false;
      state.coverLetter = action.payload;
    });
    builder.addCase(generateCoverLetterThunk.rejected, (state, action) => {
      state.isGeneratingLetter = false;
      state.errorMsg = action.payload || 'Failed to draft custom cover letter.';
    });
  }
});

export const {
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
  clearCV,
  clearAllAnalysis,
  clearAllFields,
  loadPresetSample,
} = analysisSlice.actions;

export default analysisSlice.reducer;
