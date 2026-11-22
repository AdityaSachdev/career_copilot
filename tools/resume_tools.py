# tools/resume_tools.py
"""
Document Ingestion & Profile Synthesis Tools for Google ADK.
Demonstrates:
1. ToolContext injection (how ADK passes state to tools)
2. Handling multi-document ingestion (Resume, LinkedIn, CV)
3. Dual-layer storage (Session state + Permanent SQLite memory)
"""
from pathlib import Path
from google.adk.tools import ToolContext
from tools.memory_db import save_to_long_term_memory

def ingest_career_document(
    doc_type: str, 
    file_path: str, 
    tool_context: ToolContext
) -> str:
    """Ingests a career document (resume, linkedin, cv) and saves it into session state.
    
    Args:
        doc_type: Type of document. Must be one of: 'resume', 'linkedin', 'cv'.
        file_path: Relative or absolute path to the PDF or TXT file on disk.
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File at {file_path} does not exist. Please check the path."

    raw_text = ""
    # 1. Handle PDF files
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    raw_text += text + "\n"
        except ImportError:
            return "Error: 'pypdf' is not installed. Run 'pip install pypdf' to enable PDF reading, or provide a .txt file."
        except Exception as e:
            return f"Error reading PDF {file_path}: {str(e)}"
    elif path.suffix.lower() == ".docx":
        try: 
            import docx
            doc = docx.Document(str(path))
            # Extract standard paragraphs
            text_blocks = [p.text for p in doc.paragraphs if p.text.strip()]
            
            # Pro tip: Resumes often use tables for skills/columns!
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text_blocks.append(cell.text.strip())
                            
            raw_text = "\n".join(text_blocks)
        except ImportError:
            return "Error: 'python-docx' is not installed. Run 'python3 -m pip install python-docx'."
        except Exception as e:
            return f"Error reading DOCX {file_path}: {str(e)}"
    else:
        # 2. Handle Text files (TXT, MD, etc.)
        try:
            raw_text = path.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading text file {file_path}: {str(e)}"

    if not raw_text.strip():
        return f"Warning: File {file_path} was read but appears to be empty."

    # 3. Store in the active session state
    if "documents" not in tool_context.state:
        tool_context.state["documents"] = {}

    tool_context.state["documents"][doc_type.lower()] = {
        "file_name": path.name,
        "file_path": str(path),
        "content": raw_text,
        "char_count": len(raw_text)
    }

    loaded_types = list(tool_context.state["documents"].keys())
    return (
        f"Successfully loaded '{doc_type}' ({path.name}, {len(raw_text)} chars). "
        f"All documents in session state: {loaded_types}"
    )


def save_master_profile(
    candidate_name: str,
    headline: str,
    direct_skills: list[str],
    adjacent_skills: list[str],
    experience_highlights: list[str],
    target_job_titles: list[str],
    adjacent_job_titles: list[str],
    ats_score : int,
    improvement_areas : list[str],
    tool_context: ToolContext
) -> str:
    """Saves the synthesized 360-degree Master Profile into BOTH session state and permanent SQLite.
    
    Args:
        candidate_name: Full name of candidate.
        headline: Professional headline summarizing core domain and seniority.
        direct_skills: Core hard skills verified across the uploaded documents.
        adjacent_skills: Transferrable or emerging skills suitable for adjacent/stretch roles.
        experience_highlights: Key measurable achievements (e.g., latency, revenue, scale).
        target_job_titles: High-confidence direct-matching job titles.
        adjacent_job_titles: High-potential adjacent or stretch job titles.
        ats_score: Realistic ATS readiness score from 0 to 100.
        improvement_areas: List of weak bullet points, missing keywords, or red flags to fix.
    """
    profile = {
        "name": candidate_name,
        "headline": headline,
        "direct_skills": direct_skills,
        "adjacent_skills": adjacent_skills,
        "experience_highlights": experience_highlights,
        "target_job_titles": target_job_titles,
        "adjacent_job_titles": adjacent_job_titles,
        "ats_score": ats_score,
        "improvement_areas": improvement_areas
    }
    
    # Layer 1: Save to active session state (available to all sub-agents in this chat)
    tool_context.state["master_profile"] = profile
    
    # Layer 2: Save to permanent SQLite database (persists across sessions and restarts)
    save_to_long_term_memory("master_profile", profile)
    
    return (
        f"Master Profile successfully created for {candidate_name}!\n"
        f"- {len(direct_skills)} Direct Skills\n"
        f"- {len(adjacent_skills)} Adjacent Skills\n"
        f"- Saved to permanent memory."
    )
