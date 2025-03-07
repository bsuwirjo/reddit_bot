import pytest
from core.account_manager import AccountManager

# Create dummy Reddit objects for testing.
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

def test_account_manager():
    accounts = [
        {"username": "user1", "password": "pass", "client_id": "cid1", "client_secret": "csecret1", "user_agent": "agent1"},
        {"username": "user2", "password": "pass", "client_id": "cid2", "client_secret": "csecret2", "user_agent": "agent2"}
    ]
    am = AccountManager(accounts)
    # Override the reddit_instances with dummy instances.
    am.reddit_instances = [DummyReddit("user1"), DummyReddit("user2")]
    first = am.get_next_account()
    second = am.get_next_account()
    third = am.get_next_account()
    assert first.username == "user1"
    assert second.username == "user2"
    assert third.username == "user1"
