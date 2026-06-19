import os
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

def get_metrics(y_true, y_pred):
    """
    Computes classification evaluation metrics.
    """
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    return {
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    }

def print_metrics(metrics, report=None):
    """
    Displays the computed metrics.
    """
    print("\n================ Evaluation Metrics ================")
    for key, value in metrics.items():
        print(f"{key:12}: {value:.4f} ({value*100:.2f}%)")
    print("====================================================")
    if report:
        print("\nClassification Report:\n", report)

def generate_and_save_confusion_matrix(y_true, y_pred, output_dir: str):
    """
    Computes, prints, and plots the confusion matrix, saving it as a PNG file.
    """
    cm = confusion_matrix(y_true, y_pred)
    print("\nConfusion Matrix (Raw):")
    print(cm)
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "confusion_matrix.png")
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.figure(figsize=(6, 5))
        sns.heatmap(
            cm, 
            annot=True, 
            fmt="d", 
            cmap="Blues", 
            xticklabels=["Mismatch (0)", "Match (1)"],
            yticklabels=["Mismatch (0)", "Match (1)"]
        )
        plt.title("Confusion Matrix - Resume Match Model")
        plt.ylabel("Actual Labels")
        plt.xlabel("Predicted Labels")
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"Saved confusion matrix plot to: {output_path}")
    except Exception as e:
        print(f"Failed to generate confusion matrix plot image: {e}")
        print("Note: Plot generation requires matplotlib and seaborn.")
        
    return cm
