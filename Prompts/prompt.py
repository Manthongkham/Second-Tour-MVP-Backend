def final_answer(query: str) -> str:
    prompt = f"""
You are a financial expert.

Rules:
- ALL responses must be wrap up within 100 - 750 tokens. This is a hard stop and do not end mid sentences.

User input:
{query}
"""
    return prompt
