# sub_agents/cv_builder.py
"""
ATS CV Tailorer & Application Assistant Sub-Agent for Google ADK.
Generates executive-grade tailored resumes and cover letters,
and exports them directly into beautifully styled Microsoft Word (.docx) documents.
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


def _add_bottom_border(paragraph, color_hex="1A365D", size="6"):
    """Adds a stylish horizontal bottom border rule to section headings."""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), "3")
    bottom.set(qn("w:color"), color_hex)
    pBdr.append(bottom)
    pPr.append(pBdr)


def _add_formatted_runs(paragraph, text, default_color=None, default_size=Pt(10)):
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
    """Builds an executive-grade, ATS-optimized Microsoft Word (.docx) resume."""
    doc = docx.Document()
    
    # Professional 0.65 inch margins maximize clean layout without crowding
    for section in doc.sections:
        section.top_margin = Inches(0.65)
        section.bottom_margin = Inches(0.65)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)
        
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
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(name_text)
            run.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(22)
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
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(header_title)
            run.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(11.5)
            run.font.color.rgb = NAVY
            _add_bottom_border(p, color_hex="1A365D", size="6")
            continue
            
        # 3. Sub-headings for Roles / Companies (#### or ###)
        if line.startswith("#### ") or (line.startswith("### ") and not is_section_header):
            role_text = line.replace("#", "").strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.keep_with_next = True
            _add_formatted_runs(p, role_text, default_color=SLATE, default_size=Pt(10.5))
            continue
            
        # 4. Bullet Points
        if line.startswith("- ") or line.startswith("* "):
            bullet_text = line[2:].strip()
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2.5)
            p.paragraph_format.line_spacing = 1.15
            _add_formatted_runs(p, bullet_text, default_color=BODY, default_size=Pt(9.8))
            continue
            
        # 5. Dates / Location line or Subtitle/Contact lines
        if any(sep in line for sep in ["|", "•", "@", "linkedin.com"]):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(3)
            
            # Contact info line under candidate name
            if any(term in line.lower() for term in ["@", "linkedin", "phone", "+", "authorized"]):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                _add_formatted_runs(p, line, default_color=MUTED, default_size=Pt(9.2))
            elif any(term in line.lower() for term in ["executive", "specialist", "leader", "manager", "director", "engineer"]):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                _add_formatted_runs(p, line, default_color=SLATE, default_size=Pt(10.5))
            else:
                _add_formatted_runs(p, line, default_color=MUTED, default_size=Pt(9.5))
            continue
            
        # 6. Standard Body Paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        _add_formatted_runs(p, line, default_color=BODY, default_size=Pt(9.8))

    doc.save(str(output_path))


def build_docx_cover_letter(md_text: str, output_path: Path):
    """Builds an executive-grade Microsoft Word (.docx) cover letter."""
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
        
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
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(line[2:].strip().replace("*", ""))
            run.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(18)
            run.font.color.rgb = NAVY
            continue
            
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        _add_formatted_runs(p, line, default_color=BODY, default_size=Pt(10.5))

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
    """Exports the tailored CV, cover letter, and direct pitch into a company-specific folder on the user's machine,
    generating both native Microsoft Word (.docx) and Markdown (.md) files ready for direct job submission.
    """
    # 1. Clean company and title names for folder path
    clean_company = re.sub(r'[^\w\s-]', '', company).strip().replace(" ", "_")
    clean_title = re.sub(r'[^\w\s-]', '', job_title).strip().replace(" ", "_")
    
    # 2. Define the company folder path inside 'ready_to_apply'
    company_folder = Path(__file__).parent.parent / "ready_to_apply" / clean_company
    company_folder.mkdir(parents=True, exist_ok=True)
    
    # 3. Generate Microsoft Word (.docx) files
    resume_docx = company_folder / f"{clean_company}_Tailored_Resume.docx"
    cover_docx = company_folder / f"{clean_company}_Cover_Letter.docx"
    build_docx_resume(tailored_cv_markdown, resume_docx)
    build_docx_cover_letter(cover_letter_markdown, cover_docx)
    
    # 4. Save Markdown files for review or copy-pasting
    resume_md = company_folder / f"{clean_company}_Tailored_Resume.md"
    cover_md = company_folder / f"{clean_company}_Cover_Letter.md"
    resume_md.write_text(tailored_cv_markdown, encoding="utf-8")
    cover_md.write_text(cover_letter_markdown, encoding="utf-8")
    
    # 5. Save Quick Pitch & Link
    pitch_file = company_folder / "Job_Pitch_and_Link.md"
    pitch_content = f"""# {job_title} at {company}
**LinkedIn Job Link:** {job_url}

---

## ⚡ Quick 150-Word Pitch (for LinkedIn InMail / Easy Apply)
{quick_apply_pitch}

---

## 📁 Generated Files in this Folder
- 📄 **Word Resume:** `{resume_docx.name}` (Formatted executive DOCX, ready to upload directly!)
- ✉️ **Word Cover Letter:** `{cover_docx.name}` (Professional formatted letterhead DOCX)
- 📝 **Markdown Copies:** `{resume_md.name}`, `{cover_md.name}`
"""
    pitch_file.write_text(pitch_content, encoding="utf-8")
    
    # 6. Return the exact paths so the agent can show them clearly to the user
    return (
        f"Application package successfully created in company folder:\n"
        f"📁 {company_folder}\n\n"
        f"Generated ready-to-use documents:\n"
        f"1. 📄 Resume (DOCX): '{resume_docx.name}' (Professional Word format ready for direct application)\n"
        f"2. ✉️ Cover Letter (DOCX): '{cover_docx.name}' (Matching executive letterhead)\n"
        f"3. ⚡ Quick Pitch & Links: 'Job_Pitch_and_Link.md'\n\n"
        f"All files are saved in: {company_folder}"
    )


cv_builder_agent = Agent(
    name="cv_builder",
    mode="task",
    model="gemini-3.8-flash",
    description="Takes a selected job and candidate master profile, and generates a tailored ATS CV and cover letter in ready-to-use DOCX and Markdown formats.",
    instruction="""You are an elite Executive Career Ghostwriter and ATS Optimization Specialist.
Your goal is to tailor the candidate's Master Profile specifically for the target job selected by the scout, producing executive-quality application materials in ready-to-use format.

Formatting & Structure Standards for `tailored_cv_markdown`:
1. **Header**:
   - `# [Candidate Full Name]`
   - `**[Tailored Target Job Title] | [Core Domain Specialization]**`
   - Contact Row: `[Location] | [Phone] | [Email] | [LinkedIn Profile URL] | [Work Authorization]`
2. **`### EXECUTIVE SUMMARY`**:
   - 3-4 punchy, high-impact sentences communicating candidate's proven value proposition, years of experience, and exact alignment with this role's core mission.
3. **`### CORE COMPETENCIES & EXPERTISE`**:
   - 12-16 high-frequency ATS keywords matching this job description, separated logically into Direct Core Skills and Methodological/Technical Skills.
4. **`### PROFESSIONAL EXPERIENCE`**:
   - Format: `#### [Job Title] | [Company]`
   - `*[Location]* | **[Start Date – End Date]**`
   - Bullet points MUST follow Google's X-Y-Z formula: "Accomplished [X] as measured by [Y], by doing [Z]".
   - Bold key business metrics (€/$ revenue, % efficiency, deal sizes, team scale) and industry methodologies (e.g. MEDDPICC, Agile, AWS, Python, CRM).
5. **`### EDUCATION & CERTIFICATIONS`**:
   - Degrees, institutions, and relevant industry licenses/certifications.
6. **`### LANGUAGES`**:
   - Language proficiencies.

Formatting & Structure for `cover_letter_markdown`:
- Professional letterhead with candidate name, contact info, and date.
- Addressed to Hiring Manager / Talent Acquisition Team at [Company].
- **Opening**: Targeted hook demonstrating understanding of the company's product/mission and stating why candidate is the ideal fit.
- **Body**: 2 paragraphs with specific measurable achievements mirroring this role's needs. Use "bridge framing" for adjacent/stretch skills.
- **Closing**: Confident, courteous call to action requesting an interview.

Formatting for `quick_apply_pitch`:
- 100-150 word punchy, compelling outreach note suitable for LinkedIn InMail, Easy Apply comments, or cold email.

Execution:
- Call `export_application_package` to generate both `.docx` and `.md` files in the company's dedicated folder.
- Notify the user with a summary and provide the exact file paths!
""",
    tools=[export_application_package]
)
