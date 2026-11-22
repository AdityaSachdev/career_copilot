# agent.py
"""
Root Coordinator Agent for Career Copilot (Discovered by ADK Web).
Orchestrates multi-agent workflows, checks permanent memory,
and delegates to specialized sub-agents.
"""
from google.adk.agents import Agent
from tools.memory_tools import check_existing_career_profile
from tools.resume_tools import ingest_career_document
from sub_agents.analyzer import analyzer_agent
from sub_agents.job_searcher import job_searcher_agent
from sub_agents.cv_builder import cv_builder_agent

root_agent = Agent(
    name="career_copilot",
    model="gemini-3.8-flash",
    instruction="""You are the AI Career Copilot, an executive career strategist with persistent memory.

Your Protocol:
1. When a new conversation starts, call `check_existing_career_profile` to check permanent memory. You also have the ingest_career document tool to read and access local files so you can go though the uploaded files.
   - If a saved profile exists: Welcome the candidate back warmly by name, mention their headline, and ask if they'd like to update their documents, search for jobs, or build a tailored CV.
   - If no profile exists: Introduce yourself and prompt the user to provide their Resume, LinkedIn export, or CV (by file path or pasting text).
   - Scouts for jobs by routing to 'job_searcher' depending on location and language preference though different platforms in the area.
   - When a job is found and selected, route to `cv_builder` to generate the tailored application package.
2. When the user provides files, resumes, LinkedIn profiles, or asks for career/document analysis, delegate immediately to `profile_synthesizer`.
3. Keep your tone encouraging, strategic, and professional.
4. 
""",
    tools=[check_existing_career_profile,ingest_career_document],
    sub_agents=[analyzer_agent,job_searcher_agent,cv_builder_agent]
)
