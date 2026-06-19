import numpy as np
import pandas as pd

def explain_model_features(model, vectorizer, top_n=20):
    """
    Extracts and prints the top features influencing the model's predictions.
    Supports models with coef_ (e.g. Logistic Regression, SVC) or feature_importances_ (Random Forest).
    
    Handles hybrid feature matrices: TF-IDF feature names + handcrafted feature names.
    """
    # Get TF-IDF feature names from the main vectorizer
    tfidf_feature_names = list(vectorizer.get_feature_names_out())
    
    # Append the 3 handcrafted feature names
    handcrafted_names = ["cosine_similarity", "word_overlap_ratio", "skill_overlap_ratio"]
    feature_names = tfidf_feature_names + handcrafted_names
    
    print("\n================ Model Decision Process Explanation ================")
    
    # Check if model has coefficients (linear models like Logistic Regression or LinearSVC)
    if hasattr(model, "coef_"):
        # For binary classification, coef_[0] contains the coefficients
        coef = model.coef_[0]
        
        # Handle dimension mismatch gracefully
        if len(coef) != len(feature_names):
            print(f"  Warning: Feature count mismatch (coef: {len(coef)}, names: {len(feature_names)})")
            feature_names = [f"feature_{i}" for i in range(len(coef))]
        
        # Sort coefficients
        sorted_indices = np.argsort(coef)
        
        # Top positive features (indicate Match / Class 1)
        top_positive_indices = sorted_indices[-top_n:][::-1]
        print(f"\nTop {top_n} Keywords Driving a 'MATCH' (Positive Coefficients):")
        for i, idx in enumerate(top_positive_indices):
            print(f"  {i+1:2d}. {feature_names[idx]:25} : {coef[idx]:.4f}")
            
        # Top negative features (indicate Mismatch / Class 0)
        top_negative_indices = sorted_indices[:top_n]
        print(f"\nTop {top_n} Keywords Driving a 'MISMATCH' (Negative Coefficients):")
        for i, idx in enumerate(top_negative_indices):
            print(f"  {i+1:2d}. {feature_names[idx]:25} : {coef[idx]:.4f}")
            
        return {
            "type": "linear",
            "top_match": [(feature_names[idx], float(coef[idx])) for idx in top_positive_indices],
            "top_mismatch": [(feature_names[idx], float(coef[idx])) for idx in top_negative_indices]
        }
        
    # Check if model has feature importances (tree-based models like Random Forest)
    elif hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        
        # Handle dimension mismatch gracefully
        if len(importances) != len(feature_names):
            print(f"  Warning: Feature count mismatch (importances: {len(importances)}, names: {len(feature_names)})")
            feature_names = [f"feature_{i}" for i in range(len(importances))]
        
        sorted_indices = np.argsort(importances)[-top_n:][::-1]
        
        print(f"\nTop {top_n} Most Important Keywords (Feature Importance):")
        for i, idx in enumerate(sorted_indices):
            print(f"  {i+1:2d}. {feature_names[idx]:25} : {importances[idx]:.4f}")
            
        return {
            "type": "tree",
            "top_important": [(feature_names[idx], float(importances[idx])) for idx in sorted_indices]
        }
        
    else:
        print("Model type does not support direct feature coefficient or importance extraction.")
        return {"type": "unknown"}
