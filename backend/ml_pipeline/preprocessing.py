import re
import string

# Comprehensive skills lexicon covering all 24 job categories in the dataset
TECH_SKILLS = {
    # Technology & Programming
    "react", "react.js", "angular", "vue", "vue.js", "next.js", "svelte",
    "html", "css", "tailwind", "bootstrap", "typescript", "javascript",
    "node.js", "node", "express", "fastapi", "django", "flask", "spring",
    "go", "golang", "ruby", "rails", "aws", "azure", "gcp", "docker",
    "kubernetes", "mongodb", "postgresql", "mysql", "sql", "sqlite", "redis",
    "git", "github", "jenkins", "terraform", "linux", "nginx",
    "c++", "c#", ".net", "ci/cd", "python", "java", "php", "scala",
    "swift", "kotlin", "rust", "perl", "matlab", "hadoop", "spark",
    "tableau", "power bi", "machine learning", "deep learning", "tensorflow",
    "pytorch", "nlp", "data science", "api", "rest", "microservices",
    "agile", "scrum", "devops", "sap", "oracle", "salesforce", "jira",
    # Accounting & Finance
    "accountant", "accounting", "finance", "financial", "audit", "tax",
    "ledger", "bookkeeping", "gaap", "ifrs", "cpa", "quickbooks",
    "accounts payable", "accounts receivable", "budgeting", "forecasting",
    "payroll", "reconciliation", "financial reporting", "cost accounting",
    "revenue", "compliance", "treasury", "investment", "banking",
    "credit", "risk management", "underwriting", "portfolio",
    # Healthcare
    "healthcare", "medical", "nursing", "patient care", "clinical",
    "diagnosis", "treatment", "pharmacy", "radiology", "surgery",
    "ehr", "hipaa", "cpr", "bls", "acls", "vital signs",
    "medical records", "triage", "rehabilitation", "therapy",
    "physician", "registered nurse", "laboratory",
    # Sales & Marketing
    "sales", "marketing", "crm", "lead generation", "negotiation",
    "business development", "account management", "cold calling",
    "pipeline", "revenue growth", "client relations", "b2b", "b2c",
    "branding", "digital marketing", "seo", "sem", "ppc",
    "social media", "content marketing", "email marketing",
    "market research", "advertising", "campaign",
    # Human Resources
    "human resources", "recruitment", "talent acquisition", "onboarding",
    "performance management", "employee relations", "compensation",
    "benefits administration", "hris", "workforce planning",
    "training and development", "labor relations", "succession planning",
    # Engineering
    "engineering", "mechanical", "electrical", "civil", "chemical",
    "structural", "cad", "autocad", "solidworks", "matlab",
    "project management", "pmp", "quality assurance", "qa",
    "testing", "manufacturing", "lean", "six sigma",
    # Education & Teaching
    "teaching", "curriculum", "lesson planning", "classroom management",
    "assessment", "pedagogy", "student engagement", "tutoring",
    "education", "special education", "instruction", "literacy",
    # Design
    "design", "graphic design", "ui/ux", "photoshop", "illustrator",
    "figma", "sketch", "indesign", "typography", "branding",
    "wireframing", "prototyping", "adobe creative suite",
    # Construction
    "construction", "project management", "safety", "osha",
    "blueprint", "estimating", "scheduling", "concrete",
    "plumbing", "welding", "carpentry", "renovation",
    # Aviation
    "aviation", "pilot", "flight", "aircraft", "faa",
    "navigation", "air traffic", "maintenance", "aerospace",
    # Agriculture
    "agriculture", "farming", "crop", "livestock", "irrigation",
    "soil", "harvest", "pesticide", "organic", "agronomy",
    # Legal / Advocate
    "legal", "law", "litigation", "contract", "compliance",
    "attorney", "advocate", "paralegal", "regulatory", "arbitration",
    # Chef / Culinary
    "chef", "culinary", "cooking", "kitchen", "menu planning",
    "food safety", "catering", "pastry", "restaurant",
    # Fitness
    "fitness", "personal training", "nutrition", "exercise",
    "wellness", "coaching", "strength", "conditioning",
    # BPO / Customer Service
    "bpo", "call center", "customer service", "customer support",
    "outsourcing", "help desk", "ticketing", "escalation",
    # Public Relations
    "public relations", "media relations", "press release",
    "crisis communication", "stakeholder", "communications",
    # Apparel / Fashion
    "apparel", "fashion", "textile", "merchandising", "retail",
    "inventory", "supply chain", "logistics", "procurement",
    # Arts
    "arts", "creative", "portfolio", "exhibition", "gallery",
    # Automobile
    "automobile", "automotive", "vehicle", "engine", "transmission",
    "diagnostics", "repair", "maintenance",
    # Consultant
    "consulting", "consultant", "strategy", "advisory", "analysis",
    "stakeholder management", "change management", "transformation",
    # Digital Media
    "digital media", "video production", "animation", "streaming",
    "content creation", "podcasting", "video editing",
    # General Professional
    "management", "leadership", "communication", "teamwork",
    "problem solving", "analytical", "microsoft office", "excel",
    "powerpoint", "word", "outlook", "presentation",
}

STOP_WORDS = {
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
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now",
    "company", "name", "state", "city", "phone", "email", "address"
}

def clean_text(text: str) -> str:
    """
    Cleans raw text:
    1. Lowers case
    2. Keeps tech-centric combinations like C++, .NET, CI/CD, React.js
    3. Filters stop words
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    words = re.findall(r"\b[a-zA-Z0-9+#\.\-\/]+\b", text)
    
    cleaned_words = []
    for w in words:
        w_stripped = w.strip(".-/")
        if not w_stripped or w_stripped in STOP_WORDS:
            continue
        if len(w_stripped) == 1 and w_stripped != "c":
            continue
        cleaned_words.append(w_stripped)
    return " ".join(cleaned_words)

def clean_text_basic(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r"[^a-zA-Z0-9\s]", "", text.lower()).strip()

def extract_skills(text: str) -> set:
    text_lower = f" {str(text).lower()} "
    text_clean = re.sub(r"[^a-z0-9+#\.\-\/]", " ", text_lower)
    extracted = set()
    for skill in TECH_SKILLS:
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text_clean):
            extracted.add(skill)
    return extracted

def prepare_combined_text(cv_text: str, jd_text: str) -> str:
    """
    Cleans CV and JD and combines them with a special separator.
    """
    cv_clean = clean_text(cv_text)
    jd_clean = clean_text(jd_text)
    return f"{cv_clean} [sep] {jd_clean}"
