from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self, model: str = "gpt-5.1"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model


    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            max_output_tokens=max_tokens
        )
        return response.output_text

print("SSL_CERT_FILE:", os.getenv("SSL_CERT_FILE"))