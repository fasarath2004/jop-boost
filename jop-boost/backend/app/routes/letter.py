import json
import logging
from fastapi import APIRouter
from google import genai
from google.genai import types

from app.schemas import CoverLetterRequest, CoverLetterResponse
from app.config import GEMINI_API_KEY
from app.ml.engine import TECH_SKILLS_CATEGORIES

router = APIRouter()
logger = logging.getLogger("LetterRoute")

# Initialize Gemini Client (lazy loader)
_genai_client = None

def get_genai_client():
    global _genai_client
    if _genai_client is None:
        if GEMINI_API_KEY and GEMINI_API_KEY != "MY_GEMINI_API_KEY" and GEMINI_API_KEY.strip() != "":
            logger.info("Initializing Google GenAI client with key.")
            _genai_client = genai.Client(api_key=GEMINI_API_KEY)
        else:
            logger.warning("No GEMINI_API_KEY found. Switched to offline cover letter generator.")
    return _genai_client

def generate_mock_cover_letter(cv_text: str, job_desc: str, match_pct: int) -> str:
    job_desc_lower = job_desc.lower()
    
    # Try finding skills mentioned
    skills = []
    for skill_list in TECH_SKILLS_CATEGORIES.values():
        for skill in skill_list:
            if skill in job_desc_lower and len(skill) > 3:
                skills.append(skill.title())
                if len(skills) >= 3:
                    break
        if len(skills) >= 3:
            break
            
    primary_skills = ", ".join(skills) if skills else "Frontend and Backend development"
    
    letter = (
        f"### Cover Letter (Offline Draft)\n\n"
        f"Dear Hiring Manager,\n\n"
        f"I am writing to express my strong interest in the open position matching my background. "
        f"Based on a local ML matching audit, my profile returns a **{match_pct}% compatibility match** "
        f"against your technical stack requirements.\n\n"
        f"My core competencies align exceptionally well with your target stack, particularly in areas like **{primary_skills}**. "
        f"Throughout my career, I have focused on writing clean, modular code, building highly performant services, and collaborating in agile teams. "
        f"I am confident that my qualifications will allow me to integrate smoothly and make a positive impact on your roadmap immediately.\n\n"
        f"Thank you for reviewing my application. I look forward to discussing how my experience fits your team's objectives.\n\n"
        f"Sincerely,\n"
        f"**Applicant**"
    )
    return letter

@router.post("/api/generate-cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter(request: CoverLetterRequest):
    client = get_genai_client()
    
    if not client:
        logger.info("Generating offline mock cover letter.")
        letter = generate_mock_cover_letter(request.cvText, request.jobDesc, request.matchPercentage)
        return CoverLetterResponse(coverLetter=letter, isMock=True)

    try:
        logger.info("Starting Gemini API Cover Letter generation...")
        
        prompt = (
            f"Applicant Resume Content:\n{request.cvText or 'Skilled professional'}\n\n"
            f"Target Job Description:\n{request.jobDesc}\n\n"
            f"ATS Matching Analytics Context:\n"
            f"Similarity Score: {request.matchPercentage}%\n"
            f"Fit Analysis Summary: {request.analysisSummary}\n\n"
            f"Please draft a highly targeted, elegant, and persuasive professional Cover Letter in markdown format based on this data. "
            f"Highlight how the applicant's existing skills match the core requirements, showing immediate value. "
            f"Return your response in JSON format holding a single 'coverLetter' string."
        )

        from pydantic import BaseModel

        class GeminiCoverLetterResponse(BaseModel):
            coverLetter: str

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeminiCoverLetterResponse,
                system_instruction="You are an expert executive resume writer and career consultant. Return a JSON object with 'coverLetter' containing a markdown cover letter.",
                temperature=0.0
            ),
        )

        response_text = response.text
        if not response_text:
            raise ValueError("No cover letter text received from Gemini.")
            
        data = json.loads(response_text)
        return CoverLetterResponse(coverLetter=data.get("coverLetter", ""), isMock=False)

    except Exception as e:
        logger.error(f"Gemini Cover Letter failed: {e}. Switched to offline template.")
        letter = generate_mock_cover_letter(request.cvText, request.jobDesc, request.matchPercentage)
        return CoverLetterResponse(
            coverLetter=letter,
            isMock=True,
            errorMessage=f"Gemini API failure: {str(e)}. Switched to offline generator."
        )
