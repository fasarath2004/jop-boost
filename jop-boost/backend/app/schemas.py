from pydantic import BaseModel
from typing import List, Optional

class AnalyzeRequest(BaseModel):
    cvText: Optional[str] = ""
    cvBase64: Optional[str] = None
    cvMimeType: Optional[str] = None
    jobDesc: str

class SkillMissing(BaseModel):
    skill: str
    priority: str

class SkillGroup(BaseModel):
    possessed: List[str]
    missing: List[SkillMissing]

class SkillLearn(BaseModel):
    name: str
    progress: int
    impact: str
    hours: int

class SkillRadar(BaseModel):
    subject: str
    required: int
    you: int

class AnalyzeResponse(BaseModel):
    matchPercentage: int
    fitLevel: str
    summary: str
    skills: SkillGroup
    skillsLearn: List[SkillLearn]
    skillsRadar: List[SkillRadar]
    isMock: bool = False
    errorMessage: Optional[str] = None

class CoverLetterRequest(BaseModel):
    cvText: Optional[str] = ""
    jobDesc: str
    analysisSummary: Optional[str] = ""
    matchPercentage: Optional[int] = 85

class CoverLetterResponse(BaseModel):
    coverLetter: str
    isMock: bool = False
    errorMessage: Optional[str] = None
