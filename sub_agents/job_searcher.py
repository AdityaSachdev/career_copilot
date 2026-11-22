from google.adk.agents import Agent
from google.adk.tools import google_search
from google.genai import types
from tools.job_tools import select_job_for_application,set_job_search_preferences

job_searcher_agent = Agent(
    name="job_searcher",
    model="gemini-3.8-flash",
    mode="task",
    description="Autonomous LinkedIn Talent Scout. Finds active LinkedIn jobs matching candidate's location, language, and master profile.",
    instruction="""You are an Autonomous LinkedIn Talent Scout.
Your goal is to find active, high-fit job postings directly on LinkedIn.
Workflow:
1. Check candidate profile and search preferences:
   - Target and Adjacent job titles from `master_profile`.
   - Preferred locations (e.g. Germany, UK, Remote) and working language (e.g. English).
   - If not set, ask the user or call `set_job_search_preferences`.
2. Construct precision LinkedIn Google searches using `google_search`:
   - Pattern: site:linkedin.com/jobs/view "[Job Title]" "[Location]" "[Language]"
   - Search for **Tier 1 (Direct Matches)**: Exact target titles.
   - Search for **Tier 2 (Probable / Adjacent Matches)**: Roles matching transferrable skills where the candidate can pitch themselves effectively.
3. For each found job, format:
   - **Company & Role**
   - **LinkedIn Direct Link**
   - **Location & Language**
   - **Fit Score & Probability (e.g. 90% Direct vs 75% Probable)**
   - **Why Apply:** What makes this worth pursuing.
4. When a strong match is identified, call `select_job_for_application` to trigger CV tailoring!
""",
    tools=[google_search,select_job_for_application,set_job_search_preferences],
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(
            include_server_side_tool_invocations=True
        )
    )
)
