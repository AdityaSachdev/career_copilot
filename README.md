# AI Career Copilot 🚀

An autonomous multi-agent career strategist and talent scout built with **Google Agent Development Kit (ADK)** and **Gemini 3**.

---

## 🌟 Key Features

- **Multi-Agent Architecture:**
  - **Root Coordinator (`career_copilot`):** Manages user interactions, identity verification, and multi-agent delegation.
  - **Profile Synthesizer (`profile_synthesizer`):** Ingests Resumes, LinkedIn exports, and CVs (PDF, DOCX, TXT) to compute ATS readiness scores, core competencies, and adjacent skills.
  - **Talent Scout (`job_searcher`):** Autonomous LinkedIn job discovery grounded with real-time Google Search.
  - **Executive Ghostwriter (`cv_builder`):** Generates targeted ATS-optimized resumes and cover letters in native Microsoft Word (`.docx`) and Markdown (`.md`) formats.
- **Persistent Memory:** Dual-layer memory architecture pairing active session state with permanent SQLite storage (`career_memory.db`) for tracking candidate profiles and applied jobs.
- **Organized Application Packages:** Automatically organizes tailored CVs and cover letters into company-specific folders (`ready_to_apply/{Company}/`).

---

## 🛠️ Project Structure

```text
career_copilot/
├── agent.py                 # Root coordinator agent (Discovered by ADK Web)
├── sub_agents/
│   ├── analyzer.py          # Profile synthesis & document ingestion
│   ├── job_searcher.py      # Autonomous LinkedIn job searcher (Google Search tool)
│   └── cv_builder.py        # Tailored CV, Cover Letter (.docx & .md) generator
├── tools/
│   ├── memory_tools.py      # Identity & memory access tools
│   ├── memory_db.py         # Persistent SQLite database operations
│   ├── resume_tools.py      # Document ingestion & master profile synthesis
│   └── job_tools.py         # Job selection & search preference tools
├── ready_to_apply/          # Generated company application packages
├── sample_data/             # Example resume and LinkedIn data
└── requirements.txt         # Project dependencies
```

---

## 🚀 Quickstart

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/<your-username>/career_copilot.git
cd career_copilot
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Add your Gemini API Key in `.env`:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Launch the ADK Web UI
```bash
adk web .
```
Open your browser at `http://127.0.0.1:8000` to interact with the Career Copilot!
