import os

from dotenv import load_dotenv

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker


# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------
load_dotenv()


# -----------------------------------
# DATABASE URL
# -----------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


# -----------------------------------
# DATABASE ENGINE
# -----------------------------------
if DATABASE_URL.startswith("sqlite"):

    engine = create_engine(

        DATABASE_URL,

        connect_args={
            "check_same_thread": False
        }
    )

else:

    engine = create_engine(
        DATABASE_URL
    )


# -----------------------------------
# SESSION
# -----------------------------------
SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine
)

print("DATABASE_URL =", DATABASE_URL)