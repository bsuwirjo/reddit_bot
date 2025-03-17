import openai

class OpenAIProvider:
    def __init__(self, api_key, post_prompt=None, reply_prompt=None, personality=None, memory=None):
        self.api_key = api_key
        openai.api_key = api_key
        self.post_prompt = post_prompt or "Generate an engaging Reddit post title and body."
        self.reply_prompt = reply_prompt or "Generate a thoughtful reply to the following Reddit content:"
        self.personality = personality or ""
        self.memory = memory or ""

    def generate_post_content(self, learned_context=None):
        """
        Generate post content using OpenAI's ChatCompletion API, incorporating personality,
        memory, and optionally additional learned context.
        """
        prompt = (
            f"{self.post_prompt}\n\n"
            f"Personality: {self.personality}\n"
            f"Memory: {self.memory}\n"
        )
        if learned_context:
            prompt += f"Context: {learned_context}\n"
        prompt += "\nPost:"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        text = response.choices[0].message['content'].strip()
        lines = text.split("\n", 1)
        title = lines[0] if lines else "Default Title"
        body = lines[1] if len(lines) > 1 else "Default body content."
        return title, body

    def generate_reply_content(self, target, chain_index):
        """
        Generate a reply using OpenAI's ChatCompletion API, incorporating personality, memory,
        and the full thread context.
        """
        if hasattr(target, "parent_id"):
            context = self.collect_thread_context(target)
        else:
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        reply = response.choices[0].message['content'].strip()
        return reply

    def collect_thread_context(self, target):
        """
        Collect context from the target by traversing the parent chain.
        Gathers the original post and all parent comments.
        """
        context_parts = []
        current = target
        while hasattr(current, "parent_id") and isinstance(current.parent_id, str) and current.parent_id.startswith("t1_"):
            try:
                context_parts.insert(0, current.body)
            except AttributeError:
                pass
            try:
                current = current.parent()
            except Exception:
                break
        if hasattr(current, "title") and hasattr(current, "selftext"):
            submission_text = f"Post Title: {current.title}\nPost Body: {current.selftext}"
            context_parts.insert(0, submission_text)
        return "\n\n".join(context_parts)
