from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Fetch API key from environment variable for Google Generative AI
genai_api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=genai_api_key)

# Use the appropriate model for content generation
model = genai.GenerativeModel('gemini-pro')

# FastAPI app initialization
app = FastAPI()

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for conversation history
conversation_history = {}

# Define the request body structure for the chatbot
class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot API"}

# Chatbot endpoint
@app.post("/chat")
async def handle_input(request: ChatRequest):
    user_id = "default_user"  # Using a default user ID for simplicity
    history = conversation_history.get(user_id, [])

    # Append user input to history
    history.append({"role": "user", "content": request.message})

    try:
        # Generate AI response
        response = model.generate_content(request.message)
        ai_response = response.text
    except Exception as e:
        return JSONResponse(content={"error": "Failed to generate response", "details": str(e)})

    # Append AI response to history
    history.append({"role": "ai", "content": ai_response})

    # Update conversation history
    conversation_history[user_id] = history

    return JSONResponse(content={"conversation": history})

if __name__ == "__main__":
    import uvicorn
    # Use dynamic port for deployment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
