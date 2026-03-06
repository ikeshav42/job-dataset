import json
import os
from typing import Dict
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class LLMExtractor:
    
    def __init__(self, model_name: str = "gemini-3.1-flash-lite-preview"):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
    
    def extract_fields(self, job_description: str) -> Dict:
        
        # Find requirements section
        jd_lower = job_description.lower()
        
        # Comprehensive markers for requirements section
        requirement_markers = [
            'requirements:', 'qualifications:', 'required:', 'what you will have:',
            'the essentials', 'minimum qualifications', 'you must', 'legal authorization',
            'work authorization', 'sponsorship', 'eligibility', 'visa', 'citizen',
            'must have:', 'required skills:', 'basic qualifications:', 'preferred qualifications:',
            'what we are looking for:', 'what you bring:', 'about you:'
        ]
        
        req_start = len(job_description)
        for marker in requirement_markers:
            pos = jd_lower.find(marker)
            if pos != -1 and pos < req_start:
                req_start = pos
        
        if len(job_description) > 8000:
            if req_start < len(job_description):
                # Strategy - intro (2000) + COMPLETE requirements section (6000 chars)
                focused_desc = (
                    job_description[:2000] + 
                    "\n\n[...MIDDLE SECTION OMITTED FOR BREVITY...]\n\n" + 
                    job_description[req_start:req_start+6000]
                )
            else:
                # Fallback first 4000 + last 4000
                focused_desc = (
                    job_description[:4000] + 
                    "\n\n[...MIDDLE SECTION OMITTED...]\n\n" + 
                    job_description[-4000:]
                )
        else:
            # Use complete description
            focused_desc = job_description
        
        prompt = f"""You are a professional job description analyzer. Your task is to extract specific information with HIGH ACCURACY.

    Read the ENTIRE job description below CAREFULLY. Pay special attention to sections about requirements, qualifications, work authorization, and employment details.

    === JOB DESCRIPTION START ===
    {focused_desc}
    === JOB DESCRIPTION END ===

    TASK: Extract the following information and return ONLY a valid JSON object (no markdown, no explanation, no preamble):

    {{
    "visa_requirements": "<value>",
    "education_required": "<value>",
    "work_mode": "<value>",
    "job_type": "<value>",
    "experience_years": "<value>",
    "key_skills": ["skill1", "skill2", "skill3"]
    }}

    DETAILED EXTRACTION GUIDELINES:

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. VISA_REQUIREMENTS (CRITICAL - Read the ENTIRE description for this):
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Look for ANY of these phrases (often appears near the END of job descriptions):

    → "No sponsorship" IF you find:
    - "will not sponsor", "not sponsor", "no sponsorship"
    - "cannot sponsor", "unable to sponsor"
    - "sponsorship not available", "no visa sponsorship"
    - "This includes OPT/CPT/STEM visas" (often follows no sponsorship statement)

    → "US Citizen only" IF you find:
    - "US citizen only", "US citizenship required"
    - "must be a US citizen", "requires US citizenship"
    - "ITAR", "security clearance", "export control"

    → "Green Card required" IF you find:
    - "green card required", "permanent resident"

    → "Work authorization required" IF you find:
    - "must be authorized to work", "work authorization required"
    - "legal authorization to work", "authorized to work in the US"
    - "CPT" (Curricular Practical Training for students)
    - BUT NOT if it also says "no sponsorship" (then use "No sponsorship")

    → "Not specified" IF NONE of the above phrases appear

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    2. EDUCATION_REQUIRED:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    → "PhD" IF: "PhD", "doctoral", "doctorate"
    → "Master's" IF: "master's", "masters", "MS degree", "graduate degree", "advanced degree"
    → "Bachelor's" IF: "bachelor's", "bachelors", "BS degree", "undergraduate", 
                    "pursuing a degree", "enrolled in", "currently pursuing"
    → "Not specified" IF: no degree mentioned

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    3. WORK_MODE:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    → "Remote" IF: "remote", "work from home", "work from anywhere", "fully remote"
    → "Hybrid" IF: "hybrid", "X days on-site", "X days in office", "flexible location"
    → "Onsite" IF: "onsite", "on-site", "in office", "in-person", "in person",
                "required X times per week", "must work on site"
    → "Not specified" IF: no work location mentioned

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    4. JOB_TYPE:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    → "Intern" IF: "intern", "internship", "co-op", "co op"
    → "Full-time" IF: "full-time", "full time", "fulltime"
    → "Part-time" IF: "part-time", "part time", "parttime"
    → "Contract" IF: "contract", "contractor", "1099", "temporary", "temp"
    → "Not specified" IF: no employment type mentioned

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    5. EXPERIENCE_YEARS:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    → "Entry level" IF: "entry level", "0 years", "new grad", "no experience required",
                        "intern", "internship" (if job_type is Intern)
    → "1-3" IF: "1-3 years", "1+ years", "2 years", "1 to 3 years"
    → "3-5" IF: "3-5 years", "3+ years", "4 years", "3 to 5 years"
    → "5+" IF: "5+ years", "4+ years", "more than 5 years", "6 years"
    → "Not specified" IF: no experience mentioned

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    6. KEY_SKILLS (Extract 5-10 technical skills):
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Extract: programming languages, frameworks, tools, databases, platforms
    Examples: "python", "java", "react", "aws", "docker", "sql", "git"
    Return as lowercase array of 5-10 most important skills

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    IMPORTANT REMINDERS:
    ✓ Read the COMPLETE job description before answering
    ✓ Visa/sponsorship info is usually at the END - don't miss it!
    ✓ Return ONLY the JSON object, nothing else
    ✓ Use EXACT values specified above (case-sensitive)

    Your JSON response:"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0, 
                    max_output_tokens=800,  
                    top_k=1, 
                    top_p=0.95, 
                )
            )
            
            # Parse response
            text = response.text.strip()
            
            # Remove markdown code blocks if present
            text = text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            extracted = json.loads(text)
            
            # Validate
            return self._validate_extraction(extracted)
            
        except Exception as e:
            print(f"   Error with Gemini: {e}")
            return self._get_default_fields()
    
    def _validate_extraction(self, data: Dict) -> Dict:
        """Validate extracted data"""
        
        valid_visa = ["US Citizen only", "Green Card required", "No sponsorship", 
                      "Work authorization required", "Not specified"]
        valid_education = ["PhD", "Master's", "Bachelor's", "Not specified"]
        valid_work_mode = ["Remote", "Hybrid", "Onsite", "Not specified"]
        valid_job_type = ["Intern", "Full-time", "Part-time", "Contract", "Not specified"]
        valid_experience = ["Entry level", "1-3", "3-5", "5+", "Not specified"]
        
        validated = {}
        
        validated['visa_requirements'] = data.get('visa_requirements', 'Not specified')
        if validated['visa_requirements'] not in valid_visa:
            validated['visa_requirements'] = 'Not specified'
        
        validated['education_required'] = data.get('education_required', 'Not specified')
        if validated['education_required'] not in valid_education:
            validated['education_required'] = 'Not specified'
        
        validated['work_mode'] = data.get('work_mode', 'Not specified')
        if validated['work_mode'] not in valid_work_mode:
            validated['work_mode'] = 'Not specified'
        
        validated['job_type'] = data.get('job_type', 'Not specified')
        if validated['job_type'] not in valid_job_type:
            validated['job_type'] = 'Not specified'
        
        validated['experience_years'] = data.get('experience_years', 'Not specified')
        if validated['experience_years'] not in valid_experience:
            validated['experience_years'] = 'Not specified'
        
        skills = data.get('key_skills', [])
        if isinstance(skills, list):
            validated['key_skills'] = [str(s).lower() for s in skills[:10]]
        else:
            validated['key_skills'] = []
        
        return validated
    
    def _get_default_fields(self) -> Dict:
        return {
            'visa_requirements': 'Not specified',
            'education_required': 'Not specified',
            'work_mode': 'Not specified',
            'job_type': 'Not specified',
            'experience_years': 'Not specified',
            'key_skills': []
        }
    
    def test_connection(self) -> bool:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Say 'OK'"
            )
            print(f"Gemini API connected successfully (model: {self.model_name})")
            return True
        except Exception as e:
            print(f" Gemini API error: {e}")
            return False

#test
if __name__ == "__main__":
    extractor = LLMExtractor()
    
    if not extractor.test_connection():
        print("\nMake sure GEMINI_API_KEY is set in .env file")
        exit(1)
    
    sample = """
    Software Engineering Intern - Summer 2026
    
    Requirements:
    - Bachelor's in Computer Science
    - Python, JavaScript, React
    - Must be authorized to work in US (no sponsorship)
    - 0-1 years experience
    
    Remote position.
    """
    
    result = extractor.extract_fields(sample)
    print("\nTest extraction:")
    print(json.dumps(result, indent=2))