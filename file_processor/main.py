"""
File Processor Service Main Entry Point
"""

from dotenv import load_dotenv
from consumer import start_consumer

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    print("Starting File Processor Service...")
    start_consumer()
