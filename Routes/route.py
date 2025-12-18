from fastapi import APIRouter
from pydantic import BaseModel
from Services.open_ai import OpenAIClient
from Prompts.prompt import final_answer

router = APIRouter(prefix="/query", tags=["query"])
llm = OpenAIClient()


class QueryRequest(BaseModel):
    query: str

# 🧠 Conversation memory (lives in RAM)
conversation = []
@router.post("/stream")
def run_query(user_input: QueryRequest):
    # 1) Add user message to memory
    conversation.append(f"User: {user_input.query}")

    # 2) Build prompt from memory
    full_conversation = "\n".join(conversation)
    prompt = final_answer(full_conversation)

    # 3) Ask the model
    answer = llm.generate(prompt, max_tokens=1000)

    # 4) Save assistant response
    conversation.append(f"Assistant: {answer}")

    return {"answer": answer}


@router.post("/reset")
def reset():
    conversation.clear()
    return {"message": "Conversation cleared"}

