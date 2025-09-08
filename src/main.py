"""Main entry point for DuelBot."""
import logging

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
