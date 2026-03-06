from playwright.sync_api import sync_playwright
import time
from .base_scraper import BaseScraper

class IndeedScraper(BaseScraper):
    """Scraper for Indeed.com"""
    
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://www.indeed.com/jobs"
    
    def scrape(self, query="software engineer intern", location="United States", days=1, max_jobs=10):
        """
        Scrape jobs from Indeed
        
        Args:
            query: Job search query
            location: Job location
            days: Jobs posted in last N days (1 = last 24 hours)
            max_jobs: Maximum number of jobs to scrape
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        with sync_playwright() as p:
            # Launch browser with anti-detection
            browser = p.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = context.new_page()
            
            # Build search URL
            url = f"{self.base_url}?q={query.replace(' ', '+')}&l={location.replace(' ', '+')}&fromage={days}&sort=date"
            
            print(f"Scraping Indeed: {url}")
            page.goto(url, wait_until='load')
            time.sleep(3)
            
            # Wait for job cards
            try:
                page.wait_for_selector('.job_seen_beacon', timeout=10000)
            except:
                print("No jobs found or page didn't load")
                browser.close()
                return jobs
            
            # Get all job cards
            job_cards = page.query_selector_all('.job_seen_beacon')
            print(f"Found {len(job_cards)} job cards")
            
            # Scrape each job
            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    # Extract basic info from card
                    title_elem = card.query_selector('h2.jobTitle a')
                    company_elem = card.query_selector('[data-testid="company-name"]')
                    location_elem = card.query_selector('[data-testid="text-location"]')
                    
                    if not title_elem or not company_elem:
                        continue
                    
                    job_title = title_elem.inner_text()
                    company = company_elem.inner_text()
                    
                    if location_elem:
                        location_raw = location_elem.inner_text()
                        location = location_raw.replace('Remote in ', '').replace('Hybrid work in ', '').replace('Onsite in ', '').strip()
                    else:
                        location = "Not specified"
                    
                    job_url = f"https://www.indeed.com{title_elem.get_attribute('href')}"
                    
                    # Filter: US only
                    if not self.is_us_location(location):
                        print(f"Skipping non-US job: {location}")
                        continue
                    
                    print(f"{i+1}. {company} - {job_title}")
                    
                    # Click to load description
                    title_elem.scroll_into_view_if_needed()
                    time.sleep(1)
                    title_elem.click()
                    time.sleep(2)
                    
                    # Extract full description
                    desc_elem = page.query_selector('#jobDescriptionText')
                    description = desc_elem.inner_text() if desc_elem else ""
                    
                    if not description:
                        print(f"   No description found, skipping")
                        continue
                    
                    # Create job object
                    job = {
                        'source': 'indeed',
                        'company': company,
                        'job_title': job_title,
                        'location': location,
                        'job_description': description,
                        'apply_url': job_url,
                        'posted_date': 'Last 24 hours'  # Indeed doesn't show exact date for fresh jobs
                    }
                    
                    jobs.append(job)
                    print(f"   ✓ Scraped successfully")
                    
                    time.sleep(2)  # Be nice to Indeed
                    
                except Exception as e:
                    print(f"   Error scraping job: {e}")
                    continue
            
            browser.close()
        
        return jobs