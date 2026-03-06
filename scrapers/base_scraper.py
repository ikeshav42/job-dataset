import hashlib
from datetime import datetime, timedelta

class BaseScraper:
    """Base class for all job site scrapers"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.us_states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]
    
    def generate_fingerprint(self, company, title, location):
        #Normalize company (remove common suffixes, lowercase, strip)
        company_clean = company.lower().strip()
        company_clean = company_clean.replace('inc.', '').replace('llc', '')
        company_clean = company_clean.replace(',', '').replace('.', '').strip()
        
        # Normalize title (lowercase, strip)
        title_clean = title.lower().strip()
        
        #Normalize location (lowercase, strip)
        location_clean = location.lower().strip()
        
        # Create fingerprint string
        fingerprint_str = f"{company_clean}|{title_clean}|{location_clean}"
        
        # Generate MD5 hash
        return hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    def is_us_location(self, location):
        location_upper = location.upper()
        
        # Check for state codes
        for state in self.us_states:
            if state in location_upper:
                return True
        
        # Check for common keywords
        us_keywords = ['REMOTE', 'UNITED STATES', 'USA', 'U.S.']
        if any(keyword in location_upper for keyword in us_keywords):
            return True
        
        return False
    
    def scrape(self):
        #Override this method in child classes
        raise NotImplementedError("Child class must implement scrape()")