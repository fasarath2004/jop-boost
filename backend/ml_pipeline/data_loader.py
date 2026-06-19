import os
import pandas as pd
import numpy as np

def load_and_clean_data(file_path: str):
    """
    Loads dataset from CSV, removes missing values and duplicates, 
    and converts match_score into binary class labels.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at: {file_path}")
    
    # Load dataset
    df = pd.read_csv(file_path)
    print(f"Loaded dataset with {len(df)} rows.")
    
    # Identify missing values
    missing_before = df.isnull().sum().sum()
    if missing_before > 0:
        print(f"Found {missing_before} missing values. Dropping rows with missing values.")
        df = df.dropna(subset=["cv_text", "job_desc", "match_score"])
        
    # Remove duplicates
    duplicates_count = df.duplicated(subset=["cv_text", "job_desc"]).sum()
    if duplicates_count > 0:
        print(f"Found {duplicates_count} duplicate rows. Removing duplicates.")
        df = df.drop_duplicates(subset=["cv_text", "job_desc"])
        
    print(f"Dataset shape after cleaning: {df.shape}")
    
    # Create binary labels: match_score >= 50.0 is Match (1), else Mismatch (0)
    # Target value distribution in train.csv is: 90.0 and 20.0, so this threshold is ideal.
    df["label"] = (df["match_score"] >= 50.0).astype(int)
    
    return df
