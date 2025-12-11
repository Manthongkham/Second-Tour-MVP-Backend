from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self, model: str = "gpt-5.1"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def generate(self, prompt: str) -> str:
        """
        Send a simple text prompt to the model and return the response text.
        """
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text
