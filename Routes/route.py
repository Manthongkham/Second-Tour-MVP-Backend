from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from Services.open_ai import OpenAIClient
from Prompts.prompt import final_answer, user_info
import json
import math

router = APIRouter(prefix="/query", tags=["query"])
llm = OpenAIClient()

class QueryRequest(BaseModel):
    query: str

user_state = {
    "current_city": None,
    "current_state": None,
    "new_city": None,
    "new_state": None,
    "monthly_expenses": None,
    "household_type": None,
    "months_left_in_service": None,
    "current_savings": None,
    "num_cars": None,
    "num_family_members": None
}

def update_user_state(llm, state, text):
    data = json.loads(llm.generate(user_info(text), max_tokens=300))

    for key in state:
        if data.get(key) is not None:
            state[key] = data[key]

    print("UPDATED STATE:", state)
    return state


# 🧠 Conversation memory (lives in RAM)
conversation = []
@router.post("/stream")
def run_query(user_input: QueryRequest):

    global user_state

    # 0) Update user info JSON FIRST
    user_state = update_user_state(llm, user_state, user_input.query)

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
    global user_state
    conversation.clear()
    user_state = {k: None for k in user_state}
    return {"message": "Conversation cleared"}

from fastapi import HTTPException
import math

@router.post("/finance_card")
def finance_card():
    # 1) Validate required fields
    required = [
        "monthly_expenses",
        "household_type",
        "months_left_in_service",
        "current_savings",
        "num_cars",
        "num_family_members",
        "new_city",
        "new_state",
    ]
    missing = [k for k in required if user_state.get(k) in (None, "")]
    if missing:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Missing required info to calculate finance card.",
                "missing": missing,
                "user_state": user_state
            }
        )

    # 2) Read inputs
    monthly_expenses = float(user_state["monthly_expenses"])
    household_type = str(user_state["household_type"])
    months_left = int(user_state["months_left_in_service"])
    current_savings = float(user_state["current_savings"])
    num_cars = int(user_state["num_cars"])
    num_family = int(user_state["num_family_members"])

    if months_left <= 0:
        raise HTTPException(status_code=400, detail="months_left_in_service must be > 0")

    # 3) Emergency fund multiplier (simple MVP)
    if household_type == "single":
        emergency_months = 3
    elif household_type == "married_no_kids":
        emergency_months = 6
    elif household_type == "married_kids":
        emergency_months = 12
    else:
        emergency_months = 6  # default

    # 4) Emergency fund goal
    emergency_goal = monthly_expenses * emergency_months

    # 5) Moving cost goal (simple MVP assumptions)
    # NOTE: Replace these constants later with real data.
    DEFAULT_RENT_ESTIMATE = 1800      # fallback rent/month
    AVG_CAR_MOVE_COST = 900           # per car
    AVG_FLIGHT_COST = 300             # per person
    SAFETY_BUFFER = 1.25              # +25%

    rent_est = DEFAULT_RENT_ESTIMATE
    safe_rent = rent_est * SAFETY_BUFFER
    housing_cost = safe_rent * 3      # deposit + first + last

    car_cost = num_cars * AVG_CAR_MOVE_COST
    flight_cost = num_family * AVG_FLIGHT_COST * SAFETY_BUFFER

    moving_goal = housing_cost + car_cost + flight_cost

    # 6) Savings allocation (MVP: split 50/50)
    emergency_saved = current_savings * 0.5
    moving_saved = current_savings * 0.5

    # 7) Monthly required savings
    emergency_needed = max(0.0, emergency_goal - emergency_saved)
    moving_needed = max(0.0, moving_goal - moving_saved)

    emergency_monthly = emergency_needed / months_left
    moving_monthly = moving_needed / months_left
    total_monthly = emergency_monthly + moving_monthly

    # 8) Return "finance card" payload
    return {
        "destination": f"{user_state['new_city']}, {user_state['new_state']}",
        "months_left_in_service": months_left,

        "emergency_fund": {
            "monthly_expenses": round(monthly_expenses, 2),
            "multiplier_months": emergency_months,
            "goal": round(emergency_goal, 2),
            "saved_assumed": round(emergency_saved, 2),
            "needed": round(emergency_needed, 2),
            "monthly_required": round(emergency_monthly, 2),
        },

        "moving_cost": {
            "rent_estimate_used": rent_est,
            "safety_buffer": SAFETY_BUFFER,
            "housing_cost": round(housing_cost, 2),
            "car_cost": round(car_cost, 2),
            "flight_cost": round(flight_cost, 2),
            "goal": round(moving_goal, 2),
            "saved_assumed": round(moving_saved, 2),
            "needed": round(moving_needed, 2),
            "monthly_required": round(moving_monthly, 2),
        },

        "total_monthly_required": round(total_monthly, 2),

        "assumptions": [
            "Current savings split 50/50 between emergency fund and moving fund (MVP).",
            f"Rent estimate defaulted to ${DEFAULT_RENT_ESTIMATE}/mo (MVP).",
            f"Car move cost defaulted to ${AVG_CAR_MOVE_COST}/car (MVP).",
            f"Flight cost defaulted to ${AVG_FLIGHT_COST}/person +25% buffer (MVP).",
        ],
    }
