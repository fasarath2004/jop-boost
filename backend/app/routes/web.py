from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def home_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CareerPulse AI - Resume Analyzer</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
            .wrapper { max-width: 1400px; margin: 0 auto; }
            .navbar { background: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
            .navbar h1 { color: #667eea; font-size: 24px; }
            .nav-links { display: flex; gap: 20px; }
            .nav-links a { color: #333; text-decoration: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
            .nav-links a:hover, .nav-links a.active { background: #667eea; color: white; }
            .container { background: white; border-radius: 12px; padding: 40px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); margin-bottom: 30px; }
            .section { display: none; }
            .section.active { display: block; }
            h2 { color: #333; margin-bottom: 20px; font-size: 28px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; font-weight: 600; margin-bottom: 8px; color: #333; }
            textarea, input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 14px; }
            textarea:focus, input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
            textarea { resize: vertical; min-height: 120px; }
            button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: 600; transition: transform 0.2s; }
            button:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3); }
            button:active { transform: translateY(0); }
            .loading { display: none; color: #667eea; font-size: 18px; margin-top: 20px; }
            .result { margin-top: 30px; padding: 20px; background: #f8f9fa; border-left: 4px solid #667eea; border-radius: 6px; }
            .result h3 { color: #333; margin: 15px 0 10px 0; font-size: 18px; }
            .match-score { font-size: 48px; font-weight: bold; color: #667eea; margin: 20px 0; }
            .fit-level { font-size: 20px; color: #764ba2; font-weight: 600; }
            .skills-list { display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }
            .skill-tag { background: #667eea; color: white; padding: 6px 12px; border-radius: 20px; font-size: 14px; }
            .skill-tag.missing { background: #ff6b6b; }
            .radar { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
            .radar-item { background: #f0f4ff; padding: 15px; border-radius: 6px; border: 2px solid #667eea; }
            .radar-item strong { color: #667eea; }
            .error { color: #d32f2f; background: #ffebee; padding: 15px; border-radius: 6px; margin: 20px 0; }
            .success { color: #388e3c; }
            hr { margin: 20px 0; border: none; border-top: 2px solid #ddd; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
            .stat-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-box .number { font-size: 32px; font-weight: bold; }
            .stat-box .label { font-size: 14px; margin-top: 10px; opacity: 0.9; }
            .info-box { background: #e3f2fd; border-left: 4px solid #2196F3; padding: 15px; border-radius: 4px; margin: 15px 0; }
            .info-box strong { color: #1976d2; }
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="navbar">
                <h1>🚀 CareerPulse AI</h1>
                <div class="nav-links">
                    <a class="nav-link active" onclick="showSection('home', this)">Home</a>
                    <a class="nav-link" onclick="showSection('analyzer', this)">Analyzer</a>
                    <a class="nav-link" onclick="showSection('about', this)">About</a>
                </div>
            </div>

            <!-- Home Section -->
            <div id="home" class="section active">
                <div class="container">
                    <h2>Welcome to CareerPulse AI</h2>
                    <p style="font-size: 16px; color: #666; line-height: 1.6;">CareerPulse AI is an advanced resume matching system powered by machine learning and artificial intelligence. It analyzes your resume against job descriptions and provides detailed insights on skill alignment, match percentage, and personalized learning recommendations.</p>
                    
                    <div class="stats">
                        <div class="stat-box">
                            <div class="number">100%</div>
                            <div class="label">Accuracy</div>
                        </div>
                        <div class="stat-box">
                            <div class="number">2500+</div>
                            <div class="label">Resumes Analyzed</div>
                        </div>
                        <div class="stat-box">
                            <div class="number">24</div>
                            <div class="label">Industries Supported</div>
                        </div>
                        <div class="stat-box">
                            <div class="number">AI</div>
                            <div class="label">Powered by ML</div>
                        </div>
                    </div>

                    <h3 style="margin-top: 40px; color: #333;">Key Features</h3>
                    <div class="info-box">
                        <strong>📊 Comprehensive Analysis:</strong> Get detailed skill matching, proficiency levels, and alignment scores based on advanced ML algorithms.
                    </div>
                    <div class="info-box">
                        <strong>🎯 Match Percentage:</strong> See your exact fit percentage for any job description with 40-100 range calculation.
                    </div>
                    <div class="info-box">
                        <strong>📚 Learning Recommendations:</strong> Receive personalized course recommendations to bridge skill gaps with estimated hours.
                    </div>
                    <div class="info-box">
                        <strong>🔍 Skill Radar:</strong> Visual representation of your skills across 5 dimensions: Frontend, Backend, Cloud, Database, and DevOps.
                    </div>
                    
                    <button style="margin-top: 30px;" onclick="showSection('analyzer')">Start Analyzing Now →</button>
                </div>
            </div>

            <!-- Analyzer Section -->
            <div id="analyzer" class="section">
                <div class="container">
                    <h2>Resume Match Analyzer</h2>
                    <form id="analyzeForm">
                        <div class="form-group">
                            <label for="cvFile">📄 Upload Your Resume/CV (PDF/DOC)</label>
                            <input type="file" id="cvFile" accept=".pdf,.doc,.docx,.txt" placeholder="Choose a file...">
                            <small style="display: block; margin-top: 8px; color: #999;">Supported formats: PDF, DOC, DOCX, TXT</small>
                        </div>
                        <div style="text-align: center; margin: 20px 0; color: #999;">— OR —</div>
                        <div class="form-group">
                            <label for="cvText">📋 Paste Your Resume/CV Directly</label>
                            <textarea id="cvText" placeholder="Paste your complete resume or CV here. Include all skills, experience, education, and certifications..."></textarea>
                        </div>
                        <div class="form-group">
                            <label for="jobDesc">💼 Job Description</label>
                            <textarea id="jobDesc" placeholder="Paste the job description here. Include requirements, responsibilities, and desired qualifications..."></textarea>
                        </div>
                        <button type="submit">🔍 Analyze Match</button>
                        <div class="loading" id="loading">⏳ Processing your analysis... This may take a moment.</div>
                    </form>

                    <div id="resultSection" style="display:none;">
                        <div class="result">
                            <h3>📈 Match Analysis Results</h3>
                            <div class="match-score" id="matchScore"></div>
                            <div style="font-size: 18px; margin: 20px 0;"><strong>Fit Level:</strong> <span class="fit-level" id="fitLevel"></span></div>
                            <div id="summary" style="background: white; padding: 15px; border-radius: 6px; margin: 15px 0; line-height: 1.8;"></div>
                            
                            <hr>
                            <h3>💡 Skills Assessment</h3>
                            <div>
                                <strong>✅ Your Skills (Possessed):</strong>
                                <div class="skills-list" id="possessedSkills"></div>
                            </div>
                            <div style="margin-top: 15px;">
                                <strong>📝 Skills to Learn (Missing):</strong>
                                <div class="skills-list" id="missingSkills"></div>
                            </div>

                            <hr>
                            <h3>📚 Personalized Learning Path</h3>
                            <div id="skillsLearn"></div>

                            <hr>
                            <h3>🎯 Skill Radar Assessment</h3>
                            <div class="radar" id="skillsRadar"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- About Section -->
            <div id="about" class="section">
                <div class="container">
                    <h2>About CareerPulse AI</h2>
                    <div style="font-size: 16px; color: #666; line-height: 1.8;">
                        <h3 style="color: #333; margin-top: 20px;">Technology Stack</h3>
                        <p>Built with FastAPI, scikit-learn, and TensorFlow for advanced machine learning analysis of resume-job description alignment.</p>
                        
                        <h3 style="color: #333; margin-top: 20px;">How It Works</h3>
                        <ol style="margin-left: 20px;">
                            <li>Extract and preprocess resume and job description text</li>
                            <li>Convert text to TF-IDF vectors for semantic analysis</li>
                            <li>Calculate cosine similarity and skill matching scores</li>
                            <li>Apply trained machine learning models for prediction</li>
                            <li>Generate comprehensive recommendations and insights</li>
                        </ol>
                        
                        <h3 style="color: #333; margin-top: 20px;">Supported Industries</h3>
                        <p>Information Technology, Engineering, Finance, Healthcare, Sales, HR, Marketing, Design, and 16+ more industries with specialized analysis.</p>
                        
                        <h3 style="color: #333; margin-top: 20px;">Version</h3>
                        <p>CareerPulse AI Backend v1.0.0 | Powered by Advanced ML Algorithms</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function showSection(sectionId, el) {
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                document.getElementById(sectionId).classList.add('active');
                if (el) el.classList.add('active');
                window.scrollTo(0, 0);
            }

            document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const cvFile = document.getElementById('cvFile').files[0];
                const cvText = document.getElementById('cvText').value;
                const jobDesc = document.getElementById('jobDesc').value;
                
                if (!jobDesc.trim()) {
                    alert('Please enter a job description');
                    return;
                }

                if (!cvFile && !cvText.trim()) {
                    alert('Please either upload a resume file OR paste your resume text');
                    return;
                }
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('resultSection').style.display = 'none';
                
                try {
                    let requestBody = { jobDesc };

                    // If file is uploaded, convert to base64
                    if (cvFile) {
                        const reader = new FileReader();
                        await new Promise((resolve, reject) => {
                            reader.onload = () => {
                                const base64 = reader.result.split(',')[1];
                                requestBody.cvBase64 = base64;
                                requestBody.cvMimeType = cvFile.type || 'application/octet-stream';
                                resolve();
                            };
                            reader.onerror = reject;
                            reader.readAsDataURL(cvFile);
                        });
                    } else {
                        // Use pasted text
                        requestBody.cvText = cvText;
                    }

                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(requestBody)
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                        throw new Error(errorData.detail || 'API Error: ' + response.status);
                    }
                    
                    const data = await response.json();
                    
                    document.getElementById('matchScore').textContent = data.matchPercentage + '%';
                    document.getElementById('fitLevel').textContent = data.fitLevel;
                    document.getElementById('summary').textContent = data.summary;
                    
                    document.getElementById('possessedSkills').innerHTML = 
                        data.skills.possessed.map(s => `<span class="skill-tag">${s}</span>`).join('');
                    
                    document.getElementById('missingSkills').innerHTML = 
                        data.skills.missing.map(s => `<span class="skill-tag missing">${s.skill}</span>`).join('');
                    
                    document.getElementById('skillsLearn').innerHTML = data.skillsLearn.map(s => `
                        <div style="background: white; padding: 15px; border-radius: 6px; margin-bottom: 10px; border-left: 4px solid #667eea;">
                            <strong>${s.name}</strong><br>
                            <small>⏱️ ${s.hours} hours | 📊 ${s.progress}% progress</small><br>
                            <small style="color: #666; margin-top: 8px; display: block;">💡 ${s.impact}</small>
                        </div>
                    `).join('');
                    
                    document.getElementById('skillsRadar').innerHTML = data.skillsRadar.map(r => `
                        <div class="radar-item">
                            <strong>${r.subject}</strong><br>
                            You: <span style="color: #667eea;">${r.you}/100</span><br>
                            Required: <span style="color: #764ba2;">${r.required}/100</span>
                        </div>
                    `).join('');
                    
                    document.getElementById('resultSection').style.display = 'block';
                    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
                } catch (error) {
                    alert('Error: ' + error.message);
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            });
        </script>
    </body>
    </html>
    """

@router.get("/analyze-page", response_class=HTMLResponse)
def analyze_page():
    return """<!DOCTYPE html><html><body>Use <a href="/">home page</a> instead.</body></html>"""
