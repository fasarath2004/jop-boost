from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from scipy import sparse
import joblib
import os
from preprocessing import clean_text_basic, extract_skills

def build_features(df, max_features=10000):
    """
    Builds a HYBRID feature matrix combining:
    1. TF-IDF vectors of combined CV+JD text (with unigrams + bigrams)
    2. Cosine similarity between CV and JD TF-IDF vectors
    3. Word overlap ratio
    4. Skill overlap ratio
    
    Returns a sparse matrix and the fitted vectorizer.
    """
    print("Engineering HYBRID features (TF-IDF vectors + handcrafted features)...")
    
    # Clean texts for TF-IDF
    cv_texts_clean = df["cv_text"].apply(clean_text_basic).tolist()
    jd_texts_clean = df["job_desc"].apply(clean_text_basic).tolist()
    
    # Create combined texts for the main TF-IDF features
    combined_texts = [f"{cv} {jd}" for cv, jd in zip(cv_texts_clean, jd_texts_clean)]
    
    # Fit TF-IDF vectorizer with unigrams + bigrams for richer vocabulary
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        sublinear_tf=True,       # Apply log normalization to term frequencies
        min_df=2,                # Ignore very rare terms
        max_df=0.95,             # Ignore very common terms
    )
    X_tfidf = vectorizer.fit_transform(combined_texts)
    print(f"  TF-IDF matrix shape: {X_tfidf.shape}")
    
    # Also fit a separate vectorizer for computing cosine similarity
    # (between CV and JD individually)
    sim_vectorizer = TfidfVectorizer(max_features=5000)
    all_text = cv_texts_clean + jd_texts_clean
    sim_vectorizer.fit(all_text)
    
    cv_vecs = sim_vectorizer.transform(cv_texts_clean)
    jd_vecs = sim_vectorizer.transform(jd_texts_clean)
    
    # Compute handcrafted features in batch
    n_samples = len(df)
    handcrafted = np.zeros((n_samples, 3), dtype=np.float64)
    
    print("  Computing cosine similarity, word overlap, and skill overlap...")
    
    # 1. Cosine similarity (batch - row-wise dot products)
    # For sparse matrices, compute row-by-row cosine similarity efficiently
    for i in range(n_samples):
        handcrafted[i, 0] = cosine_similarity(cv_vecs[i], jd_vecs[i])[0][0]
    
    # 2. Word overlap + 3. Skill overlap
    for i, (_, row) in enumerate(df.iterrows()):
        cv = row["cv_text"]
        jd = row["job_desc"]
        
        cv_clean = cv_texts_clean[i]
        jd_clean = jd_texts_clean[i]
        
        # Word overlap ratio
        cv_words = set(cv_clean.split())
        jd_words = set(jd_clean.split())
        intersection = cv_words.intersection(jd_words)
        handcrafted[i, 1] = len(intersection) / len(jd_words) if len(jd_words) > 0 else 0
        
        # Skill overlap
        cv_skills = extract_skills(cv)
        jd_skills = extract_skills(jd)
        skill_intersection = cv_skills.intersection(jd_skills)
        handcrafted[i, 2] = len(skill_intersection) / len(jd_skills) if len(jd_skills) > 0 else 0
    
    # Concatenate TF-IDF sparse matrix with handcrafted dense features
    handcrafted_sparse = sparse.csr_matrix(handcrafted)
    X_features = sparse.hstack([X_tfidf, handcrafted_sparse], format="csr")
    
    print(f"  Final hybrid feature matrix shape: {X_features.shape}")
    print(f"    - TF-IDF features: {X_tfidf.shape[1]}")
    print(f"    - Handcrafted features: 3 (cosine_sim, word_overlap, skill_overlap)")
    
    # Store the sim_vectorizer inside the main vectorizer for later use
    vectorizer.sim_vectorizer_ = sim_vectorizer
    
    return X_features, vectorizer

def extract_features_for_sample(cv_text, jd_text, vectorizer):
    """
    Extracts features for a new sample using a pre-fitted vectorizer.
    If the vectorizer is the new hybrid type (has sim_vectorizer_), returns hybrid features.
    If it's the old type, returns just the 3 handcrafted features to preserve compatibility.
    """
    cv_clean = clean_text_basic(cv_text)
    jd_clean = clean_text_basic(jd_text)
    
    # Check if this is the new hybrid vectorizer
    is_hybrid = hasattr(vectorizer, "sim_vectorizer_")
    
    if is_hybrid:
        # 1. TF-IDF features from combined text
        combined = f"{cv_clean} {jd_clean}"
        X_tfidf = vectorizer.transform([combined])
        
        # 2. Cosine similarity using the similarity sub-vectorizer
        sim_vectorizer = vectorizer.sim_vectorizer_
        cv_vec = sim_vectorizer.transform([cv_clean])
        jd_vec = sim_vectorizer.transform([jd_clean])
        cos_sim = cosine_similarity(cv_vec, jd_vec)[0][0]
    else:
        # Old behavior: compute cosine sim using the main vectorizer
        cv_vec = vectorizer.transform([cv_clean])
        jd_vec = vectorizer.transform([jd_clean])
        cos_sim = cosine_similarity(cv_vec, jd_vec)[0][0]
    
    # 3. Word overlap ratio
    cv_words = set(cv_clean.split())
    jd_words = set(jd_clean.split())
    intersection = cv_words.intersection(jd_words)
    word_overlap = len(intersection) / len(jd_words) if len(jd_words) > 0 else 0
    
    # 4. Skill overlap ratio
    cv_skills = extract_skills(cv_text)
    jd_skills = extract_skills(jd_text)
    skill_intersection = cv_skills.intersection(jd_skills)
    skill_overlap_ratio = len(skill_intersection) / len(jd_skills) if len(jd_skills) > 0 else 0
    
    if is_hybrid:
        # Combine into sparse format matching new training
        handcrafted = sparse.csr_matrix([[cos_sim, word_overlap, skill_overlap_ratio]])
        X_features = sparse.hstack([X_tfidf, handcrafted], format="csr")
        return X_features
    else:
        # Return old format: just the 3 features in a numpy array
        return np.array([[cos_sim, word_overlap, skill_overlap_ratio]])

def save_vectorizer(vectorizer, path: str):
    """
    Saves the TF-IDF vectorizer object to disk.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(vectorizer, path)
    print(f"Saved vectorizer to {path}")

def load_vectorizer(path: str):
    """
    Loads the TF-IDF vectorizer object from disk.
    """
    return joblib.load(path)
