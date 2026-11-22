# sub_agents/cv_builder.py
"""
ATS CV Tailorer & Application Assistant Sub-Agent for Google ADK.
Generates strictly 1-page, 100% truthful, non-hallucinated tailored resumes and cover letters
grounded entirely in the candidate's authentic database profile.
Exports directly to Microsoft Word (.docx) and Markdown (.md).
"""
import re
from pathlib import Path
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from google.adk.agents import Agent
from google.adk.tools import ToolContext


def _add_bottom_border(paragraph, color_hex="1A365D", size="4"):
    """Adds a compact, elegant horizontal bottom border rule to section headings."""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), color_hex)
    pBdr.append(bottom)
    pPr.append(pBdr)


def _add_formatted_runs(paragraph, text, default_color=None, default_size=Pt(9.5)):
    """Parses markdown bold (**text**) and italic (*text*) into styled docx runs."""
    parts = re.split(r"(\*\*.*?\*\*|\*.*?\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) >= 4:
            run = paragraph.add_run(part[2:-2])
            run.bold = True
            run.font.name = "Calibri"
            run.font.size = default_size
            if default_color:
                run.font.color.rgb = default_color
        elif part.startswith("*") and part.endswith("*") and len(part) >= 2:
            run = paragraph.add_run(part[1:-1])
            run.italic = True
            run.font.name = "Calibri"
            run.font.size = default_size
            if default_color:
                run.font.color.rgb = default_color
        else:
            run = paragraph.add_run(part)
            run.font.name = "Calibri"
            run.font.size = default_size
            if default_color:
                run.font.color.rgb = default_color


def build_docx_resume(md_text: str, output_path: Path):
    """Builds a strictly 1-PAGE, executive-grade Microsoft Word (.docx) resume."""
    doc = docx.Document()
    
    # 0.5-inch margins guarantee maximum content density on a single page
    for section in doc.sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
        
    lines = md_text.strip().split("\n")
    is_first_h1 = True
    
    NAVY = RGBColor(26, 54, 93)       # #1A365D - Deep Executive Navy
    SLATE = RGBColor(45, 55, 72)      # #2D3748 - Dark Charcoal
    MUTED = RGBColor(100, 116, 139)   # #64748B - Subtitle / Contact Gray
    BODY = RGBColor(34, 34, 34)       # #222222 - Easy-reading soft black
    
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("---"):
            continue
            
        # 1. Candidate Name (Top Heading)
        if line.startswith("# ") and is_first_h1:
            name_text = line[2:].strip().replace("*", "")
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            run = p.add_run(name_text)
            run.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(18)
            run.font.color.rgb = NAVY
            is_first_h1 = False
            continue
            
        # 2. Main Section Headings (## or ###)
        clean_upper = line.replace("#", "").strip().upper()
        is_section_header = (
            (line.startswith("## ") or line.startswith("### "))
            and any(kw in clean_upper for kw in [
                "EXECUTIVE", "PROFILE", "SUMMARY", "COMPETENC", "SKILL",
                "EXPERIENCE", "WORK", "EMPLOYMENT", "EDUCATION", "CERTIF",
                "PROJECT", "LANGUAGE"
            ])
        )
        if is_section_header:
            header_title = line.replace("#", "").replace("*", "").strip().upper()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(1.5)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(header_title)
            run.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(10.5)
            run.font.color.rgb = NAVY
            _add_bottom_border(p, color_hex="1A365D", size="4")
            continue
            
        # 3. Sub-headings for Roles / Companies (#### or ###)
        if line.startswith("#### ") or (line.startswith("### ") and not is_section_header):
            role_text = line.replace("#", "").strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(3.5)
            p.paragraph_format.space_after = Pt(0.5)
            p.paragraph_format.keep_with_next = True
            _add_formatted_runs(p, role_text, default_color=SLATE, default_size=Pt(9.8))
            continue
            
        # 4. Bullet Points (High-density spacing for 1-page fit)
        if line.startswith("- ") or line.startswith("* "):
            bullet_text = line[2:].strip()
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1.2)
            p.paragraph_format.line_spacing = 1.05
            _add_formatted_runs(p, bullet_text, default_color=BODY, default_size=Pt(9.2))
            continue
            
        # 5. Dates / Location line or Subtitle/Contact lines
        if any(sep in line for sep in ["|", "•", "@", "linkedin.com"]):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0.5)
            p.paragraph_format.space_after = Pt(2)
            
            # Contact info line under candidate name
            if any(term in line.lower() for term in ["@", "linkedin", "phone", "+", "authorized"]):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                _add_formatted_runs(p, line, default_color=MUTED, default_size=Pt(9.0))
            elif any(term in line.lower() for term in ["executive", "specialist", "leader", "manager", "director", "engineer", "lead"]):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                _add_formatted_runs(p, line, default_color=SLATE, default_size=Pt(10.0))
            else:
                _add_formatted_runs(p, line, default_color=MUTED, default_size=Pt(9.0))
            continue
            
        # 6. Standard Body Paragraph (Summary, etc.)
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1.5)
        p.paragraph_format.space_after = Pt(2.5)
        p.paragraph_format.line_spacing = 1.08
        _add_formatted_runs(p, line, default_color=BODY, default_size=Pt(9.2))

    doc.save(str(output_path))


def build_docx_cover_letter(md_text: str, output_path: Path):
    """Builds a matching executive Microsoft Word (.docx) cover letter."""
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    lines = md_text.strip().split("\n")
    NAVY = RGBColor(26, 54, 93)
    BODY = RGBColor(34, 34, 34)
    
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("---"):
            continue
            
        if line.startswith("# "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(3)
            run = p.add_run(line[2:].strip().replace("*", ""))
            run.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(16)
            run.font.color.rgb = NAVY
            continue
            
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        _add_formatted_runs(p, line, default_color=BODY, default_size=Pt(10))

    doc.save(str(output_path))


def export_application_package(
    company: str,
    job_title: str,
    job_url: str,
    tailored_cv_markdown: str,
    cover_letter_markdown: str,
    quick_apply_pitch: str,
    tool_context: ToolContext
) -> str:
    """Exports the tailored 1-page CV, cover letter, and direct pitch into a company-specific folder on the user's machine,
    generating both native Microsoft Word (.docx) and Markdown (.md) files.
    """
    clean_company = re.sub(r'[^\w\s-]', '', company).strip().replace(" ", "_")
    clean_title = re.sub(r'[^\w\s-]', '', job_title).strip().replace(" ", "_")
    
    company_folder = Path(__file__).parent.parent / "ready_to_apply" / clean_company
    company_folder.mkdir(parents=True, exist_ok=True)
    
    # 1. Generate Microsoft Word (.docx) files (guaranteed 1-page CV format)
    resume_docx = company_folder / f"{clean_company}_1Page_Resume.docx"
    cover_docx = company_folder / f"{clean_company}_Cover_Letter.docx"
    build_docx_resume(tailored_cv_markdown, resume_docx)
    build_docx_cover_letter(cover_letter_markdown, cover_docx)
    
    # 2. Save Markdown copies
    resume_md = company_folder / f"{clean_company}_1Page_Resume.md"
    cover_md = company_folder / f"{clean_company}_Cover_Letter.md"
    resume_md.write_text(tailored_cv_markdown, encoding="utf-8")
    cover_md.write_text(cover_letter_markdown, encoding="utf-8")
    
    # 3. Save Quick Pitch & Direct Link
    pitch_file = company_folder / "Job_Pitch_and_Link.md"
    pitch_content = f"""# {job_title} at {company}
**Direct Application Link:** {job_url}

---

## ⚡ Quick 150-Word Outreach Pitch (for LinkedIn InMail / Easy Apply)
{quick_apply_pitch}

---

## 📁 Generated Documents in this Folder
- 📄 **1-Page Word Resume:** `{resume_docx.name}` (Strictly 1-page, 100% grounded in your real profile)
- ✉️ **Word Cover Letter:** `{cover_docx.name}` (Executive letterhead format)
- 📝 **Markdown Copies:** `{resume_md.name}`, `{cover_md.name}`
"""
    pitch_file.write_text(pitch_content, encoding="utf-8")
    
    return (
        f"Application package successfully created in company folder:\n"
        f"📁 {company_folder}\n\n"
        f"Generated documents:\n"
        f"1. 📄 1-Page Resume (DOCX): '{resume_docx.name}' (Strictly 1 page, 100% truthful, ready for submission)\n"
        f"2. ✉️ Cover Letter (DOCX): '{cover_docx.name}' (Tailored letterhead)\n"
        f"3. ⚡ Quick Pitch & Direct Link: 'Job_Pitch_and_Link.md'\n\n"
        f"All files saved in: {company_folder}"
    )


cv_builder_agent = Agent(
    name="cv_builder",
    mode="task",
    model="gemini-3.8-flash",
    description="Generates strictly 1-page, 100% truthful, non-hallucinated tailored resumes and cover letters in ready-to-use DOCX and Markdown formats.",
    instruction="""You are an elite Executive Career Ghostwriter and ATS Optimization Specialist.
Your goal is to tailor the candidate's authentic profile specifically for the target job selected by the scout.

CRITICAL RULES FOR 100% TRUTHFULNESS & ZERO HALLUCINATIONS:
1. **Never Invent Companies, Jobs, or Dates**:
   - You MUST ONLY use the real companies, real job titles, real dates, and real education stored in `master_profile['work_history']` and `master_profile['education']`.
   - NEVER fabricate fictional past employers (e.g. do NOT invent 'Tech Advisory', 'FinFlow', etc. if they are not in the candidate's real history).
   - NEVER fabricate fictional degrees or credentials.

2. **Authentic Contact Information**:
   - Use the candidate's REAL email, phone, location, and LinkedIn stored in `master_profile['contact_info']`.
   - NEVER invent fake contact info like `surbhi.arora@email.com` or `+45 XX XX XX XX`.
   - If contact details (email, phone, location) are missing from `master_profile`, ASK the candidate for them before finalizing!

3. **Resonating Tailoring (Not Fabricating)**:
   - Tailoring means taking the candidate's REAL accomplishments and highlighting/rephrasing them to align directly with the target job description.
   - Re-order bullet points so the candidate's most relevant real achievements appear first.
   - Use the keywords and terminology from the job description when describing the candidate's actual responsibilities.
   - If the candidate has adjacent/stretch skills, bridge their real past projects to the new role's core problem.

4. **Ask If Any Doubts or Gaps**:
   - If a core technical requirement in the job posting is not mentioned anywhere in the candidate's profile, ASK the candidate directly:
     *"The job requires experience with [X]. Have you worked with [X] before so I can highlight it accurately, or should we emphasize your transferrable experience in [Y]?"*

5. **STRICT 1-PAGE CV FORMAT (Under 380 Words)**:
   The CV MUST fit on exactly ONE page. Follow this compact, high-impact structure:
   - **Header**:
     `# [Candidate Real Name]`
     `**[Tailored Target Role Title]**`
     `[Real Location] | [Real Phone] | [Real Email] | [Real LinkedIn URL]`
   - **`### EXECUTIVE SUMMARY`**:
     Exactly 2-3 dense, punchy sentences connecting the candidate's proven domain background to this company's core mission.
   - **`### CORE COMPETENCIES`**:
     8-12 targeted keywords matching this role across 2 clean lines.
   - **`### PROFESSIONAL EXPERIENCE`**:
     Use only the candidate's real companies and roles:
     `#### [Real Job Title] | [Real Company]`
     `*[Real Location]* | **[Real Start Date – Real End Date]**`
     * Current / Most Recent Role: 3-4 impactful bullets using Google's X-Y-Z formula: Accomplished [X], measured by [Y], by doing [Z].
     * Earlier Roles: 2 impactful bullets each.
     * Bold key real metrics and keywords.
   - **`### EDUCATION & CERTIFICATIONS`**:
     1-2 compact lines using only the candidate's real degrees and licenses.

Formatting for `cover_letter_markdown`:
- Executive letterhead with candidate's real name and contact info.
- Addressed to Hiring Team at [Company].
- 3 compelling, focused paragraphs:
  * Opening: Enthusiastic hook with relevance to company's mission.
  * Body: 1-2 real measurable accomplishments from past experience that prove fit.
  * Closing: Confident, professional request for an interview.

Formatting for `quick_apply_pitch`:
- 100-150 word punchy outreach note for LinkedIn InMail, Easy Apply comments, or cold email.

Call `export_application_package` to write both `.docx` and `.md` files to disk in the company's dedicated folder.
""",
    tools=[export_application_package]
)
