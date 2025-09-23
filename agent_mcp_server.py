import sys
import os
import logging
from typing import Any
from dotenv import load_dotenv
import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport # Import SseServerTransport
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route
import uvicorn


# Import the GovOpenApiAgent
from agent import GovOpenApiAgent

# --- New Imports for Runner and Session ---
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types # Alias to avoid conflict with mcp.types

load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Constants ---
APP_NAME = "gov_openapi_app"
USER_ID = "mcp_user_123" # Changed for MCP server context
SESSION_ID = "mcp_session_456" # Changed for MCP server context
ENABLE_TELEMETRY_LOGGING = os.getenv("ENABLE_ADK_TELEMETRY", "True").lower() == "true"

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    app = Server("gov-openapi-agent-mcp")

    # --- Agent and Runner Setup ---
    agent = GovOpenApiAgent()
    session_service = InMemorySessionService()

    # Create a session
    async def _create_session_task():
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )
    anyio.run(_create_session_task)

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    async def _process_user_input_internal(
        runner: Runner,
        user_id: str,
        session_id: str,
        user_input: str,
        session_service: InMemorySessionService
    ) -> str:
        """Helper function to process user input and return the agent's final response."""
        logger.info(f"Wuulong:Processing user input: {user_input}")
        content = genai_types.Content(role="user", parts=[genai_types.Part(text=user_input)])
        events = runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        )

        final_response_text = ""
        async for event in events:
            if ENABLE_TELEMETRY_LOGGING and 0:
                logger.info(f"Event: {event.model_dump_json(indent=2, exclude_none=True)}")
            
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
                break # Assuming we only care about the first final response

        return final_response_text

    @app.call_tool()
    async def process_user_prompt(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        logger.info(f"Wuulong:process_user_prompt: {arguments}")
        if name != "process_user_prompt":
            raise ValueError(f"Unknown tool: {name}")
        if "prompt" not in arguments:
            raise ValueError("Missing required argument 'prompt'")

        user_prompt = arguments["prompt"]
        logger.info(f"Received prompt: {user_prompt}")

        try:
            response_text = await _process_user_input_internal(
                runner=runner,
                user_id=USER_ID,
                session_id=SESSION_ID,
                user_input=user_prompt,
                session_service=session_service
            )
            if response_text:
                return [types.TextContent(type="text", text=response_text)]
            else:
                return [types.TextContent(type="text", text="Agent did not return any text content.")]
        except Exception as e:
            logger.error(f"Error processing prompt with GovOpenApiAgent: {e})")
            return [types.TextContent(type="text", text=f"Error: {e}")]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        logger.info(f"Wuulong:Listing tools for GovOpenApiAgent")
        return [
            types.Tool(
                name="process_user_prompt",
                title="處理使用者提示並與政府開放資料平台互動",
                description="接收使用者提示，智能解析並透過 OpenAPI 介面查詢相關政府開放資料，返回結果。",
                inputSchema={
                    "type": "object",
                    "required": ["prompt"],
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "使用者輸入的自然語言提示",
                        }
                    },
                },
            )
        ]

    if transport == "sse":
        sse = SseServerTransport("/messages/")

        async def handle_sse(request: Request):
            logger.info(f"Wuulong:handle_sse")
            async with sse.connect_sse(request.scope, request.receive, request._send) as streams:  # type: ignore[reportPrivateUsage]
                await anyio.sleep(0.1)
                logger.info(f"Wuulong:connect_sse: {streams}")
                await app.run(streams[0], streams[1], app.create_initialization_options())
            return Response()

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        uvicorn.run(starlette_app, host="127.0.0.1", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(streams[0], streams[1], app.create_initialization_options())

        anyio.run(arun)

    return 0

if __name__ == "__main__":
    sys.exit(main())
