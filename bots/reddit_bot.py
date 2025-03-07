import logging

class RedditBot:
    def __init__(self, account_manager, config, content_provider=None, reddit_instance=None, username=None):
        """
        RedditBot that can post and reply on Reddit.
        
        Parameters:
            account_manager: An instance of AccountManager.
            config: The configuration dictionary.
            content_provider: An optional content provider (e.g., OpenAIProvider) for generating posts/replies.
            reddit_instance: A dedicated Reddit instance for this bot/account.
            username: The Reddit account's username.
        """
        self.account_manager = account_manager
        self.config = config
        self.content_provider = content_provider
        self.reddit = reddit_instance
        self.username = username
        self.logger = logging.getLogger(self.__class__.__name__)
        self.subreddits = config.get("subreddits", [])
        self.chain_length = config.get("replies", {}).get("chain_length", 1)

    def get_reddit(self):
        """
        Retrieve the dedicated Reddit instance if available; otherwise, get the next available one.
        """
        if self.reddit is not None:
            return self.reddit
        return self.account_manager.get_next_account()

    def generate_post_content(self):
        """
        Generate a post's title and body using the content provider.
        """
        if self.content_provider:
            return self.content_provider.generate_post_content()
        return ("Default Title", "Default content body.")

    def generate_reply_content(self, target, chain_index=0):
        """
        Generate reply text for the given target using the content provider.
        """
        if self.content_provider:
            return self.content_provider.generate_reply_content(target, chain_index)
        return f"Default reply #{chain_index+1}"

    def post(self):
        """
        Create a new post in each configured subreddit.
        """
        title, body = self.generate_post_content()
        if not self.subreddits:
            self.logger.warning("No subreddits configured.")
            return

        reddit = self.get_reddit()
        for sub in self.subreddits:
            try:
                subreddit = reddit.subreddit(sub)
                submission = subreddit.submit(title=title, selftext=body)
                self.logger.info(
                    f"Posted to r/{sub} using account {reddit.user.me()} (Submission ID: {submission.id})"
                )
            except Exception as e:
                self.logger.error(f"Error posting to r/{sub}: {e}")

    def reply(self, submission):
        """
        Reply to a given submission or comment.
        
        Parameters:
            submission: A Reddit submission or comment object to reply to.
        """
        reddit = self.get_reddit()
        try:
            reply_text = self.generate_reply_content(submission, 0)
            comment = submission.reply(reply_text)
            self.logger.info(
                f"Replied to submission {submission.id} with comment {comment.id} using account {reddit.user.me()}"
            )
        except Exception as e:
            self.logger.error(f"Error replying to submission {submission.id}: {e}")

    def handle_command(self, command, target=None):
        """
        Handle a command ("post" or "reply").
        
        Parameters:
            command: Command string ("post" or "reply").
            target: For "reply", a Reddit submission or comment to reply to.
        """
        if command.lower() == "post":
            self.post()
        elif command.lower() == "reply":
            if target is not None:
                self.reply(target)
            else:
                self.logger.error("No target provided for reply command.")
        else:
            self.logger.error(f"Unknown command: {command}")

    def learn_and_post(self, subreddit_name):
        """
        Learn about a subreddit by reading the first 5 posts and their top-level comments,
        then generate and post content that reflects the style of the subreddit combined with
        the bot's own personality.
        
        Parameters:
            subreddit_name: The name of the subreddit to learn from.
        """
        reddit = self.get_reddit()
        subreddit = reddit.subreddit(subreddit_name)
        learned_context = ""
        try:
            for submission in subreddit.new(limit=5):
                learned_context += f"Post Title: {submission.title}\nPost Body: {submission.selftext}\n"
                submission.comments.replace_more(limit=0)
                for comment in submission.comments:
                    learned_context += f"Comment: {comment.body}\n"
                learned_context += "\n"
        except Exception as e:
            self.logger.error(f"Error learning from subreddit {subreddit_name}: {e}")
            return

        if self.content_provider:
            title, body = self.content_provider.generate_post_content(learned_context=learned_context)
            try:
                new_submission = subreddit.submit(title=title, selftext=body)
                self.logger.info(
                    f"Learned and posted to r/{subreddit_name} using account {reddit.user.me()} (Submission ID: {new_submission.id})"
                )
            except Exception as e:
                self.logger.error(f"Error posting to r/{subreddit_name}: {e}")
        else:
            self.logger.error("No content provider available for generating post content.")
