import sys
import time
import json
from scrapers.indeed_scraper import IndeedScraper
from extractors.llm_extractor import LLMExtractor
from database.supabase_client import supabase

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(" config.json not found!")
        sys.exit(1)
    except json.JSONDecodeError:
        print("config.json is not valid JSON!")
        sys.exit(1)


def main():
    """Main entry point"""
    print("="*60)
    print("JOB DATASET SCRAPER (LLM-Powered)")
    print("="*60)
    
    config = load_config()
    
    print("\n[Setup] Initializing LLM extractor...")
    extractor = LLMExtractor(model_name=config['llm']['model'])
    
    if not extractor.test_connection():
        print("\nLLM API not available!")
        return
    
    print("[Setup] Initializing scraper...")
    scraper = IndeedScraper(headless=config['scraper']['headless'])
    
    saved_count = 0
    duplicate_count = 0
    error_count = 0
    
    print(f"\n[Starting] Scraping and processing up to {config['scraper']['max_jobs']} jobs...")
    print(f"Query: {config['scraper']['search_query']}")
    print(f"Location: {config['scraper']['search_location']}\n")
    
    for job_num, job in enumerate(scraper.scrape_generator(
        query=config['scraper']['search_query'],
        location=config['scraper']['search_location'],
        days=config['scraper']['search_days'],
        max_jobs=config['scraper']['max_jobs'],
        config=config
    ), 1):
        try:
            print(f"[{job_num}] {job['company']} - {job['job_title']}")
            
            fingerprint = scraper.generate_fingerprint(
                job['company'],
                job['job_title'],
                job['location']
            )
            
            existing = supabase.table(config['database']['table_name']).select('id').eq('fingerprint', fingerprint).execute()
            
            if existing.data:
                print(f"   Duplicate (skipping)")
                duplicate_count += 1
                continue
            
            print(f"   Analyzing with LLM...")
            start_time = time.time()
            extracted = extractor.extract_fields(job['job_description'])
            extraction_time = time.time() - start_time
            
            print(f"   ✓ Done ({extraction_time:.2f}s) | Visa: {extracted['visa_requirements']} | Type: {extracted['job_type']}")
            
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
            
            supabase.table(config['database']['table_name']).insert(job_data).execute()
            print(f"   💾 Saved\n")
            
            saved_count += 1
            
        except Exception as e:
            print(f"   ✗ Error: {e}\n")
            error_count += 1
            continue
    
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Saved:      {saved_count}")
    print(f"Duplicates: {duplicate_count}")
    print(f"Errors:     {error_count}")
    print(f"Total:      {saved_count + duplicate_count + error_count}")
    print("="*60)


if __name__ == "__main__":
    main()