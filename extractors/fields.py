def extract_visa_requirements(jd_text):
    jd_lower = jd_text.lower()
    
    # Check for citizenship requirements
    citizenship_keywords = [
        'us citizen only',
        'citizenship required',
        'must be a us citizen',
        'us citizenship required',
        'requires us citizenship'
    ]
    if any(kw in jd_lower for kw in citizenship_keywords):
        return 'US Citizen only'
    
    # Check for green card requirements
    if 'green card' in jd_lower and 'required' in jd_lower:
        return 'Green Card required'
    
    # Check for ITAR
    itar_keywords = ['itar', 'export control', 'security clearance']
    if any(kw in jd_lower for kw in itar_keywords):
        return 'ITAR restricted'
    
    # Check for no sponsorship
    no_sponsor_keywords = [
        'no sponsorship',
        'no visa sponsorship',
        'not sponsor',
        'cannot sponsor'
    ]
    if any(kw in jd_lower for kw in no_sponsor_keywords):
        return 'No sponsorship'
    
    # Check for work authorization
    if 'work authorization' in jd_lower or 'authorized to work' in jd_lower:
        return 'Work authorization required'
    
    return 'Not specified'


def extract_education(jd_text):
    jd_lower = jd_text.lower()
    
    # Check for PhD
    if 'phd' in jd_lower or 'doctoral' in jd_lower or 'doctorate' in jd_lower:
        return 'PhD'
    
    # Check for Master's
    if "master's" in jd_lower or 'masters' in jd_lower or 'graduate' in jd_lower:
        return "Master's"
    
    # Check for Bachelor's
    if "bachelor's" in jd_lower or 'bachelors' in jd_lower or 'undergraduate' in jd_lower:
        return "Bachelor's"
    
    return 'Not specified'


def extract_work_mode(jd_text):
    jd_lower = jd_text.lower()
    
    # Check for remote
    if 'fully remote' in jd_lower or 'completely remote' in jd_lower:
        return 'Remote'
    
    if 'remote' in jd_lower and 'hybrid' not in jd_lower and 'not remote' not in jd_lower:
        return 'Remote'
    
    # Check for hybrid
    if 'hybrid' in jd_lower:
        return 'Hybrid'
    
    # Check for onsite
    onsite_keywords = ['onsite', 'on-site', 'in-office', 'in office']
    if any(kw in jd_lower for kw in onsite_keywords):
        return 'Onsite'
    
    return 'Not specified'


def extract_skills(jd_text):
    jd_lower = jd_text.lower()
    
    # Skill dictionary
    skill_keywords = {
        # Programming languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 
        'rust', 'swift', 'kotlin', 'ruby', 'php', 'scala',
        
        # ML/AI
        'pytorch', 'tensorflow', 'keras', 'scikit-learn', 'machine learning',
        'deep learning', 'neural networks', 'llm', 'transformers',
        
        # Web
        'react', 'vue', 'angular', 'node.js', 'django', 'flask', 'fastapi',
        'spring', 'express',
        
        # Data
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
        'spark', 'hadoop', 'kafka', 'airflow',
        
        # Cloud
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
        
        # Tools
        'git', 'linux', 'ci/cd', 'jenkins', 'github actions'
    }
    
    found_skills = []
    for skill in skill_keywords:
        if skill in jd_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicates

def extract_job_type(jd_text):
    jd_lower = jd_text.lower()
    
    # Check for intern
    if 'intern' in jd_lower or 'internship' in jd_lower:
        return 'Intern'
    
    # Check for full-time
    if 'full-time' in jd_lower or 'full time' in jd_lower or 'fulltime' in jd_lower:
        return 'Full-time'
    
    # Check for part-time
    if 'part-time' in jd_lower or 'part time' in jd_lower or 'parttime' in jd_lower:
        return 'Part-time'
    
    # Check for contract
    if 'contract' in jd_lower or 'contractor' in jd_lower:
        return 'Contract'
    
    # Check for temporary
    if 'temporary' in jd_lower or 'temp' in jd_lower:
        return 'Temporary'
    
    return 'Not specified'


def extract_experience_years(jd_text):ss
    import re
    jd_lower = jd_text.lower()
    
    # Pattern: "X+ years", "X-Y years", "X years"
    patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'(\d+)\s*-\s*(\d+)\s*years?',
        r'minimum\s+(\d+)\s*years?',
        r'at least\s+(\d+)\s*years?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, jd_lower)
        if match:
            if len(match.groups()) == 2:  # Range like "2-4 years"
                return f"{match.group(1)}-{match.group(2)} years"
            else:  # Single number
                return f"{match.group(1)}+ years"
    
    # Check for entry level
    if 'entry level' in jd_lower or 'entry-level' in jd_lower or '0 years' in jd_lower:
        return 'Entry level'
    
    return 'Not specified'