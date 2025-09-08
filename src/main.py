"""Main entry point for DuelBot."""
import logging
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import DuelBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main function to run the bot."""
    bot = DuelBot()
    bot.run()

if __name__ == "__main__":
    main()
