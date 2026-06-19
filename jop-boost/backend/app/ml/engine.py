import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

logger = logging.getLogger("MLEngine")

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

# Flatten all skills for quick dictionary lookup
ALL_SKILLS = set()
for skills in TECH_SKILLS_CATEGORIES.values():
    ALL_SKILLS.update(skills)

# Global spaCy model reference (lazy loaded)
_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            # Load small English model
            _nlp = spacy.load("en_core_web_sm")
        except Exception:
            try:
                import spacy
                # Try downloading if not present
                logger.info("spaCy model 'en_core_web_sm' not found. Attempting download...")
                from spacy.cli import download
                download("en_core_web_sm")
                _nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                logger.warning(f"Could not load or download spaCy model 'en_core_web_sm': {e}. Falling back to basic preprocessing.")
                _nlp = None
    return _nlp

def preprocess_text_fallback(text: str) -> str:
    """Fallback text preprocessing using simple regex tokenization and common English stop words."""
    if not text:
        return ""
    # Simple tokenization: lowercase and find alphanumeric words
    words = re.findall(r'\b\w+\b', text.lower())
    # Basic set of English stop words
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
    processed_tokens = [w for w in words if w not in stop_words]
    return " ".join(processed_tokens)

def preprocess_text(text: str) -> str:
    """Preprocess text using spaCy (lowercase, lemmatize, remove stop words/punctuation).
    Falls back to basic preprocessing if spaCy is not available or fails."""
    if not text:
        return ""
    try:
        nlp = get_nlp()
        if nlp is not None:
            doc = nlp(text.lower())
            processed_tokens = []
            for token in doc:
                if not token.is_stop and not token.is_punct and not token.is_space:
                    processed_tokens.append(token.lemma_)
            return " ".join(processed_tokens)
    except Exception as e:
        logger.warning(f"spaCy preprocessing failed: {e}. Falling back to basic preprocessing.")
    
    return preprocess_text_fallback(text)

def extract_skills(text: str) -> set:
    """Extract known technical skills from text using phrase matching and token boundaries."""
    if not text:
        return set()
    
    text_lower = f" {text.lower()} "
    # Replace common punctuation with spaces to avoid token boundary issues
    text_clean = re.sub(r'[,;:\(\)\{\}\[\]\n\r\t]', ' ', text_lower)
    # Ensure double spaces are collapsed
    text_clean = re.sub(r'\s+', ' ', text_clean)

    extracted = set()
    
    # First: Match multi-word or exact phrase matches (like "spring boot" or "react.js")
    for skill in ALL_SKILLS:
        # Avoid matching small substrings like "go" inside "google" or "aws" inside "awesome"
        # We check word boundaries
        pattern = rf'\b{re.escape(skill)}\b'
        if re.search(pattern, text_clean):
            # Map clean normalized representation
            extracted.add(skill)

    # Return matching skill names formatted nicely
    # Match the extracted skill back to the display case in our category definitions
    result_map = {}
    for cat, skills in TECH_SKILLS_CATEGORIES.items():
        for skill in skills:
            if skill in extracted:
                # Store with correct capitalization (e.g. 'react.js' -> 'React.js')
                display_name = skill
                # Simple capitalization rules for nice presentation
                if skill == "react.js": display_name = "React.js"
                elif skill == "node.js": display_name = "Node.js"
                elif skill == "vue.js": display_name = "Vue.js"
                elif skill == "next.js": display_name = "Next.js"
                elif skill == "express.js": display_name = "Express.js"
                elif skill == "fastapi": display_name = "FastAPI"
                elif skill == "typescript": display_name = "TypeScript"
                elif skill == "javascript": display_name = "JavaScript"
                elif skill == "mongodb": display_name = "MongoDB"
                elif skill == "postgresql": display_name = "PostgreSQL"
                elif skill == "mysql": display_name = "MySQL"
                elif skill == "sqlite": display_name = "SQLite"
                elif skill == "nosql": display_name = "NoSQL"
                elif skill == "github": display_name = "GitHub"
                elif skill == "gitlab": display_name = "GitLab"
                elif skill == "spring boot": display_name = "Spring Boot"
                elif skill == "react native": display_name = "React Native"
                elif skill == "html5": display_name = "HTML5"
                elif skill == "css3": display_name = "CSS3"
                elif skill == "aws": display_name = "AWS"
                elif skill == "gcp": display_name = "GCP"
                elif skill == "ci/cd": display_name = "CI/CD"
                elif skill in ["html", "css", "sql", "git", "ecs", "s3", "ec2"]: 
                    display_name = skill.upper()
                else: 
                    display_name = skill.title()
                
                result_map[skill] = display_name
                
    return set(result_map.values())

def calculate_similarity(cv_text: str, jd_text: str) -> float:
    """Calculate the TF-IDF Cosine Similarity score between the CV and Job Description."""
    if not cv_text or not jd_text:
        return 0.0
    
    # Preprocess text to improve vectorizer relevance
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
        # Fallback if vocabulary could not be fit (e.g. short input)
        return 0.0

def build_radar_chart_data(cv_skills: set, jd_skills: set) -> list:
    """Calculate match metrics for 5 radar categories."""
    radar_data = []
    
    cv_skills_lower = {s.lower() for s in cv_skills}
    jd_skills_lower = {s.lower() for s in jd_skills}
    
    for category, skills in TECH_SKILLS_CATEGORIES.items():
        # Get category skills required in the Job Description
        required_in_cat = [s for s in skills if s in jd_skills_lower]
        # Get category skills possessed by the CV
        possessed_in_cat = [s for s in skills if s in cv_skills_lower]
        
        # Determine baseline requirements (default to some target if none mentioned)
        if len(required_in_cat) > 0:
            required_score = 80 + min(20, len(required_in_cat) * 5)  # Range 80-100
            # Calculate match level
            match_ratio = len([s for s in possessed_in_cat if s in required_in_cat]) / len(required_in_cat)
            you_score = int(match_ratio * required_score)
        else:
            # Baseline levels if category is not requested by the JD
            required_score = 50
            if len(possessed_in_cat) > 0:
                you_score = min(90, 50 + len(possessed_in_cat) * 10)
            else:
                you_score = 25
                
        # Ensure 'you' score is within reasonable limits
        you_score = max(20, min(you_score, 100))
        
        radar_data.append({
            "subject": category,
            "required": required_score,
            "you": you_score
        })
        
    return radar_data
