
import groq

class GroqLLM:
    def __init__(self, model_name='mixtral-8x7b-32768'):
        self.client = groq.Groq(api_key="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")
        self.model_name = model_name

    def invoke(self, prompt, max_tokens=10000):
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model_name,
            max_tokens=max_tokens
        )
        return self.Response(response.choices[0].message.content)

    class Response:
        def __init__(self, content):
            self.content = content