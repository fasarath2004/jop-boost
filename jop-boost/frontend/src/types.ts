export interface SkillMissing {
  skill: string;
  priority: 'Priority 1' | 'Nice to have';
}

export interface SkillGap {
  possessed: string[];
  missing: SkillMissing[];
}

export interface SuggestedSkill {
  name: string;
  progress: number;
  impact: string;
  hours: number;
}

export interface RadarData {
  subject: string;
  required: number;
  you: number;
}

export interface AnalysisResponse {
  matchPercentage: number;
  fitLevel: 'Strong Fit' | 'Moderate Fit' | 'Development Needed';
  summary: string;
  skills: SkillGap;
  skillsLearn: SuggestedSkill[];
  skillsRadar: RadarData[];
}

export interface CoverLetterResponse {
  coverLetter: string;
}
