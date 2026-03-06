from playwright.sync_api import sync_playwright
import time
from .base_scraper import BaseScraper

class IndeedScraper(BaseScraper):
    
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://www.indeed.com/jobs"
    
    def scrape_generator(self, query="software engineer intern", location="United States", days=1, max_jobs=10, config=None):
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = context.new_page()
            
            url = f"{self.base_url}?q={query.replace(' ', '+')}&l={location.replace(' ', '+')}&fromage={days}&sort=date"
            
            page.goto(url, wait_until='load')
            time.sleep(3)
            
            try:
                page.wait_for_selector('.job_seen_beacon', timeout=10000)
            except:
                browser.close()
                return
            
            jobs_collected = 0
            processed_jobs = set()
            
            blacklist = config.get('scraper', {}).get('blacklist_keywords', []) if config else []
            
            job_cards = page.query_selector_all('.job_seen_beacon')
            
            for card in job_cards:
                if jobs_collected >= max_jobs:
                    break
                
                try:
                    title_elem = card.query_selector('h2.jobTitle a')
                    company_elem = card.query_selector('[data-testid="company-name"]')
                    location_elem = card.query_selector('[data-testid="text-location"]')
                    
                    if not (title_elem and company_elem):
                        continue
                    
                    job_title = title_elem.inner_text().strip()
                    company = company_elem.inner_text().strip()
                    
                    if blacklist:
                        job_title_lower = job_title.lower()
                        if any(keyword in job_title_lower for keyword in blacklist):
                            continue
                    
                    job_id = f"{company}|{job_title}"
                    
                    if job_id in processed_jobs:
                        continue
                    
                    processed_jobs.add(job_id)
                    
                    if location_elem:
                        job_location = location_elem.inner_text().strip()
                        job_location = job_location.replace("Remote in ", "").replace("Hybrid work in ", "").replace("Onsite in ", "")
                    else:
                        job_location = "Not specified"
                    
                    if not self.is_us_location(job_location):
                        continue
                    
                    job_url = f"https://www.indeed.com{title_elem.get_attribute('href')}"
                    
                    title_elem.scroll_into_view_if_needed()
                    time.sleep(1)
                    title_elem.click()
                    time.sleep(2)
                    
                    desc_elem = page.query_selector('#jobDescriptionText')
                    description = desc_elem.inner_text() if desc_elem else ""
                    
                    if not description:
                        continue
                    
                    job_data = {
                        'source': 'indeed',
                        'company': company,
                        'job_title': job_title,
                        'location': job_location,
                        'job_description': description,
                        'apply_url': job_url,
                        'posted_date': f'Last {days} day{"s" if days > 1 else ""}'
                    }
                    
                    jobs_collected += 1
                    yield job_data
                    
                    time.sleep(2)
                    
                except Exception as e:
                    continue
            
            browser.close()