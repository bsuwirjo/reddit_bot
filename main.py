import logging
import sys
from config.config import load_config
from core.account_manager import AccountManager
from core.bot_manager import BotManager

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    try:
        config = load_config("config/config.yaml")
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    account_manager = AccountManager(config.get("accounts", []))
    bot_manager = BotManager(config, account_manager)
    
    # Define the subreddit to learn from.
    learn_subreddit = "DnDGreentext"
    
    bots = bot_manager.get_bots()
    if bots:
        bots[0].learn_and_post(learn_subreddit)
    else:
        logging.error("No bots available.")
