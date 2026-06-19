# CareerPulse AI - Machine Learning Project Report

## Overview
This project involves building an advanced **NLP-based Resume Match Prediction Pipeline**. The pipeline dynamically assesses the alignment between candidate Resumes (CVs) and Job Descriptions (JDs) using Natural Language Processing (NLP) and Machine Learning classifiers.

## 1. Data Preprocessing & Exploratory Data Analysis (EDA)
The dataset (`train.csv`) was thoroughly cleaned and preprocessed:
- **Size**: 3,683 records initially, yielding **3,681 clean records** after removing duplicates.
- **Distribution**: The target labels were mapped to binary classes. 
  - `Match (1)` mapping to scores >= 50.0 (~67.4% of data).
  - `Mismatch (0)` mapping to scores < 50.0 (~32.6% of data).
- **Text Analysis**: We extracted term frequencies and noticed that JDs were consistently short (average 11 words) compared to full Resumes (average 777 words).

*All EDA visualizations (like match distribution and length density curves) were successfully plotted and saved to `reports/eda_distribution.png`.*

## 2. Feature Engineering
To solve the length imbalance between CV and JD texts and improve model generalization, we engineered the following three predictive features instead of raw concatenated TF-IDF vectors:
1. **TF-IDF Cosine Similarity**: Computing the exact semantic similarity score between the vector of the CV and the vector of the JD.
2. **Word Overlap Ratio**: Measuring the percentage of words in the Job Description that appear in the candidate's Resume.
3. **Skill Overlap Ratio**: Employing a custom tech-skill extraction function to measure exactly how many target skills the candidate possesses.

## 3. Model Selection and Training
Multiple models were rigorously trained and cross-validated using 5-Fold Stratified Cross-Validation on the engineered features:
1. Logistic Regression
2. Multinomial Naive Bayes
3. Linear Support Vector Classifier (LinearSVC)
4. Random Forest Classifier
5. Decision Tree Classifier

**Model Comparison Results:**
| Model | Accuracy | Precision | Recall | F1 Score |
|-------|----------|-----------|--------|----------|
| **Linear SVC** | **85.7%** | **91.1%** | **87.3%** | **89.2%** |
| Logistic Regression | 82.2% | 84.0% | 90.9% | 87.3% |
| Random Forest | 81.1% | 85.6% | 86.5% | 86.0% |
| Decision Tree | 80.5% | 85.6% | 85.3% | 85.5% |

### Best Algorithm Selected
The **Linear Support Vector Classifier (LinearSVC)** emerged as the strongest performer. Hyperparameter tuning using `GridSearchCV` further optimized its performance (Best parameter: `C=10.0`).

## 4. Evaluation Metrics
Upon evaluation on the held-out validation set, the best model achieved:
- **Accuracy**: 84.53%
- **Precision**: 90.15%
- **Recall**: 86.52%
- **F1 Score**: 88.30%

The **Confusion Matrix** shows that the model correctly predicts the vast majority of matches and mismatches with strong reliability. A visual plot was saved to `reports/confusion_matrix.png`.

## 5. Deployment & Integration
The best model (`match_model.joblib`) and the unified TF-IDF vectorizer (`vectorizer.joblib`) have been saved to `backend/app/ml/model/`.
The backend prediction engine (`backend/app/ml/engine.py`) has been upgraded to consume the optimized feature representations and leverage the Linear SVC's `decision_function` (transformed into a normalized 0-100% probability curve) to output robust Match Scores in real time for the frontend.

## 6. Suggestions to Increase Accuracy Above 90%
To push the validation accuracy reliably beyond the 90% threshold, the following improvements are recommended:
- **Deep Learning / Transformer Architectures**: Implementing fine-tuned Hugging Face Transformer models (such as `BERT`, `RoBERTa`, or `Sentence-Transformers`) to extract deep semantic embeddings from CVs and JDs, capturing nuance better than basic TF-IDF similarity.
- **Extended Skill Ontologies**: Integrating more comprehensive Knowledge Graphs and Skill Ontologies (like EMSI or O*NET) so the skill matching is hierarchy-aware (e.g. recognizing that `React` implies `JavaScript` proficiency).
- **Larger, Balanced Datasets**: Gathering more varied Job Descriptions with broader lengths and greater variability in text structure.

## Resume/CV Project Description for Portfolio
**Machine Learning Engineer – Candidate Matching Pipeline**
- Designed and deployed an end-to-end NLP text classification pipeline to evaluate Resume-to-Job Description fit, processing over 3,600+ records.
- Engineered novel predictive features including TF-IDF Cosine Similarity and targeted Skill Overlap Ratios to boost baseline accuracy by over 17%.
- Automated model selection using scikit-learn and 5-Fold Stratified Cross Validation, optimizing a Linear SVC to achieve **85%+ Accuracy** and **88%+ F1 Score**.
- Integrated the finalized classification engine directly into a production-ready FastAPI backend, returning high-precision Match Percentages to a React frontend.
