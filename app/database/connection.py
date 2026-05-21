import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------
load_dotenv()

# -----------------------------------
# DATABASE URL
# -----------------------------------
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    raise ValueError("SUPABASE_DB_URL is not set in .env")



# -----------------------------------
# DATABASE ENGINE
# -----------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # keeps connection alive
)

# -----------------------------------
# SESSION
# -----------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -----------------------------------
# TEST CONNECTION FUNCTION
# -----------------------------------
def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful:", result.fetchone())

    except Exception as e:
        print("❌ Database connection failed:")
        print(str(e))


# -----------------------------------
# RUN TEST (optional)
# -----------------------------------
if __name__ == "__main__":
    test_connection()