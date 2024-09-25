import groq
import asyncio


class GroqLLM:
    def __init__(self, model_name="llama3-8b-8192", api_key=None):
        self.client = groq.Groq(api_key=None)
        self.model_name = model_name

    def invoke(self, prompt, max_tokens=2000):
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model_name,
            max_tokens=max_tokens,
        )
        return self.Response(response.choices[0].message.content)

    async def ainvoke(self, prompt, max_tokens=2000):
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model_name,
            max_tokens=max_tokens,
        )
        return self.Response(response.choices[0].message.content)

    class Response:
        def __init__(self, content):
            self.content = content
