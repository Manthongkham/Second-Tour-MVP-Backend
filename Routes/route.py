from fastapi import APIRouter
from pydantic import BaseModel
from Services.open_ai import OpenAIClient
from Prompts.prompt import final_answer

router = APIRouter(prefix="/query", tags=["query"])
llm = OpenAIClient()

class QueryRequest(BaseModel):
    query: str

@router.post("/stream")
def run_query(payload: QueryRequest):
    prompt = final_answer(payload.query)
    answer = llm.generate(prompt, max_tokens=1000)
    return {"answer": answer}
