import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def test_connection():
    result = supabase.table('jobs').select('*').limit(1).execute()
    print(f"✓ Connected to Supabase! Rows: {len(result.data)}")

if __name__ == "__main__":
    test_connection()
