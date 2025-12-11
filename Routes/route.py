from fastapi import APIRouter
from pydantic import BaseModel
from Services.open_ai import OpenAIClient
from Prompts.prompt import final_answer

router = APIRouter(prefix="/query", tags=["query"])
llm = OpenAIClient()

class QueryRequest(BaseModel):
    query: str

@router.post("/stream")
def run_query(user_input: QueryRequest):
    prompt = final_answer(user_input.query)
    answer = llm.generate(prompt, max_tokens=1000)
    return {"answer": answer}
