import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import logging
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the GovOpenApiAgent
try:
    from agent import GovOpenApiAgent
except ImportError as e:
    logger.error(f"Failed to import GovOpenApiAgent: {e}. Make sure agent.py is accessible.")
    raise

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    response: str

# --- FastAPI App Initialization ---
app = FastAPI(
    title="GovOpenApiAgent Web API",
    description="Web interface for interacting with the GovOpenApiAgent.",
    version="1.0.0",
        servers=[{"url": "http://localhost:8802", "description": "Agent Web API Server"}]

)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development. In production, specify your frontend URL(s).
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Global instances
gov_openapi_agent: GovOpenApiAgent = None
session_service: InMemorySessionService = None
agent_runner: Runner = None

# Fixed user and session IDs for this web interface
WEB_USER_ID = "web_user"
WEB_SESSION_ID = "web_session_fixed"
WEB_APP_NAME = "web_agent_app"

@app.on_event("startup")
async def startup_event():
    global gov_openapi_agent, session_service, agent_runner
    logger.info("Initializing GovOpenApiAgent and related services...")
    try:
        # 1. Initialize GovOpenApiAgent
        gov_openapi_agent = GovOpenApiAgent()
        logger.info("GovOpenApiAgent initialized.")

        # 2. Initialize Session Service
        session_service = InMemorySessionService()
        logger.info("InMemorySessionService initialized.")

        # 3. Create a session for the web interface
        await session_service.create_session(
            app_name=WEB_APP_NAME,
            user_id=WEB_USER_ID,
            session_id=WEB_SESSION_ID,
        )
        logger.info(f"Session created for user '{WEB_USER_ID}' and session '{WEB_SESSION_ID}'.")

        # 4. Initialize Runner
        agent_runner = Runner(
            agent=gov_openapi_agent,
            app_name=WEB_APP_NAME,
            session_service=session_service,
        )
        logger.info("Agent Runner initialized.")

        logger.info("All services initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}", exc_info=True)
        gov_openapi_agent = None
        session_service = None
        agent_runner = None

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down GovOpenApiAgent Web API.")

# --- API Endpoints ---

@app.get("/health", summary="Health check endpoint")
async def health_check():
    return {"status": "ok", "agent_initialized": agent_runner is not None}

@app.post("/query", response_model=QueryResponse, summary="Send a query to the GovOpenApiAgent")
async def query_agent(request: QueryRequest):
    if agent_runner is None:
        raise HTTPException(status_code=503, detail="Agent services are not initialized. Please check server logs.")

    logger.info(f"Received query: {request.prompt}")
    try:
        content = genai_types.Content(role="user", parts=[genai_types.Part(text=request.prompt)])
        events = agent_runner.run_async(
            user_id=WEB_USER_ID,
            session_id=WEB_SESSION_ID,
            new_message=content,
        )

        final_response_text = ""
        async for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
                break
        
        if not final_response_text:
            logger.warning(f"Agent did not return a final text response for prompt: {request.prompt}")
            final_response_text = "Agent did not return a specific response."

        return QueryResponse(response=final_response_text)
    except Exception as e:
        logger.error(f"Error processing query with GovOpenApiAgent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# To run the server:
# uvicorn web:app --reload --port 8802
