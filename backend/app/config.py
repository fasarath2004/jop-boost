import os
import dotenv

# Load environment variables
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv.load_dotenv(os.path.join(parent_dir, ".env"))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# CORS Allowed Origins
ALLOWED_ORIGINS_STR = os.environ.get(
    "ALLOWED_ORIGINS", 
    "https://jop-boost-frontend.vercel.app,http://localhost:5173,http://127.0.0.1:5173"
)
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",") if origin.strip()]

