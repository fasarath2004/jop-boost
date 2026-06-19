from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import analyze, letter
from app.config import ALLOWED_ORIGINS

app = FastAPI(
    title="CareerPulse AI Backend",
    description="Structured FastAPI + Machine Learning Resume Matching System",
    version="1.0.0"
)

# Setup CORS with explicit allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(analyze.router)
app.include_router(letter.router)

@app.get("/")
def read_root():
    return {"status": "running", "service": "CareerPulse API"}
