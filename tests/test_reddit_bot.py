import pytest
from bots.reddit_bot import RedditBot

# Dummy content provider for testing.
class DummyContentProvider:
    def generate_post_content(self, learned_context=None):
        if learned_context:
            return ("Learned Title", f"Learned Body with context: {learned_context}")
        return ("Dummy Title", "Dummy Body")
    def generate_reply_content(self, target, chain_index):
        return "Dummy Reply"

# Dummy classes to simulate Reddit API objects.
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
    def new(self, limit):
        return [DummySubmission(f"Post {i} Title", f"Post {i} Body") for i in range(1, limit+1)]
    def submit(self, title, selftext):
        return DummySubmission(title, selftext)

class DummySubmission:
    def __init__(self, title, selftext):
        self.title = title
        self.selftext = selftext
        self.id = "dummy_id"
        self.comments = DummyCommentForest()
    def reply(self, text):
        return DummyComment(text)

class DummyComment:
    def __init__(self, text):
        self.body = text
        self.id = "dummy_comment_id"

class DummyCommentForest:
    def __init__(self):
        self.comments = [DummyComment("Comment 1 Body"), DummyComment("Comment 2 Body")]
    def replace_more(self, limit):
        pass
    def __iter__(self):
        return iter(self.comments)

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

def test_reddit_bot_learn_and_post(monkeypatch):
    dummy_am = DummyAccountManager()
    config = {"replies": {"chain_length": 1}}
    content_provider = DummyContentProvider()
    dummy_reddit = DummyReddit("dummy_user")
    bot = RedditBot(dummy_am, config, content_provider=content_provider, reddit_instance=dummy_reddit, username="dummy_user")
    
    submissions = []
    def dummy_submit(self, title, selftext):
        submissions.append((title, selftext))
        return DummySubmission(title, selftext)
    monkeypatch.setattr(DummySubreddit, "submit", dummy_submit)
    
    bot.learn_and_post("dummy_subreddit")
    
    assert len(submissions) == 1
    title, body = submissions[0]
    assert title == "Learned Title"
    assert "Learned Body with context:" in body
    assert "Post 1 Title" in body
    assert "Comment 1 Body" in body
