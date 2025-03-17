import pytest
from config.config import load_config

def test_load_config(tmp_path):
    config_content = """
accounts:
  - username: "test_user"
    password: "pass"
    client_id: "cid"
    client_secret: "csecret"
    user_agent: "test user agent"
subreddits:
  - "test_subreddit"
openai_api_key: "dummy_key"
openai:
  post_prompt: "Test post prompt"
  reply_prompt: "Test reply prompt"
personalities:
  test_user:
    description: "Test personality"
    memory: "Test memory"
"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    config_file.write_text(config_content)
    
    config = load_config(str(config_file))
    assert config["accounts"][0]["username"] == "test_user"
    assert config["subreddits"][0] == "test_subreddit"
    assert config["openai"]["post_prompt"] == "Test post prompt"
