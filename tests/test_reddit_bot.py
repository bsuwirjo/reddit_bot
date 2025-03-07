import pytest
from bots.reddit_bot import RedditBot

# Dummy content provider for testing.
class DummyContentProvider:
    def generate_post_content(self):
        return ("Dummy Title", "Dummy Body")
    def generate_reply_content(self, target, chain_index):
        return "Dummy Reply"

# Dummy Reddit and related classes.
class DummyReddit:
    def __init__(self, username):
        self.username = username
    def subreddit(self, name):
        return DummySubreddit(name)
    @property
    def user(self):
        return self
    def me(self):
        return self.username

class DummySubreddit:
    def __init__(self, name):
        self.name = name
    def submit(self, title, selftext):
        return DummySubmission(title, selftext)

class DummySubmission:
    def __init__(self, title, selftext):
        self.title = title
        self.selftext = selftext
        self.id = "dummy_id"
    def reply(self, text):
        return DummyComment(text)

class DummyComment:
    def __init__(self, text):
        self.text = text
        self.id = "dummy_comment_id"

class DummyAccountManager:
    def get_next_account(self):
        return DummyReddit("dummy_user")

def test_reddit_bot_post(monkeypatch):
    dummy_am = DummyAccountManager()
    config = {"subreddits": ["dummy_subreddit"], "replies": {"chain_length": 1}}
    content_provider = DummyContentProvider()
    dummy_reddit = DummyReddit("dummy_user")
    bot = RedditBot(dummy_am, config, content_provider=content_provider, reddit_instance=dummy_reddit, username="dummy_user")
    
    submitted = []
    # Override submit method on DummySubreddit to capture submission data.
    def dummy_submit(self, title, selftext):
        submitted.append((title, selftext))
        return DummySubmission(title, selftext)
    monkeypatch.setattr(DummySubreddit, "submit", dummy_submit)
    
    bot.post()
    assert submitted[0] == ("Dummy Title", "Dummy Body")

def test_reddit_bot_reply(monkeypatch):
    dummy_am = DummyAccountManager()
    config = {"subreddits": ["dummy_subreddit"], "replies": {"chain_length": 1}}
    content_provider = DummyContentProvider()
    dummy_reddit = DummyReddit("dummy_user")
    bot = RedditBot(dummy_am, config, content_provider=content_provider, reddit_instance=dummy_reddit, username="dummy_user")
    
    submission = DummySubmission("Test Title", "Test Body")
    replied = []
    def dummy_reply(text):
        replied.append(text)
        return DummyComment(text)
    monkeypatch.setattr(submission, "reply", dummy_reply)
    bot.reply(submission)
    assert replied[0] == "Dummy Reply"
