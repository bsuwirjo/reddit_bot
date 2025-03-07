import pytest
from providers.openai_provider import OpenAIProvider

# DummyResponse mimics the new ChatCompletion response format.
class DummyResponse:
    def __init__(self, text):
        self.choices = [type("Choice", (), {"message": {"content": text}})()]

# Dummy completion function that accepts arbitrary kwargs.
def dummy_completion_create(*args, **kwargs):
    messages = kwargs.get("messages", [])
    user_message = messages[0]["content"] if messages else ""
    if "Post:" in user_message:
        return DummyResponse("Test Title\nTest Body")
    else:
        return DummyResponse("Test Reply")

def test_generate_post_content(monkeypatch):
    monkeypatch.setattr("providers.openai_provider.openai.ChatCompletion.create", dummy_completion_create)
    provider = OpenAIProvider(
        "dummy_key",
        post_prompt="Test post prompt",
        personality="Test personality",
        memory="Test memory"
    )
    title, body = provider.generate_post_content()
    assert title == "Test Title"
    assert body == "Test Body"

def test_generate_reply_content_without_thread(monkeypatch):
    monkeypatch.setattr("providers.openai_provider.openai.ChatCompletion.create", dummy_completion_create)
    provider = OpenAIProvider(
        "dummy_key",
        reply_prompt="Test reply prompt",
        personality="Test personality",
        memory="Test memory"
    )
    # Dummy target without a parent chain.
    class DummyTarget:
        title = "Dummy Title"
        selftext = "Dummy Body"
    reply = provider.generate_reply_content(DummyTarget(), 0)
    assert reply == "Test Reply"

def test_collect_thread_context():
    provider = OpenAIProvider(
        "dummy_key",
        reply_prompt="Test reply prompt",
        personality="Test personality",
        memory="Test memory"
    )
    # Create a dummy submission representing the original post.
    class DummySubmission:
        title = "Submission Title"
        selftext = "Submission Body"
    # Create a dummy comment that replies to the submission.
    class DummyComment:
        def __init__(self, body, parent_obj):
            self.body = body
            self.parent_id = "t1_dummy"
            self._parent = parent_obj
        def parent(self):
            return self._parent
    submission = DummySubmission()
    dummy_comment = DummyComment("Comment Body", submission)
    context = provider.collect_thread_context(dummy_comment)
    expected_context = "Post Title: Submission Title\nPost Body: Submission Body\n\nComment Body"
    assert context == expected_context

def test_generate_reply_content_with_thread(monkeypatch):
    captured_prompts = []
    def dummy_completion_create_capture(*args, **kwargs):
        captured_prompts.append(kwargs["messages"][0]["content"])
        return DummyResponse("Test Reply")
    monkeypatch.setattr("providers.openai_provider.openai.ChatCompletion.create", dummy_completion_create_capture)
    
    provider = OpenAIProvider(
        "dummy_key",
        reply_prompt="Test reply prompt",
        personality="Test personality",
        memory="Test memory"
    )
    class DummySubmission:
        title = "Submission Title"
        selftext = "Submission Body"
    class DummyComment:
        def __init__(self, body, parent_obj):
            self.body = body
            self.parent_id = "t1_dummy"
            self._parent = parent_obj
        def parent(self):
            return self._parent
    submission = DummySubmission()
    dummy_comment = DummyComment("Comment Body", submission)
    reply = provider.generate_reply_content(dummy_comment, 0)
    assert len(captured_prompts) == 1, "Expected one captured prompt"
    prompt = captured_prompts[0]
    assert "Submission Title" in prompt, f"Prompt does not contain 'Submission Title': {prompt}"
    assert "Submission Body" in prompt, f"Prompt does not contain 'Submission Body': {prompt}"
    assert "Comment Body" in prompt, f"Prompt does not contain 'Comment Body': {prompt}"
    assert reply == "Test Reply"
