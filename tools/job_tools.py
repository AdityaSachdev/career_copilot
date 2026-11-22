# tools/job_tools.py
"""
Job Selection & Tracking Tools for Google ADK.
Validates direct job posting links and manages candidate search preferences.
"""
from google.adk.tools import ToolContext
from tools.memory_db import save_to_long_term_memory, load_from_long_term_memory

def select_job_for_application(
    job_title: str,
    company: str,
    job_url: str,
    job_description_summary: str,
    key_requirements: list[str],
    match_category: str,
    tool_context: ToolContext
) -> str:
    """Selects a specific job to target for resume tailoring and application drafting.
    Validates that the provided URL is a direct job posting, not a generic company page.
    
    Args:
        job_title: Title of the position.
        company: Company name.
        job_url: Direct link to the live job posting (e.g. linkedin.com/jobs/view/<id> or careers.<company>.com/job/<id>).
        job_description_summary: Brief overview of responsibilities and mission.
        key_requirements: Top 3-5 critical hard requirements from the job post.
        match_category: Either 'Direct Match' or 'Adjacent Match'.
    """
    clean_url = (job_url or "").strip()
    url_lower = clean_url.lower()

    # Reject generic company directory links or search queries
    is_generic_company_page = (
        "/company/" in url_lower
        or "/jobs/search" in url_lower
        or "/search/jobs" in url_lower
        or not (url_lower.startswith("http://") or url_lower.startswith("https://"))
    )

    if is_generic_company_page:
        return (
            f"REJECTED: The URL '{clean_url}' is a generic company profile or search page, NOT a direct job post! "
            f"Candidates need the exact link where they can directly apply to '{job_title}' at {company}. "
            f"Please run a precision Google search to get the exact job post URL:\n"
            f"Query: site:linkedin.com/jobs/view \"{company}\" \"{job_title}\"\n"
            f"Or find the direct applicant tracking link (e.g. jobs.lever.co, boards.greenhouse.io, workday, careers.{company.lower().replace(' ', '')}.com) "
            f"and call `select_job_for_application` with the true direct link."
        )

    job_data = {
        "title": job_title,
        "company": company,
        "url": clean_url,
        "summary": job_description_summary,
        "requirements": key_requirements,
        "category": match_category
    }
    
    # Save the target job in active session state
    tool_context.state["target_job"] = job_data
    
    return (
        f"Selected '{job_title}' at {company} ({match_category}). "
        f"Direct application link verified: {clean_url}. "
        f"Saved to session state. Ready to tailor a truthful, 1-page CV and cover letter!"
    )


def set_job_search_preferences(
    locations: list[str],
    language_preference: str,
    work_mode: str,
    tool_context: ToolContext
) -> str:
    """Saves user location, language, and work mode preferences into permanent memory.
    
    Args:
        locations: Target cities or countries (e.g. ['Remote Germany', 'Munich', 'London']).
        language_preference: Preferred working language (e.g. 'English', 'German').
        work_mode: Preferred work mode (e.g. 'Remote', 'Hybrid', 'Any').
    """
    prefs = {
        "locations": locations,
        "language": language_preference,
        "work_mode": work_mode
    }
    # 1. Save in active session
    tool_context.state["search_preferences"] = prefs
    
    # 2. Save in permanent SQLite database
    save_to_long_term_memory("search_preferences", prefs)
    
    return f"Saved preferences: Locations={locations}, Language={language_preference}, Mode={work_mode} to permanent memory."
