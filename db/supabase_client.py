import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from the .env file
load_dotenv()

def get_supabase_client() -> Client:
    """Initializes and returns an authenticated Supabase client."""
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env file.")
        
    return create_client(url, key)

# Optional quick test
if __name__ == "__main__":
    try:
        client = get_supabase_client()
        print("✅ Supabase client initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize Supabase: {e}")