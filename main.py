import logging
import sys
from config.config import load_config
from core.account_manager import AccountManager
from core.bot_manager import BotManager

if __name__ == "__main__":
    # Configure logging for console output.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Load configuration from file.
    try:
        config = load_config("config/config.yaml")
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Initialize the account manager.
    account_manager = AccountManager(config.get("accounts", []))
    # Initialize BotManager to create one RedditBot per account.
    bot_manager = BotManager(config, account_manager)

    # Example usage:
    # Execute a "post" command for all bot instances.
    #bot_manager.execute_command_for_all("post")
    
    # To instruct a specific bot to reply to a submission, first obtain a submission object.
    # Example (this requires an actual submission object from Reddit):
    # submission = bot_manager.get_bots()[1].get_reddit().subreddit("example_subreddit1").new(limit=1).__next__()
    # Then instruct a specific bot (e.g., "bot_user_2") to reply:
    # bot_manager.execute_command_for_bot("bot_user_2", "reply", target=submission)
