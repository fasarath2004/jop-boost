from sklearn.model_selection import StratifiedKFold, cross_validate, GridSearchCV
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import numpy as np

def get_candidate_models():
    """
    Returns a dictionary of classification models to evaluate.
    Restricting to fast linear models that work well with large sparse TF-IDF features.
    """
    return {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
        "SGD Classifier": SGDClassifier(random_state=42, loss="modified_huber", max_iter=1000),
        "Linear Support Vector Classifier": LinearSVC(random_state=42, dual='auto', max_iter=2000)
    }

def compare_models(X, y):
    """
    Evaluates candidate models using Stratified K-Fold Cross Validation.
    Returns a comparison DataFrame.
    """
    models = get_candidate_models()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    scoring = ['accuracy', 'precision', 'recall', 'f1']
    results = []
    
    print("\n--- Evaluating Models with 5-Fold Stratified CV ---")
    for name, model in models.items():
        print(f"Running CV for {name}...")
        scores = cross_validate(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
        
        results.append({
            "Model": name,
            "Accuracy": np.mean(scores['test_accuracy']),
            "Precision": np.mean(scores['test_precision']),
            "Recall": np.mean(scores['test_recall']),
            "F1 Score": np.mean(scores['test_f1']),
            "Fit Time (s)": np.mean(scores['fit_time'])
        })
        
    df_results = pd.DataFrame(results).sort_values(by="F1 Score", ascending=False)
    return df_results

def get_hyperparameter_grids():
    """
    Returns hyperparameter grids for tuning the candidate models.
    """
    return {
        "Logistic Regression": {
            "C": [0.1, 0.5, 1.0, 5.0, 10.0, 50.0],
            "solver": ["liblinear", "lbfgs"]
        },
        "SGD Classifier": {
            "alpha": [1e-5, 1e-4, 1e-3, 1e-2],
            "loss": ["modified_huber", "log_loss"],
            "penalty": ["l2", "l1", "elasticnet"]
        },
        "Linear Support Vector Classifier": {
            "C": [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]
        },
        "Random Forest Classifier": {
            "n_estimators": [100, 200, 300],
            "max_depth": [10, 20, 30, None],
            "min_samples_split": [2, 5]
        },
        "Gradient Boosting": {
            "n_estimators": [100, 200, 300],
            "max_depth": [3, 5, 7],
            "learning_rate": [0.05, 0.1, 0.2],
            "subsample": [0.8, 1.0]
        },
        "Decision Tree Classifier": {
            "max_depth": [10, 20, 30, None],
            "min_samples_split": [2, 5, 10]
        }
    }

def tune_best_model(model_name, X, y):
    """
    Performs grid search to optimize hyperparameters of the selected best model.
    """
    print(f"\n--- Hyperparameter Tuning for {model_name} ---")
    models = get_candidate_models()
    grids = get_hyperparameter_grids()
    
    base_model = models[model_name]
    grid = grids[model_name]
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=grid,
        scoring="f1",
        cv=cv,
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X, y)
    print(f"Best Hyperparameters: {grid_search.best_params_}")
    print(f"Best CV F1 Score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_, grid_search.best_params_
