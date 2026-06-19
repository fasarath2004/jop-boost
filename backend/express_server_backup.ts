import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = 3000;

// Set up body parsers to handle base64 PDF/Word uploads up to 12MB safely
app.use(express.json({ limit: "12mb" }));
app.use(express.urlencoded({ limit: "12mb", extended: true }));

// Lazy initializer for Google Gen AI client
let aiClient: GoogleGenAI | null = null;
function getGenAI(): GoogleGenAI | null {
  if (!aiClient) {
    const key = process.env.GEMINI_API_KEY;
    if (key && key !== "MY_GEMINI_API_KEY" && key.trim() !== "") {
      aiClient = new GoogleGenAI({
        apiKey: key,
        httpOptions: {
          headers: {
            "User-Agent": "aistudio-build",
          },
        },
      });
    }
  }
  return aiClient;
}

// Simulated fallback data generator when API key is missing or on request failure
function generateMockResponse(cvContent: string, jobDesc: string): any {
  // Extract simple keywords from inputs to make mock extremely tailored and smart
  const combined = `${cvContent} ${jobDesc}`.toLowerCase();
  
  const potentialSkills = [
    { name: "React.js", search: "react" },
    { name: "Node.js", search: "node" },
    { name: "TypeScript", search: "typescript" },
    { name: "GraphQL", search: "graphql" },
    { name: "AWS (EC2/S3)", search: "aws" },
    { name: "Docker", search: "docker" },
    { name: "Python", search: "python" },
    { name: "Kubernetes", search: "kubernetes" },
    { name: "Agile / Scrum", search: "agile" },
    { name: "Tailwind CSS", search: "tailwind" },
    { name: "CI/CD Pipelines", search: "ci/cd" },
    { name: "REST APIs", search: "rest" },
    { name: "SQL / PostgreSQL", search: "sql" },
    { name: "NoSQL / MongoDB", search: "nosql" },
    { name: "System Design", search: "system design" },
    { name: "Leadership", search: "leader" }
  ];

  const processedPossessed: string[] = [];
  const processedMissing: Array<{ skill: string; priority: "Priority 1" | "Nice to have" }> = [];

  // Categorize based on content match
  potentialSkills.forEach(item => {
    const isMentionedInCV = cvContent.toLowerCase().includes(item.search);
    const isMentionedInJD = jobDesc.toLowerCase().includes(item.search);

    if (isMentionedInJD) {
      if (isMentionedInCV || (cvContent.length < 50 && Math.random() > 0.4)) {
        processedPossessed.push(item.name);
      } else {
        processedMissing.push({
          skill: item.name,
          priority: Math.random() > 0.5 ? "Priority 1" : "Nice to have"
        });
      }
    }
  });

  // Guarantee at least some data if inputs are sparse
  if (processedPossessed.length === 0) {
    processedPossessed.push("React.js", "Node.js", "Agile / Scrum");
  }
  if (processedMissing.length === 0) {
    processedMissing.push(
      { skill: "GraphQL", priority: "Priority 1" },
      { skill: "AWS (EC2/S3)", priority: "Priority 1" },
      { skill: "Docker", priority: "Nice to have" }
    );
  }

  // Create learning recommendations based on missing skills
  const skillsLearn = processedMissing.map((missing, idx) => {
    const hours = (idx + 1) * 5 + 5;
    const progress = Math.floor(Math.random() * 60);
    return {
      name: `${missing.skill} Fundamentals`,
      progress,
      impact: missing.priority === "Priority 1" 
        ? `High impact for this role. Est. ${hours} hours.` 
        : `Recommended addition. Est. ${hours} hours.`,
      hours
    };
  });

  // Ensure learning recommendations has elements
  if (skillsLearn.length === 0) {
    skillsLearn.push({
      name: "System Design Core Essentials",
      progress: 30,
      impact: "High impact for this role. Est. 12 hours.",
      hours: 12
    });
  }

  // Radar categories mapping
  const subjects = ["React", "Python", "Cloud", "Leadership", "Node.js", "TypeScript"];
  const skillsRadar = subjects.map(subject => {
    const isPossessed = processedPossessed.some(s => s.toLowerCase().includes(subject.toLowerCase()));
    const req = 75 + Math.floor(Math.random() * 20); // 75-95
    const you = isPossessed 
      ? req - Math.floor(Math.random() * 15) // Close gap
      : Math.max(20, req - 30 - Math.floor(Math.random() * 30)); // Large gap
    return { subject, required: req, you };
  });

  // Calculate Match Score
  const matchRatio = processedPossessed.length / (processedPossessed.length + processedMissing.length);
  const matchPercentage = Math.min(98, Math.max(45, Math.round(matchRatio * 100)));
  
  let fitLevel: "Strong Fit" | "Moderate Fit" | "Development Needed" = "Moderate Fit";
  if (matchPercentage >= 80) fitLevel = "Strong Fit";
  else if (matchPercentage < 60) fitLevel = "Development Needed";

  return {
    matchPercentage,
    fitLevel,
    summary: `Based on an automated ATS assessment of your qualifications against this target profile, your alignment is evaluated at ${matchPercentage}%. You present robust credentials in ${processedPossessed.slice(0, 3).join(", ")}, which align closely with primary stack prerequisites. However, addressing knowledge gaps in key target aspects—specifically ${processedMissing.slice(0, 2).map(m => m.skill).join(" and ")}—will significantly bolster tracking score compliance to bypass ATS constraints.`,
    skills: {
      possessed: processedPossessed,
      missing: processedMissing
    },
    skillsLearn,
    skillsRadar
  };
}

// 1. Analyze Resume and Job Description
app.post("/api/analyze", async (req, res) => {
  try {
    const { cvText, cvBase64, cvMimeType, jobDesc } = req.body;

    if (!jobDesc || jobDesc.trim() === "") {
      return res.status(400).json({ error: "Job description is required." });
    }

    const ai = getGenAI();
    if (!ai) {
      console.log("No GEMINI_API_KEY found or invalid. Falling back to robust simulated AI parser.");
      const fallback = generateMockResponse(cvText || "Applicant Resume Content", jobDesc);
      return res.json({ ...fallback, isMock: true });
    }

    console.log("Starting real Gemini API Career Analysis...");
    
    // Construct request parts
    const contents: any[] = [];
    
    // Add CV as file part (if base64 PDF is provided) or standard text
    if (cvBase64 && cvMimeType) {
      contents.push({
        inlineData: {
          mimeType: cvMimeType,
          data: cvBase64.replace(/^data:.*,/, ""), // Strip metadata if present
        }
      });
      contents.push({
        text: `The above file is the applicant's resume. Target job description below:\n\n${jobDesc}`
      });
    } else {
      contents.push({
        text: `Applicant Resume / CV Content:\n${cvText || "No resume content provided. Assume standard starter credentials to fill in gaps."}\n\nTarget Job Description:\n${jobDesc}`
      });
    }

    const systemInstruction = 
      "You are CareerPulse AI, an advanced applicant tracking system (ATS) expert, tech recruiter, and professional career advisor. " +
      "Your objective is to conduct a meticulous fit analysis comparing the provided Candidate Resume to the Target Job Description. " +
      "Assess competencies, technical stacks, methodologies, soft skills, and experiences. " +
      "Determine a matching score (40 to 100), identify possessed skills, list missing skills labeled by tracking priority ('Priority 1' or 'Nice to have'), " +
      "give customized suggestions for learning modules to build to fill these gaps, and score 5-6 core categories (like React, Python, Cloud, Leadership, Node.js, etc.) " +
      "comparing the required weight against the applicant's level. Return your results exclusively in JSON matching the requested schema. Maintain logical consistency.";

    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: contents,
      config: {
        systemInstruction,
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            matchPercentage: { 
              type: Type.INTEGER, 
              description: "ATS alignment fit percentage from 0 to 100" 
            },
            fitLevel: { 
              type: Type.STRING, 
              description: "Must be 'Strong Fit' (80+), 'Moderate Fit' (60-79), or 'Development Needed' (<60)" 
            },
            summary: { 
              type: Type.STRING, 
              description: "A concise, professional 3-4 sentence analysis summarizing strengths, primary gaps, and recommendation focus." 
            },
            skills: {
              type: Type.OBJECT,
              properties: {
                possessed: {
                  type: Type.ARRAY,
                  items: { type: Type.STRING },
                  description: "Skills mentioned in both Resume and Job Description, or high confidence matches."
                },
                missing: {
                  type: Type.ARRAY,
                  items: {
                    type: Type.OBJECT,
                    properties: {
                      skill: { type: Type.STRING },
                      priority: { 
                        type: Type.STRING, 
                        description: "Must be 'Priority 1' (for critical, missing keywords in Job Description) or 'Nice to have'" 
                      }
                    },
                    required: ["skill", "priority"]
                  },
                  description: "Crucial keywords or tools requested by the job description that are missing from the resume."
                }
              },
              required: ["possessed", "missing"]
            },
            skillsLearn: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  name: { type: Type.STRING, description: "Short course name or subject title to fill the gap (e.g. 'GraphQL Fundamentals')" },
                  progress: { type: Type.INTEGER, description: "Estimate of candidate's current familiarity progress percentage from 0 to 80" },
                  impact: { type: Type.STRING, description: "Impact explanation (e.g. 'High impact. Est. 10 hours for core proficiency.')" },
                  hours: { type: Type.INTEGER, description: "Estimated hours to learn this subject" }
                },
                required: ["name", "progress", "impact", "hours"]
              },
              description: "3 highly relevant specific skills development areas to learn next."
            },
            skillsRadar: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  subject: { type: Type.STRING, description: "Category/subject header such as 'React', 'Python', 'Cloud', 'Node.js', 'Leadership'" },
                  required: { type: Type.INTEGER, description: "Level required by job (0 to 100)" },
                  you: { type: Type.INTEGER, description: "Applicant's evaluated level matching this category (0 to 100)" }
                },
                required: ["subject", "required", "you"]
              },
              description: "Exactly 5 or 6 radar dimensions matching the job profile."
            }
          },
          required: ["matchPercentage", "fitLevel", "summary", "skills", "skillsLearn", "skillsRadar"]
        }
      }
    });

    const bodyText = response.text;
    if (!bodyText) {
      throw new Error("Empty response token received from Gemini.");
    }

    const data = JSON.parse(bodyText.trim());
    return res.json({ ...data, isMock: false });

  } catch (error: any) {
    console.error("Gemini API Error in /api/analyze:", error);
    // Fall back gracefully to mock analysis so application state is uninterrupted
    const fallback = generateMockResponse(
      req.body.cvText || "Applicant Resume Content", 
      req.body.jobDesc || "Target Profile Details"
    );
    return res.json({ 
      ...fallback, 
      isMock: true, 
      errorMessage: error.message || "An error occurred with Gemini API. Switched to smart simulated parsing." 
    });
  }
});

// 2. Generate Cover Letter
app.post("/api/generate-cover-letter", async (req, res) => {
  try {
    const { cvText, jobDesc, analysisSummary, matchPercentage } = req.body;

    if (!jobDesc) {
      return res.status(400).json({ error: "Job description is required to target the letter." });
    }

    const ai = getGenAI();
    if (!ai) {
      console.log("No GEMINI_API_KEY. Generating highly personalized custom mock cover letter.");
      const letter = generateMockCoverLetter(cvText, jobDesc, matchPercentage);
      return res.json({ coverLetter: letter, isMock: true });
    }

    console.log("Starting real Gemini API Cover Letter generation...");
    
    const prompt = 
      `Applicant Resume/Bio Context:\n${cvText || "Energetic, skilled professional with a strong match."}\n\n` +
      `Target Job Description:\n${jobDesc}\n\n` +
      `Automated Fit Analysis Summary:\n${analysisSummary || "The applicant fits well with key competencies."}\n\n` +
      `Match Score: ${matchPercentage || 85}%\n\n` +
      "Relying on the above details, write a highly targeted, elegant, and persuasive professional Cover Letter in markdown format. " +
      "Focus deeply on highlighting how the applicant's existing skills can immediately add value. Be concise, respectful, and articulate. " +
      "Frame the tone as visionary, professional, and logic-driven. Emphasize target metrics. Return your response in JSON format holding a single 'coverLetter' string.";

    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            coverLetter: { 
              type: Type.STRING, 
              description: "The complete markdown-formatted cover letter content." 
            }
          },
          required: ["coverLetter"]
        }
      }
    });

    const bodyText = response.text;
    if (!bodyText) {
      throw new Error("No cover letter text received from Gemini.");
    }

    const data = JSON.parse(bodyText.trim());
    return res.json({ ...data, isMock: false });

  } catch (error: any) {
    console.error("Gemini Cover Letter Error:", error);
    // Fall back to high-quality fallback letter
    const letter = generateMockCoverLetter(
      req.body.cvText, 
      req.body.jobDesc, 
      req.body.matchPercentage || 85
    );
    return res.json({ 
      coverLetter: letter, 
      isMock: true, 
      errorMessage: error.message || "Switched to smart simulated generator." 
    });
  }
});

// Mock cover letter generator for beautiful offline fallback
function generateMockCoverLetter(cvText: string = "", jobDesc: string = "", matchPct: number = 85): string {
  // Extract custom terms to inject
  const matchComp = jobDesc.match(/([A-Z][a-zA-Z0-9\+\#\-\.\s]{2,15})(?=\s|,|\.)/g) || [];
  const primaryTerm = matchComp[0] || "Frontend Engineer";
  const organization = jobDesc.match(/([A-Z][a-zA-Z\s]{2,15}\s(Inc\.|Corporation|LLC|Co\.|Technologies|Solutions))/)?.[0] || "Target Innovators";

  return `### Cover Letter

Dear Hiring Committee,

I am writing to express my eager interest in the **${primaryTerm}** role at **${organization}**. Following an automated fit scoring evaluation of my qualifications against your specific stack, my credentials returned a **${matchPct}% match rating**—signaling a powerful strategic and technical alignment with your needs.

Your team is searching for a professional who can deliver exceptional quality while streamlining development cycle-time. Across my career, I have prioritized modular code architecture and optimized data strategies. My background in developing resilient web assets directly supports your goals for cross-functional efficiency, agile alignment, and scalable delivery.

I am particularly excited about how my hands-on qualifications map to your current priorities. This alignment enables me to ramp up quickly, assume immediate system responsibilities, and contribute to your team's velocity on Day One.

Thank you for your time and analytical view of my candidacy. I look forward to discussing how my experience can address your tactical challenges in detail.

Sincerely,  
**Your Dedicated AI Assistant (on behalf of Candidate)**`;
}

// 3. Vite development middleware / production static server configuration
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    // Development mode with hot reloads handled by Vite middleware
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    // Production mode
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`[CareerPulse Server] Service initiated on http://localhost:${PORT}`);
  });
}

startServer();
