import os
import sys

# Add backend directory to sys path so app can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.engine import predict_match

sample_cv = "Experienced Software Engineer with proficiency in React, Node.js, and cloud deployments on AWS using Docker."
sample_jd = "Looking for a backend developer skilled in Node.js, Python, and microservices. Experience with AWS and containerization is a plus."

score = predict_match(sample_cv, sample_jd)
print(f"Match Score from backend ML engine: {score:.2f}%")
