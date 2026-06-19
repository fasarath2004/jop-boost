import logging
import os
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import spacy
except ImportError:
    spacy = None

logger = logging.getLogger("MLEngine")

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.joblib")
MODEL_PATH = os.path.join(MODEL_DIR, "match_model.joblib")

# Standard tech vocabulary grouped by categories for skill extraction and radar charts
TECH_SKILLS_CATEGORIES = {
    "Frontend": [
        "react", "react.js", "angular", "vue", "vue.js", "next.js", "svelte",
        "html", "html5", "css", "css3", "tailwind", "tailwind css", "bootstrap",
        "typescript", "javascript", "redux", "graphql", "webpack", "vite",
        "sass", "less", "jquery", "flutter", "react native"
    ],
    "Backend": [
        "node.js", "node", "express", "express.js", "fastapi", "django", "flask",
        "spring boot", "spring", "go", "golang", "ruby on rails", "rails",
        "asp.net", "net core", "nestjs", "graphql", "laravel", "php", "gunicorn"
    ],
    "Cloud": [
        "aws", "amazon web services", "azure", "gcp", "google cloud", "google cloud platform",
        "docker", "kubernetes", "k8s", "serverless", "lambda", "ecs", "s3", "ec2",
        "heroku", "netlify", "vercel", "cloudflare"
    ],
    "Database": [
        "mongodb", "postgresql", "postgres", "mysql", "sql", "sqlite", "nosql",
        "redis", "cassandra", "dynamodb", "oracle", "firebase", "firestore",
        "mariadb", "neo4j"
    ],
    "DevOps": [
        "git", "github", "gitlab", "ci/cd", "continuous integration", "jenkins",
        "github actions", "terraform", "ansible", "linux", "bash", "docker",
        "kubernetes", "prometheus", "grafana", "nginx"
    ]
}

ALL_SKILLS = set()
for skills in TECH_SKILLS_CATEGORIES.values():
    ALL_SKILLS.update(skills)

_nlp = None
_model = None
_vectorizer = None

def load_model():
    global _model, _vectorizer
    if _model is not None and _vectorizer is not None:
        return
    try:
        _vectorizer = joblib.load(VECTORIZER_PATH)
        _model = joblib.load(MODEL_PATH)
        logger.info("Loaded trained model.")
    except Exception as e:
        logger.warning(f"Could not load trained model: {e}")
        _model = None
        _vectorizer = None

def model_available() -> bool:
    load_model()
    return _model is not None and _vectorizer is not None

def get_combined_text(cv_text: str, jd_text: str) -> str:
    cv_clean = preprocess_text(cv_text)
    jd_clean = preprocess_text(jd_text)
    return f"{cv_clean} [SEP] {jd_clean}"

def predict_match(cv_text: str, jd_text: str) -> float:
    load_model()
    if not model_available():
        return 0.0
    try:
        import sys
        import numpy as np
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ml_pipe_path = os.path.join(base_dir, "ml_pipeline")
        if ml_pipe_path not in sys.path:
            sys.path.append(ml_pipe_path)
        from features import extract_features_for_sample
        
        features = extract_features_for_sample(cv_text, jd_text, _vectorizer)
        
        if hasattr(_model, "predict_proba"):
            prob = _model.predict_proba(features)[0][1]
        elif hasattr(_model, "decision_function"):
            df_val = _model.decision_function(features)[0]
            prob = 1 / (1 + np.exp(-df_val))
        else:
            pred = _model.predict(features)[0]
            prob = float(pred)
            
        score = prob * 100.0
        return float(max(0.0, min(100.0, score)))
    except Exception as e:
        logger.warning(f"Model prediction failed: {e}")
        return 0.0

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            try:
                import spacy
                _nlp = spacy.load("en_core_web_sm")
            except Exception:
                import spacy
                import subprocess
                logger.info("spaCy model 'en_core_web_sm' not found. Attempting download...")
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
                _nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(
                f"Could not load or download spaCy model 'en_core_web_sm': {e}. "
                "Falling back to basic preprocessing."
            )
            _nlp = None
    return _nlp

def preprocess_text_fallback(text: str) -> str:
    if not text:
        return ""
    words = re.findall(r"\b\w+\b", text.lower())
    stop_words = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
        "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
        "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
        "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
        "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
        "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
        "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
        "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
        "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
        "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
        "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
    }
    return " ".join([w for w in words if w not in stop_words])

def preprocess_text(text: str) -> str:
    if not text:
        return ""
    try:
        nlp = get_nlp()
        if nlp is not None:
            doc = nlp(text.lower())
            tokens = [
                token.lemma_ for token in doc
                if not token.is_stop and not token.is_punct and not token.is_space
            ]
            return " ".join(tokens)
    except Exception as e:
        logger.warning(f"spaCy preprocessing failed: {e}")
    return preprocess_text_fallback(text)

def extract_skills(text: str) -> set:
    if not text:
        return set()
    text_lower = f" {text.lower()} "
    text_clean = re.sub(r"[,;:\(\)\{\}\[\]\n\r\t]", " ", text_lower)
    text_clean = re.sub(r"\s+", " ", text_clean)
    extracted = set()
    for skill in ALL_SKILLS:
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text_clean):
            extracted.add(skill)
    result_map = {}
    for skills in TECH_SKILLS_CATEGORIES.values():
        for skill in skills:
            if skill in extracted:
                display_name = skill
                if skill == "react.js":
                    display_name = "React.js"
                elif skill == "node.js":
                    display_name = "Node.js"
                elif skill == "vue.js":
                    display_name = "Vue.js"
                elif skill == "next.js":
                    display_name = "Next.js"
                elif skill == "express.js":
                    display_name = "Express.js"
                elif skill == "fastapi":
                    display_name = "FastAPI"
                elif skill == "typescript":
                    display_name = "TypeScript"
                elif skill == "javascript":
                    display_name = "JavaScript"
                elif skill == "mongodb":
                    display_name = "MongoDB"
                elif skill == "postgresql":
                    display_name = "PostgreSQL"
                elif skill == "mysql":
                    display_name = "MySQL"
                elif skill == "sqlite":
                    display_name = "SQLite"
                elif skill == "nosql":
                    display_name = "NoSQL"
                elif skill == "github":
                    display_name = "GitHub"
                elif skill == "gitlab":
                    display_name = "GitLab"
                elif skill == "spring boot":
                    display_name = "Spring Boot"
                elif skill == "react native":
                    display_name = "React Native"
                elif skill == "html5":
                    display_name = "HTML5"
                elif skill == "css3":
                    display_name = "CSS3"
                elif skill == "aws":
                    display_name = "AWS"
                elif skill == "gcp":
                    display_name = "GCP"
                elif skill == "ci/cd":
                    display_name = "CI/CD"
                elif skill in ["html", "css", "sql", "git", "ecs", "s3", "ec2"]:
                    display_name = skill.upper()
                else:
                    display_name = skill.title()
                result_map[skill] = display_name
    return set(result_map.values())

def calculate_similarity(cv_text: str, jd_text: str) -> float:
    if not cv_text or not jd_text:
        return 0.0
    cv_clean = preprocess_text(cv_text)
    jd_clean = preprocess_text(jd_text)
    if not cv_clean or not jd_clean:
        return 0.0
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([cv_clean, jd_clean])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity)
    except Exception:
        return 0.0

def build_radar_chart_data(cv_skills: set, jd_skills: set) -> list:
    radar_data = []
    cv_skills_lower = {s.lower() for s in cv_skills}
    jd_skills_lower = {s.lower() for s in jd_skills}
    for category, skills in TECH_SKILLS_CATEGORIES.items():
        required_in_cat = [s for s in skills if s in jd_skills_lower]
        possessed_in_cat = [s for s in skills if s in cv_skills_lower]
        if len(required_in_cat) > 0:
            required_score = 80 + min(20, len(required_in_cat) * 5)
            match_ratio = len([s for s in possessed_in_cat if s in required_in_cat]) / len(required_in_cat)
            you_score = int(match_ratio * required_score)
        else:
            required_score = 50
            if len(possessed_in_cat) > 0:
                you_score = min(90, 50 + len(possessed_in_cat) * 10)
            else:
                you_score = 25
        you_score = max(20, min(you_score, 100))
        radar_data.append({"subject": category, "required": required_score, "you": you_score})
    return radar_data