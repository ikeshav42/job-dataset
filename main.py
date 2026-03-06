import sys
import time
from scrapers.indeed_scraper import IndeedScraper
from extractors.llm_extractor import LLMExtractor
from database.supabase_client import supabase

def process_and_save_jobs(jobs, extractor, scraper):
    saved_count = 0
    duplicate_count = 0
    error_count = 0
    
    for i, job in enumerate(jobs, 1):
        try:
            print(f"\n[{i}/{len(jobs)}] Processing: {job['company']} - {job['job_title']}")
            
            fingerprint = scraper.generate_fingerprint(
                job['company'],
                job['job_title'],
                job['location']
            )
            
            existing = supabase.table('jobs').select('id').eq('fingerprint', fingerprint).execute()
            
            if existing.data:
                print(f"   ⊘ Duplicate (skipping - no API call)")
                duplicate_count += 1
                continue  # Save api call
            

            print(f"    Extracting fields with LLM...")
            start_time = time.time()
            extracted = extractor.extract_fields(job['job_description'])
            extraction_time = time.time() - start_time
            
            print(f"   ✓ Extraction complete ({extraction_time:.2f}s)")
            print(f"      Visa: {extracted['visa_requirements']}")
            print(f"      Education: {extracted['education_required']}")
            print(f"      Type: {extracted['job_type']} | Experience: {extracted['experience_years']}")
            print(f"      Skills: {', '.join(extracted['key_skills'][:5])}")
            
            job_data = {
                'fingerprint': fingerprint,
                'source': job['source'],
                'company': job['company'],
                'job_title': job['job_title'],
                'location': job['location'],
                'work_mode': extracted['work_mode'],
                'job_type': extracted['job_type'],
                'experience_years': extracted['experience_years'],
                'visa_requirements': extracted['visa_requirements'],
                'education_required': extracted['education_required'],
                'key_skills': extracted['key_skills'],
                'job_description': job['job_description'],
                'apply_url': job['apply_url'],
                'posted_date': job.get('posted_date', 'Not specified')
            }
            
            supabase.table('jobs').insert(job_data).execute()
            print(f"   💾 Saved to database")
            
            saved_count += 1
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            error_count += 1
            continue
    
    return saved_count, duplicate_count, error_count


def main():
    """Main entry point"""
    print("="*60)
    print("JOB DATASET SCRAPER (LLM-Powered)")
    print("="*60)
    
    # Initialize LLM extractor
    print("\n[Setup] Initializing LLM extractor...")
    extractor = LLMExtractor()
    
    # Test connection
    if not extractor.test_connection():
        print("\n❌ LLM API not available!")
        return
    
    # Initialize scraper
    scraper = IndeedScraper(headless=False)
    
    # Scrape jobs
    print("\n[1/2] Scraping Indeed...")
    jobs = scraper.scrape(
        query="software engineer intern",
        location="United States",
        days=1,
        max_jobs=10
    )
    
    print(f"\n✓ Scraped {len(jobs)} jobs")
    
    # Process and save (pass scraper to function)
    print("\n[2/2] Processing with LLM...")
    saved, duplicates, errors = process_and_save_jobs(jobs, extractor, scraper)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total scraped: {len(jobs)}")
    print(f"Saved:         {saved}")
    print(f"Duplicates:    {duplicates} (API calls saved! ✅)")
    print(f"Errors:        {errors}")
    print(f"API calls used: {saved + errors} (not {len(jobs)})")
    print("="*60)


if __name__ == "__main__":
    main()