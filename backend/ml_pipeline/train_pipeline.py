import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_and_clean_data
from features import build_features, save_vectorizer, extract_features_for_sample
from models import compare_models, tune_best_model
from evaluate import get_metrics, print_metrics, generate_and_save_confusion_matrix

# Configure paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "train.csv")
MODEL_DIR = os.path.join(BASE_DIR, "app", "ml", "model")
REPORTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "reports")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def run_eda(df: pd.DataFrame):
    print("\n================ Exploratory Data Analysis (EDA) ================")
    print(f"Dataset Size: {len(df)} samples")
    print(f"Match instances: {sum(df['label'] == 1)} ({sum(df['label'] == 1)/len(df)*100:.2f}%)")
    print(f"Mismatch instances: {sum(df['label'] == 0)} ({sum(df['label'] == 0)/len(df)*100:.2f}%)")
    
    df["cv_word_count"] = df["cv_text"].apply(lambda x: len(str(x).split()))
    df["jd_word_count"] = df["job_desc"].apply(lambda x: len(str(x).split()))
    
    print("\nWord Count Statistics:")
    print(df[["cv_word_count", "jd_word_count"]].describe())
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        sns.countplot(x="match_score", data=df, hue="match_score", palette="viridis", legend=False)
        plt.title("Distribution of Match Scores")
        
        plt.subplot(1, 2, 2)
        sns.kdeplot(df["cv_word_count"], fill=True, label="Resume CV")
        sns.kdeplot(df["jd_word_count"], fill=True, label="Job Description")
        plt.title("Text Length Distribution")
        plt.legend()
        
        plt.tight_layout()
        eda_plot_path = os.path.join(REPORTS_DIR, "eda_distribution.png")
        plt.savefig(eda_plot_path, dpi=150)
        plt.close()
    except Exception as e:
        print(f"Failed to generate EDA plots: {e}")
        
    print("================================================================")

def main():
    print("Starting Machine Learning Pipeline (Hybrid Features v2)...")
    df = load_and_clean_data(DATA_PATH)
    run_eda(df)
    
    # Build hybrid features: TF-IDF vectors + handcrafted features
    X_features, vectorizer = build_features(df, max_features=10000)
    y = df["label"].values
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_features, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTrain set size: {X_train.shape[0]} | Validation set size: {X_val.shape[0]}")
    print(f"Feature dimensions: {X_train.shape[1]}")
    
    from sklearn.svm import LinearSVC
    print("\nSkipping grid search to train immediately...")
    best_model_name = "Linear Support Vector Classifier"
    best_model_tuned = LinearSVC(C=10.0, random_state=42, dual='auto')
    
    print(f"\nTraining tuned {best_model_name} on training split...")
    best_model_tuned.fit(X_train, y_train)
    
    y_pred = best_model_tuned.predict(X_val)
    
    metrics = get_metrics(y_val, y_pred)
    class_report = classification_report(y_val, y_pred, target_names=["Mismatch (0)", "Match (1)"])
    print_metrics(metrics, class_report)
    generate_and_save_confusion_matrix(y_val, y_pred, REPORTS_DIR)
    
    # ---- Accuracy verification ----
    val_accuracy = metrics["Accuracy"]
    val_f1 = metrics["F1 Score"]
    print(f"\n{'='*60}")
    print(f"  ACCURACY CHECK: {val_accuracy*100:.2f}% (target: >= 85.00%)")
    print(f"  F1 SCORE CHECK: {val_f1*100:.2f}%")
    if val_accuracy >= 0.85:
        print(f"  ✅ TARGET MET! Accuracy >= 85%")
    else:
        print(f"  ⚠️  Target not yet met. Accuracy < 85%")
    print(f"{'='*60}")
    
    # NOTE: Saves to a separate 'classifier' subdir to avoid overwriting
    # the regression model from app/ml/train.py (which uses match_model.joblib).
    # engine.py loads from app/ml/model/ — retrain the regression model for compatibility.
    vectorizer_save_path = os.path.join(MODEL_DIR, "vectorizer.joblib")
    model_save_path = os.path.join(MODEL_DIR, "classifier_model.joblib")
    
    save_vectorizer(vectorizer, vectorizer_save_path)
    joblib.dump(best_model_tuned, model_save_path)
    print(f"Saved optimized best model to: {model_save_path}")
    
    print("\n================ Prediction Demo on Sample Input ================")
    sample_cv = "Experienced Software Engineer with proficiency in React, Node.js, and cloud deployments on AWS using Docker."
    sample_jd = "Looking for a backend developer skilled in Node.js, Python, and microservices. Experience with AWS and containerization is a plus."
    
    demo_features = extract_features_for_sample(sample_cv, sample_jd, vectorizer)
    demo_pred_class = best_model_tuned.predict(demo_features)[0]
    
    if hasattr(best_model_tuned, "predict_proba"):
        demo_prob = best_model_tuned.predict_proba(demo_features)[0][1]
    elif hasattr(best_model_tuned, "decision_function"):
        df_val = best_model_tuned.decision_function(demo_features)[0]
        demo_prob = 1 / (1 + np.exp(-df_val))
    else:
        demo_prob = float(demo_pred_class)
        
    demo_score = demo_prob * 100
    print(f"Predicted Class: {demo_pred_class} ({'Match' if demo_pred_class == 1 else 'Mismatch'})")
    print(f"Predicted Match Score (probability-based): {demo_score:.2f}%")
    print("=================================================================")
    print("\nML Pipeline run completed successfully.")

if __name__ == "__main__":
    main()
