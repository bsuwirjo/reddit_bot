import pytest
from providers.openai_provider import OpenAIProvider

# Dummy response class to simulate OpenAI API responses.
class DummyResponse:
    def __init__(self, text):
        self.choices = [type("Choice", (), {"text": text})()]

# A dummy completion create function that always returns a fixed reply.
def dummy_completion_create(engine, prompt, max_tokens, temperature):
    return DummyResponse("Test Reply")

def test_generate_post_content(monkeypatch):
    monkeypatch.setattr("providers.openai_provider.openai.Completion.create", dummy_completion_create)
    provider = OpenAIProvider(
        "dummy_key",
        post_prompt="Test post prompt",
        personality="Test personality",
        memory="Test memory"
    )
    title, body = provider.generate_post_content()
    # We expect non-empty title and body.
    assert title != ""
    assert body != ""

def test_generate_reply_content_without_thread(monkeypatch):
    """
    Test generate_reply_content when the target does not have a parent chain.
    """
    monkeypatch.setattr("providers.openai_provider.openai.Completion.create", dummy_completion_create)
    provider = OpenAIProvider(
        "dummy_key",
        reply_prompt="Test reply prompt",
        personality="Test personality",
        memory="Test memory"
    )
    # Create a dummy target without a parent_id.
    class DummyTarget:
        title = "Dummy Title"
        selftext = "Dummy Body"
    reply = provider.generate_reply_content(DummyTarget(), 0)
    assert reply == "Test Reply"

def test_collect_thread_context():
    """
    Test the collect_thread_context method directly to ensure it collects the submission
    and comment context.
    """
    provider = OpenAIProvider(
        "dummy_key",
        reply_prompt="Test reply prompt",
        personality="Test personality",
        memory="Test memory"
    )
    
    # Create a dummy submission that represents the original post.
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
    assert context == expected_context, f"Expected context:\n{expected_context}\nGot:\n{context}"

def test_generate_reply_content_with_thread(monkeypatch):
    """
    Test that generate_reply_content collects the full thread context when the target has a parent chain.
    """
    captured_prompts = []
    def dummy_completion_create_capture(engine, prompt, max_tokens, temperature):
        captured_prompts.append(prompt)
        return DummyResponse("Test Reply")
    monkeypatch.setattr("providers.openai_provider.openai.Completion.create", dummy_completion_create_capture)
    
    provider = OpenAIProvider(
        "dummy_key",
        reply_prompt="Test reply prompt",
        personality="Test personality",
        memory="Test memory"
    )
    
    # Create a dummy submission (the root post).
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
    
    reply = provider.generate_reply_content(dummy_comment, 0)
    
    # Ensure a prompt was captured.
    assert len(captured_prompts) == 1, "Expected one captured prompt"
    prompt = captured_prompts[0]
    
    # Check that the prompt includes the submission title, submission body, and comment body.
    assert "Submission Title" in prompt, f"Prompt does not contain 'Submission Title': {prompt}"
    assert "Submission Body" in prompt, f"Prompt does not contain 'Submission Body': {prompt}"
    assert "Comment Body" in prompt, f"Prompt does not contain 'Comment Body': {prompt}"
    
    # Also, the dummy reply should be returned.
    assert reply == "Test Reply"
