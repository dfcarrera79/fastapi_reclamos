import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
db_uri1 = os.getenv("DB_URI1")
db_uri2 = os.getenv("DB_URI2")