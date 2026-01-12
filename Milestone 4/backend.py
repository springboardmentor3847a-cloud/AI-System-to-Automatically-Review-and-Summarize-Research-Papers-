from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os

# Import your custom modules
import auth
import database
import workflow

app = FastAPI(
    title="ResearchAI API",
    description="Backend API for the Automated Research Assistant",
    version="1.0.0"
)

# --- Pydantic Models (Data Validation) ---
class UserLogin(BaseModel):
    username: str
    password: str

class ResearchRequest(BaseModel):
    topic: str
    username: str

class HistoryResponse(BaseModel):
    topic: str
    timestamp: str

# --- Endpoints ---

@app.get("/")
def home():
    return {"message": "ResearchAI API is running. Go to /docs for Swagger UI."}

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserLogin):
    """Register a new user."""
    success, message = auth.register_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@app.post("/login")
def login(user: UserLogin):
    """Authenticate a user."""
    if auth.authenticate_user(user.username, user.password):
        # In a real app, you would return a JWT token here
        return {"status": "success", "message": "Login successful", "user": user.username}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/research")
def start_research(request: ResearchRequest):
    """Trigger the LangGraph workflow to research a topic."""
    if not request.topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    try:
        # 1. Run the AI Agent Workflow
        print(f"Received research request for: {request.topic}")
        final_report = workflow.run_research(request.topic)
        
        # 2. Save to Database
        # We save a snippet (first 200 chars) as the summary for the history list
        summary_snippet = final_report[:200].replace("\n", " ") + "..."
        database.save_research(request.username, request.topic, summary_snippet)
        
        return {
            "topic": request.topic,
            "report": final_report,
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{username}", response_model=List[HistoryResponse])
def get_user_history(username: str):
    """Fetch past research topics for a user."""
    raw_history = database.get_history(username)
    # Convert DB tuples to JSON format
    return [{"topic": h[0], "timestamp": h[1]} for h in raw_history]

# --- Run Server ---
if __name__ == "__main__":
    # This allows you to run 'python backend.py' directly
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)