import logging
from bots.reddit_bot import RedditBot
from providers.openai_provider import OpenAIProvider

class BotManager:
    def __init__(self, config, account_manager):
        """
        BotManager instantiates one RedditBot per account,
        each with its unique personality and knowledge.
        """
        self.config = config
        self.account_manager = account_manager
        self.bots = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialize_bots()

    def _initialize_bots(self):
        accounts = self.config.get("accounts", [])
        personalities = self.config.get("personalities", {})
        openai_config = self.config.get("openai", {})
        post_prompt = openai_config.get("post_prompt")
        reply_prompt = openai_config.get("reply_prompt")
        openai_api_key = self.config.get("openai_api_key", None)

        for i, acc in enumerate(accounts):
            username = acc.get("username")
            # Get personality for this account using the username as key.
            personality_info = personalities.get(username, {"description": "", "memory": ""})
            personality = personality_info.get("description", "")
            memory = personality_info.get("memory", "")

            content_provider = None
            if openai_api_key:
                content_provider = OpenAIProvider(
                    openai_api_key,
                    post_prompt=post_prompt,
                    reply_prompt=reply_prompt,
                    personality=personality,
                    memory=memory
                )
            # Use the dedicated Reddit instance from the account manager.
            reddit_instance = self.account_manager.reddit_instances[i]
            bot = RedditBot(self.account_manager, self.config, content_provider=content_provider,
                            reddit_instance=reddit_instance, username=username)
            self.bots.append(bot)
            self.logger.info(f"Initialized RedditBot for account: {username}")

    def get_bots(self):
        return self.bots

    def execute_command_for_all(self, command, target=None):
        """
        Execute a command ("post" or "reply") for all instantiated bots.
        """
        for bot in self.bots:
            bot.handle_command(command, target)

    def execute_command_for_bot(self, bot_username, command, target=None):
        """
        Execute a command ("post" or "reply") for a specific bot identified by its username.
        
        Parameters:
            bot_username: The username of the bot to target.
            command: The command string ("post" or "reply").
            target: For "reply", a Reddit submission or comment object to reply to.
        """
        found = False
        for bot in self.bots:
            if bot.username == bot_username:
                bot.handle_command(command, target)
                self.logger.info(f"Executed command '{command}' for bot: {bot_username}")
                found = True
                break
        if not found:
            self.logger.error(f"No bot found for username: {bot_username}")
