import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Import existing clients
from spotify_client import SpotifySuperClient as SpotifyClient
from llm_client import LLMClient
from lastfm_client import LastfmClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="PersonalAIs Web Interface")

# Initialize Clients
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
lastfm_api_key = os.getenv("LASTFM_API_KEY")
lastfm_api_secret = os.getenv("LASTFM_API_SECRET")
llm_provider = os.getenv("LLM_PROVIDER", "ollama")
dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
username = os.getenv("SPOTIFY_USERNAME")

spotify_client = None
llm_client = None
lastfm_client = None

try:
    logger.info("Initializing clients...")
    if all([client_id, client_secret, redirect_uri, username]):
        spotify_client = SpotifyClient(client_id, client_secret, redirect_uri, username)
        logger.info("Spotify client initialized.")
    
    if lastfm_api_key and lastfm_api_secret:
        lastfm_client = LastfmClient(lastfm_api_key, lastfm_api_secret)
        logger.info("Last.fm client initialized.")

    llm_client = LLMClient(api_key=dashscope_api_key, provider=llm_provider)
    logger.info(f"LLM client ({llm_provider}) initialized.")

except Exception as e:
    logger.error(f"Error initializing clients: {e}")


# Pydantic models
class ChatRequest(BaseModel):
    message: str

# API Endpoints
@app.get("/api/me")
async def get_my_profile():
    if not spotify_client:
        raise HTTPException(status_code=503, detail="Spotify client not initialized")
    result = spotify_client.get_user_profile()
    if result["success"]:
        return result["data"]
    raise HTTPException(status_code=400, detail=result["message"])

@app.get("/api/now_playing")
async def get_now_playing():
    if not spotify_client:
        raise HTTPException(status_code=503, detail="Spotify client not initialized")
    result = spotify_client.get_current_playback()
    # Handle case where nothing is playing (returns success but data is None)
    if result["success"]:
        return result["data"] if result["data"] else {"is_playing": False}
    raise HTTPException(status_code=400, detail=result["message"])

@app.get("/api/playlists")
async def get_playlists():
    if not spotify_client:
        raise HTTPException(status_code=503, detail="Spotify client not initialized")
    result = spotify_client.get_user_playlists(limit=50) 
    if result["success"]:
        return result["data"]
    raise HTTPException(status_code=400, detail=result["message"])

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not llm_client:
        raise HTTPException(status_code=503, detail="LLM client not initialized")
    
    # Construct a simple prompt with context
    # Ideally, you'd want to maintain conversation history or context here
    prompt = request.message
    
    # We can inject some context if available, e.g., current song
    context = ""
    if spotify_client:
        pb = spotify_client.get_current_playback()
        if pb["success"] and pb["data"]:
            track = pb["data"]["item"]
            context = f"[Context: User is currently listening to '{track['name']}' by '{', '.join(a['name'] for a in track['artists'])}']\n"
    
    full_prompt = f"{context}User: {prompt}\nAssistant:"
    
    # Generate response
    response = llm_client.generate(full_prompt)
    
    # Handle different response structures (Dashscope vs Ollama wrapper)
    reply_text = "I couldn't generate a response."
    
    if response:
        # Check if it's the MockResponse object we created for Ollama
        if hasattr(response, 'output'):
             if hasattr(response.output, 'text'):
                 reply_text = response.output.text
             elif hasattr(response.output, 'choices'): # Standard OpenAI response obj
                 reply_text = response.choices[0].message.content
        # Or maybe it's a dict or other object depending on provider
        elif isinstance(response, dict):
             # Try to find text in common locations
             reply_text = response.get('output', {}).get('text', str(response))

    return {"response": reply_text}


# Serve Static Files
# Mount static files to root for index.html, or specific path
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("web_server:app", host="0.0.0.0", port=8000, reload=True)
