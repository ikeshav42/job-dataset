# Job Dataset Scraper

ETL pipeline that scrapes tech internship postings from Indeed, extracts structured fields using Google Gemini AI, and stores them in PostgreSQL.

## Why

I'm an MS CS student at UT Arlington (graduating May 2027) looking for Summer 2026 internships. I built this to:

- Learn ETL pipeline design
- Understand the chaotic job market (trends, visa policies, skill demands)
- Stop reading hundreds of lengthy job descriptions manually
- Find visa-friendly opportunities faster

## What It Does

**Extract:** Scrapes Indeed for internship postings

**Transform:** Google Gemini API extracts:
- Visa requirements
- Education requirements  
- Work mode (Remote/Hybrid/Onsite)
- Skills
- Experience level

**Load:** Saves to Supabase (PostgreSQL) with deduplication

## Tech Stack

Python 3.11 • Playwright • Google Gemini API • Supabase

## Database Schema

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| fingerprint | TEXT | Unique hash (company + title + location) |
| scraped_at | TIMESTAMP | When scraped |
| source | TEXT | Job board ("indeed") |
| company | TEXT | Company name |
| job_title | TEXT | Job title |
| location | TEXT | Location |
| job_description | TEXT | Full description |
| apply_url | TEXT | Application URL |
| posted_date | TEXT | When posted |
| work_mode | TEXT | Remote/Hybrid/Onsite |
| visa_requirements | TEXT | Sponsorship status |
| education_required | TEXT | Degree level |
| job_type | TEXT | Intern/Full-time/etc |
| experience_years | TEXT | Experience level |
| key_skills | TEXT[] | Extracted skills |

## Setup
```bash
# Install
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install

# Configure
# 1. Create Supabase account, run database/schema.sql
# 2. Get Gemini API key from https://aistudio.google.com (free: 500 req/day)
# 3. Create .env file:
GEMINI_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_KEY=your_key

# 4. Edit config.json for search query and filters

# Run
python3 main.py
```

## Configuration

Edit `config.json`:
```json
{
  "scraper": {
    "search_query": "software intern summer 2026",
    "search_days": 7,
    "max_jobs": 50,
    "blacklist_keywords": ["sales", "marketing", "finance"]
  }
}
```

**Known Bug:** `max_jobs` currently limited to jobs on first page. Pagination disabled.

## Performance

- 6-10 seconds per job
- ~500 requests/day (Gemini free tier)
- 85-100% extraction accuracy
- Blacklist filtering before API call

## Legal Disclaimer

**Educational and personal use only.**

May violate Indeed's Terms of Service. You are responsible for legal compliance.

**Do NOT:**
- Publish or sell scraped data
- Use commercially
- Share personal information from postings

Respect GDPR/CCPA. Keep data private. Use responsibly.

**By using this tool, you accept all legal responsibility.**

## What I Learned

- ETL pipeline design
- LLM prompt engineering
- API rate limit management
- Database deduplication
- Web scraping anti-bot measures

## Roadmap

- Fix pagination for 50+ jobs
- LinkedIn/Glassdoor scrapers
- Analytics dashboard
- Trend analysis blog posts

## Author

Keshav Sundararaman - MS CS @ UT Arlington

## License

MIT