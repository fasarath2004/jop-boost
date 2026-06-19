import logging
import os
import time
import threading
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Setup router and logging
router = APIRouter()
logger = logging.getLogger("QARoute")
logger.setLevel(logging.INFO)

# Retrieve Gemini API key securely from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Rate limiter: only call Gemini every N requests to preserve quota
_qa_gemini_counter = 0
_qa_counter_lock = threading.Lock()
QA_GEMINI_INTERVAL = int(os.environ.get("QA_GEMINI_INTERVAL", "20"))

# Request and Response Pydantic Validation Models
class QARequest(BaseModel):
    question: str = Field(..., description="The user's question to be answered by the AI.")
    context_keys: Optional[List[str]] = Field(None, description="Optional keys to retrieve specific context from the database.")

class QAResponse(BaseModel):
    answer: str
    context_used: bool

# Mock Database for Knowledge Retrieval (Context)
# In a real system, this would be a Vector Database (e.g., Pinecone, Milvus) or a Relational DB.
MOCK_DATABASE = {
    "resume_tips": "A good resume should highlight technical skills clearly and quantify achievements.",
    "interview_prep": "Use the STAR method (Situation, Task, Action, Result) for behavioral interviews.",
    "ml_project": "The NLP Resume Match project uses TF-IDF cosine similarity, Skill Overlaps, and a tuned Linear Support Vector Classifier."
}

def retrieve_context_from_db(keys: Optional[List[str]]) -> str:
    """
    Simulates database retrieval. The database role is STRICTLY context storage/retrieval.
    """
    if not keys:
        # Default context if no specific keys are provided
        return "You are an expert AI Assistant answering questions based on context."
    
    retrieved_contexts = []
    for key in keys:
        if key in MOCK_DATABASE:
            retrieved_contexts.append(MOCK_DATABASE[key])
            
    if not retrieved_contexts:
        return "No relevant context found in the database."
    
    return " ".join(retrieved_contexts)

def generate_with_gemini_with_retry(prompt: str, max_retries: int = 3) -> str:
    """
    Sends prompt to Gemini API. Incorporates rate-limit handling with exponential backoff.
    Ensures absolutely NO local models are used.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "MY_GEMINI_API_KEY" or GEMINI_API_KEY.strip() == "":
        logger.error("Gemini API key is not configured.")
        raise HTTPException(status_code=500, detail="Server configuration error: Missing Gemini API Key.")
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Sending request to Gemini API (Attempt {attempt})...")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2, # Low temperature for factual RAG responses
                    system_instruction="You are an expert assistant. Answer the user's question relying strictly on the provided context."
                )
            )
            
            if not response.text:
                raise ValueError("Received empty response from Gemini API.")
                
            return response.text
            
        except Exception as e:
            error_str = str(e).lower()
            # Handle rate limits or quota errors
            if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
                logger.warning(f"Rate limit hit. Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
            else:
                logger.error(f"Gemini API Error: {str(e)}")
                raise HTTPException(status_code=502, detail=f"External API Error: {str(e)}")
                
    raise HTTPException(status_code=429, detail="Exceeded maximum retries due to rate limiting.")

def generate_mock_answer(question: str, context: str) -> str:
    return (
        f"Based on the available context, here is my response:\n\n"
        f"{context[:500]}\n\n"
        f"*This is a local fallback response. Enable Gemini API calls for AI-powered answers.*"
    )

@router.post("/api/qa", response_model=QAResponse)
async def process_question(request: QARequest):
    """
    Primary endpoint adhering to the strict workflow:
    User Question -> Retrieve Context -> Send to Gemini -> Return Response.
    """
    logger.info(f"Received question: {request.question}")
    
    # 1. Retrieve Context
    logger.info("Retrieving context from database...")
    context = retrieve_context_from_db(request.context_keys)
    
    # 2. Construct Prompt
    prompt = f"Context:\n{context}\n\nQuestion: {request.question}\n\nAnswer strictly based on the context provided."
    
    # 3. Rate limit: use local fallback on most requests, call Gemini only every N requests
    global _qa_gemini_counter
    with _qa_counter_lock:
        _qa_gemini_counter += 1
        should_use_gemini = (
            bool(GEMINI_API_KEY)
            and GEMINI_API_KEY != "MY_GEMINI_API_KEY"
            and _qa_gemini_counter % QA_GEMINI_INTERVAL == 0
        )
    
    if not should_use_gemini:
        logger.info(f"Using local fallback (request #{_qa_gemini_counter}, Gemini every {QA_GEMINI_INTERVAL}).")
        answer = generate_mock_answer(request.question, context)
        return QAResponse(
            answer=answer,
            context_used=bool(request.context_keys)
        )
    
    # 4. Generate Answer via external Gemini API
    logger.info("Generating answer via external Gemini API...")
    answer = generate_with_gemini_with_retry(prompt)
    
    # 5. Return formatted response
    logger.info("Successfully generated response.")
    return QAResponse(
        answer=answer,
        context_used=bool(request.context_keys)
    )
