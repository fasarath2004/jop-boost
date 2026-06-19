import base64
import io
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pypdf import PdfReader
from google import genai
from google.genai import types

from app.schemas import AnalyzeRequest, AnalyzeResponse, SkillGroup, SkillMissing, SkillLearn, SkillRadar
from app.ml import engine as ml_engine
from app.config import GEMINI_API_KEY

router = APIRouter()
logger = logging.getLogger("AnalyzeRoute")

# Initialize Gemini Client (lazy loader)
_genai_client = None

def get_genai_client():
    global _genai_client
    if _genai_client is None:
        if GEMINI_API_KEY and GEMINI_API_KEY != "MY_GEMINI_API_KEY" and GEMINI_API_KEY.strip() != "":
            logger.info("Initializing Google GenAI client with key.")
            _genai_client = genai.Client(api_key=GEMINI_API_KEY)
        else:
            logger.warning("No GEMINI_API_KEY found. Switched to offline ML mode.")
    return _genai_client

# PDF Text Extractor Helper
def extract_text_from_pdf_base64(base64_str: str) -> str:
    try:
        # Strip metadata header if present
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        pdf_bytes = base64.b64decode(base64_str)
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error parsing PDF Base64: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF document: {str(e)}")

# Fallback generator for offline matching
def generate_mock_response(cv_text: str, job_desc: str, possessed: List[str], missing: List[str], similarity_score: float) -> AnalyzeResponse:
    total_jd_skills = len(possessed) + len(missing)
    overlap_ratio = len(possessed) / total_jd_skills if total_jd_skills > 0 else 0.5
    
    # Combined score formula
    match_percentage = int((similarity_score * 0.4 + overlap_ratio * 0.6) * 100)
    match_percentage = max(40, min(match_percentage, 98))
    
    fit_level = "Moderate Fit"
    if match_percentage >= 80:
        fit_level = "Strong Fit"
    elif match_percentage < 60:
        fit_level = "Development Needed"

    possessed_skills = possessed if possessed else ["React.js", "Node.js", "Agile / Scrum"]
    missing_skills_list = [{"skill": s, "priority": "Priority 1" if i % 2 == 0 else "Nice to have"} for i, s in enumerate(missing)]
    if not missing_skills_list:
        missing_skills_list = [
            {"skill": "GraphQL", "priority": "Priority 1"},
            {"skill": "AWS (EC2/S3)", "priority": "Priority 1"},
            {"skill": "Docker", "priority": "Nice to have"}
        ]

    skills_learn = []
    for idx, missing_item in enumerate(missing_skills_list[:3]):
        hours = (idx + 1) * 5 + 5
        progress = int((idx + 1) * 20 % 70)
        skills_learn.append(SkillLearn(
            name=f"{missing_item['skill']} Fundamentals",
            progress=progress,
            impact="High impact for this role. Est. {} hours.".format(hours) if missing_item["priority"] == "Priority 1" else "Recommended addition. Est. {} hours.".format(hours),
            hours=hours
        ))
    if not skills_learn:
        skills_learn = [
            SkillLearn(name="System Design Essentials", progress=30, impact="High impact. Est. 12 hours.", hours=12)
        ]

    radar_data = ml_engine.build_radar_chart_data(set(possessed_skills), set(possessed_skills + [m["skill"] for m in missing_skills_list]))
    skills_radar = [SkillRadar(subject=r["subject"], required=r["required"], you=r["you"]) for r in radar_data]

    summary_text = (
        f"Based on a local machine learning TF-IDF vector analysis of your qualifications against the target requirements, "
        f"your candidate alignment is evaluated at {match_percentage}%. You present robust credentials in {', '.join(possessed_skills[:3])}, "
        f"which align closely with primary stack prerequisites. However, addressing knowledge gaps in key target aspects—specifically "
        f"{', '.join([m['skill'] for m in missing_skills_list[:2]])}—will significantly bolster tracking score compliance to bypass ATS constraints."
    )

    return AnalyzeResponse(
        matchPercentage=match_percentage,
        fitLevel=fit_level,
        summary=summary_text,
        skills=SkillGroup(
            possessed=possessed_skills,
            missing=[SkillMissing(skill=m["skill"], priority=m["priority"]) for m in missing_skills_list]
        ),
        skillsLearn=skills_learn,
        skillsRadar=skills_radar,
        isMock=True
    )

@router.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_resume(request: AnalyzeRequest):
    cv_text = request.cvText or ""
    
    if request.cvBase64 and request.cvMimeType == "application/pdf":
        logger.info("Extracting text from PDF resume...")
        cv_text = extract_text_from_pdf_base64(request.cvBase64)
    
    if not cv_text.strip():
        cv_text = "Standard starter candidate profile"

    job_desc = request.jobDesc
    if not job_desc.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")

    # 1. Run local ML skill extraction
    cv_skills = ml_engine.extract_skills(cv_text)
    jd_skills = ml_engine.extract_skills(job_desc)

    possessed = list(cv_skills.intersection(jd_skills))
    missing = list(jd_skills - cv_skills)

    # 2. Run local TF-IDF cosine similarity
    similarity = ml_engine.calculate_similarity(cv_text, job_desc)
    logger.info(f"Local Cosine Similarity: {similarity:.4f}")

    # 3. Check for Gemini client
    client = get_genai_client()
    if not client:
        logger.info("Using local matching engine fallback.")
        return generate_mock_response(cv_text, job_desc, possessed, missing, similarity)

    # 4. Invoke Gemini Structured analysis
    try:
        total_skills_count = len(possessed) + len(missing)
        overlap_ratio = len(possessed) / total_skills_count if total_skills_count > 0 else 0.5
        local_match_score = int((similarity * 0.4 + overlap_ratio * 0.6) * 100)
        local_match_score = max(40, min(local_match_score, 99))
        local_radar = ml_engine.build_radar_chart_data(cv_skills, jd_skills)

        prompt = (
            f"Candidate Resume Text:\n{cv_text}\n\n"
            f"Target Job Description:\n{job_desc}\n\n"
            f"--- ML Analytics Reference ---\n"
            f"TF-IDF Cosine Similarity Score: {similarity:.4f}\n"
            f"Extracted Possessed Skills: {', '.join(possessed)}\n"
            f"Extracted Missing Skills: {', '.join(missing)}\n"
            f"Calculated Baseline Match Percentage: {local_match_score}%\n"
            f"Calculated Local Radar Levels: {json.dumps(local_radar)}\n"
            f"---------------------------------\n\n"
            f"Please conduct an expert Recruiters/ATS assessment comparing the Candidate Resume to the Target Job Description. "
            f"Use the ML Reference as your baseline constraints. "
            f"You MUST return a JSON response matching the schema. Structure requirements:\n"
            f"- matchPercentage: refine the match score (between 40 and 100) based on your expert evaluation, staying close to the baseline {local_match_score}%.\n"
            f"- fitLevel: 'Strong Fit' (80+), 'Moderate Fit' (60-79), or 'Development Needed' (<60).\n"
            f"- summary: A detailed 3-4 sentence professional commentary explaining the candidate's alignment, core strengths, and critical gaps.\n"
            f"- skills: Categorize the tech skills. possessed: list of strings. missing: list of objects with 'skill' and 'priority' ('Priority 1' for critical gaps, 'Nice to have' for minor gaps).\n"
            f"- skillsLearn: Exactly 3 highly targeted, actionable recommendations of courses/subjects to learn to bridge the gaps. For each, estimate current progress (0-80), impact text, and hours required (integer).\n"
            f"- skillsRadar: Exactly 5 items matching the subjects: 'Frontend', 'Backend', 'Cloud', 'Database', 'DevOps'. Populate required level and evaluated candidate level (0-100), aligning with the local radar references."
        )

        system_instruction = (
            "You are CareerPulse AI, an advanced applicant tracking system (ATS) expert, tech recruiter, and professional career advisor. "
            "Evaluate competencies, technical stacks, methodologies, soft skills, and experiences. "
            "You must return your results exclusively in JSON matching the requested schema structure."
        )

        from pydantic import BaseModel

        class GeminiSkillMissing(BaseModel):
            skill: str
            priority: str

        class GeminiSkillGroup(BaseModel):
            possessed: List[str]
            missing: List[GeminiSkillMissing]

        class GeminiSkillLearn(BaseModel):
            name: str
            progress: int
            impact: str
            hours: int

        class GeminiSkillRadar(BaseModel):
            subject: str
            required: int
            you: int

        class GeminiAnalysisResponse(BaseModel):
            matchPercentage: int
            fitLevel: str
            summary: str
            skills: GeminiSkillGroup
            skillsLearn: List[GeminiSkillLearn]
            skillsRadar: List[GeminiSkillRadar]

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeminiAnalysisResponse,
                system_instruction=system_instruction,
                temperature=0.0
            ),
        )

        response_text = response.text
        if not response_text:
            raise ValueError("Empty output token from Gemini API.")
            
        data = json.loads(response_text)
        return AnalyzeResponse(
            matchPercentage=data.get("matchPercentage", local_match_score),
            fitLevel=data.get("fitLevel", "Moderate Fit"),
            summary=data.get("summary", ""),
            skills=SkillGroup(
                possessed=data.get("skills", {}).get("possessed", possessed),
                missing=[SkillMissing(skill=m["skill"], priority=m["priority"]) for m in data.get("skills", {}).get("missing", [])]
            ),
            skillsLearn=[SkillLearn(name=s["name"], progress=s["progress"], impact=s["impact"], hours=s["hours"]) for s in data.get("skillsLearn", [])],
            skillsRadar=[SkillRadar(subject=s["subject"], required=s["required"], you=s["you"]) for s in data.get("skillsRadar", [])],
            isMock=False
        )

    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}. Switching to offline fallback.")
        fallback = generate_mock_response(cv_text, job_desc, possessed, missing, similarity)
        fallback.errorMessage = f"Gemini API failure: {str(e)}. Switched to local ML matcher."
        return fallback
