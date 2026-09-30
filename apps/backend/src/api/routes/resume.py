from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from src.api import deps
from src.models.user import User
import tempfile
import os

router = APIRouter()

@router.post("/extract")
async def extract_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Extract text from a resume (PDF) and perform deterministic extraction of skills and experience.
    This does NOT save the data to the user profile. It only returns the extracted payload.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for MVP.")
    
    try:
        import pdfplumber
    except ImportError:
        raise HTTPException(status_code=500, detail="PDF parsing library not installed.")
        
    extracted_text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        with pdfplumber.open(temp_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except Exception as e:
        os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")
    
    os.unlink(temp_path)
    
    # Very basic deterministic parsing for MVP
    text_lower = extracted_text.lower()
    
    # Skill dictionary to check against
    common_skills = [
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust",
        "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi",
        "sql", "postgresql", "mysql", "mongodb", "redis", "aws", "azure", "gcp",
        "docker", "kubernetes", "git", "linux", "html", "css", "machine learning",
        "data analysis", "power bi", "tableau", "excel", "agile", "scrum"
    ]
    
    found_skills = []
    for skill in common_skills:
        # Simple word boundary check would be better, but simple inclusion for MVP prototype
        import re
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.append(skill.title())
            
    # Mocking experience extraction is prohibited, so we will try to find keywords or return empty
    # If we can't extract it reliably, return empty.
    
    return {
        "skills": found_skills,
        "experience": [],
        "education": [],
        "job_titles": [],
        "years_of_experience": None
    }
