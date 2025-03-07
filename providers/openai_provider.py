import openai

class OpenAIProvider:
    def __init__(self, api_key, post_prompt=None, reply_prompt=None, personality=None, memory=None):
        self.api_key = api_key
        openai.api_key = api_key
        self.post_prompt = post_prompt or "Generate an engaging Reddit post title and body."
        self.reply_prompt = reply_prompt or "Generate a thoughtful reply to the following Reddit content:"
        self.personality = personality or ""
        self.memory = memory or ""

    def generate_post_content(self):
        """
        Generate post content using OpenAI, incorporating personality and memory.
        """
        prompt = (
            f"{self.post_prompt}\n\n"
            f"Personality: {self.personality}\n"
            f"Memory: {self.memory}\n\n"
            "Post:"
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        text = response.choices[0].text.strip()
        # Split the response into a title and a body.
        lines = text.split("\n", 1)
        title = lines[0] if lines else "Default Title"
        body = lines[1] if len(lines) > 1 else "Default body content."
        return title, body

    def collect_thread_context(self, target):
        """
        Collect context from the target by traversing the parent chain.
        If the target is a comment, this function gathers the text of all
        parent comments (and the submission) so that the generated prompt
        includes the entire conversation thread.
        """
        context_parts = []
        current = target

        # Traverse up the comment chain.
        # Check if the target has a parent_id and if it indicates a comment (prefix "t1_").
        while hasattr(current, "parent_id") and isinstance(current.parent_id, str) and current.parent_id.startswith("t1_"):
            # Assume the comment text is available as "body"
            try:
                context_parts.insert(0, current.body)
            except AttributeError:
                pass  # If no body, skip
            try:
                # Move to the parent comment
                current = current.parent()
            except Exception:
                break  # In case parent() is not implemented or fails

        # At this point, current is likely the submission. Include its title and selftext.
        if hasattr(current, "title") and hasattr(current, "selftext"):
            submission_text = f"Post Title: {current.title}\nPost Body: {current.selftext}"
            context_parts.insert(0, submission_text)
        return "\n\n".join(context_parts)

    def generate_reply_content(self, target, chain_index):
        """
        Generate a reply based on the target content using OpenAI,
        incorporating personality, memory, and the full thread context.
        """
        # If the target has a parent_id, attempt to collect the full thread context.
        if hasattr(target, "parent_id"):
            context = self.collect_thread_context(target)
        else:
            # If no parent_id, fallback to using target's title or body.
            if hasattr(target, "title"):
                context = f"Post Title: {target.title}\nPost Body: {target.selftext}"
            elif hasattr(target, "body"):
                context = target.body
            else:
                context = "No context available."

        prompt = (
            f"{self.reply_prompt}\n\n"
            f"Personality: {self.personality}\n"
            f"Memory: {self.memory}\n\n"
            f"Context:\n{context}\n\n"
            f"Reply #{chain_index+1}:"
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        reply = response.choices[0].text.strip()
        return reply
