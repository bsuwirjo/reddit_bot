import praw
import logging
import threading

class AccountManager:
    def __init__(self, accounts):
        """
        Initialize multiple Reddit account instances using PRAW.
        """
        self.reddit_instances = []
        self._lock = threading.Lock()  # Remove if running strictly single-threaded.
        self.current_index = 0

        for acc in accounts:
            reddit = praw.Reddit(
                client_id=acc.get("client_id"),
                client_secret=acc.get("client_secret"),
                username=acc.get("username"),
                password=acc.get("password"),
                user_agent=acc.get("user_agent", "MultiAccountBot")
            )
            self.reddit_instances.append(reddit)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initialized {len(self.reddit_instances)} Reddit account(s).")

    def get_next_account(self):
        """
        Retrieve the next Reddit instance in a round-robin fashion.
        """
        with self._lock:
            if not self.reddit_instances:
                raise Exception("No Reddit accounts available")
            reddit = self.reddit_instances[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.reddit_instances)
            return reddit
