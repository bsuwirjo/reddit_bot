import pytest
from core.bot_manager import BotManager
from core.account_manager import AccountManager

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

# Dummy AccountManager that returns dummy Reddit instances.
class DummyAccountManager:
    def __init__(self):
        self.reddit_instances = [DummyReddit("bot_user_1"), DummyReddit("bot_user_2")]
    def get_next_account(self):
        return self.reddit_instances[0]

def test_bot_manager_initialization():
    # Create a dummy config.
    config = {
        "accounts": [
            {"username": "bot_user_1", "password": "pass", "client_id": "cid1", "client_secret": "cs1", "user_agent": "ua1"},
            {"username": "bot_user_2", "password": "pass", "client_id": "cid2", "client_secret": "cs2", "user_agent": "ua2"}
        ],
        "subreddits": ["dummy_subreddit"],
        "replies": {"chain_length": 1},
        "openai_api_key": "dummy_key",
        "openai": {"post_prompt": "Test post prompt", "reply_prompt": "Test reply prompt"},
        "personalities": {
            "bot_user_1": {"description": "Personality1", "memory": "Memory1"},
            "bot_user_2": {"description": "Personality2", "memory": "Memory2"}
        }
    }
    account_manager = DummyAccountManager()
    bot_manager = BotManager(config, account_manager)
    bots = bot_manager.get_bots()
    assert len(bots) == 2
    assert bots[0].username == "bot_user_1"
    assert bots[1].username == "bot_user_2"

def test_bot_manager_execute_command_for_bot(monkeypatch):
    config = {
        "accounts": [
            {"username": "bot_user_1", "password": "pass", "client_id": "cid1", "client_secret": "cs1", "user_agent": "ua1"},
            {"username": "bot_user_2", "password": "pass", "client_id": "cid2", "client_secret": "cs2", "user_agent": "ua2"}
        ],
        "subreddits": ["dummy_subreddit"],
        "replies": {"chain_length": 1},
        "openai_api_key": "dummy_key",
        "openai": {"post_prompt": "Test post prompt", "reply_prompt": "Test reply prompt"},
        "personalities": {
            "bot_user_1": {"description": "Personality1", "memory": "Memory1"},
            "bot_user_2": {"description": "Personality2", "memory": "Memory2"}
        }
    }
    account_manager = DummyAccountManager()
    bot_manager = BotManager(config, account_manager)
    # Monkeypatch each bot's handle_command to record its call.
    calls = []
    def fake_handle_command(self, command, target):
        calls.append((self.username, command, target))
    for bot in bot_manager.get_bots():
        monkeypatch.setattr(bot, "handle_command", fake_handle_command.__get__(bot))
    bot_manager.execute_command_for_bot("bot_user_2", "reply", target="dummy_target")
    assert any(username == "bot_user_2" and command == "reply" and target == "dummy_target" for username, command, target in calls)
