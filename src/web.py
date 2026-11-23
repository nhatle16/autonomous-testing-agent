import os
import uuid
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain.messages import HumanMessage
from pydantic import BaseModel

from src.agent import build_agent
from src.chat import iter_reply

STATIC_DIR = Path(__file__).parent / "static"


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ResetRequest(BaseModel):
    session_id: str


def create_app(agent=None) -> FastAPI:
    """Build the web chat app; the Gemini agent is built only when none is passed."""
    agent = agent or build_agent()
    app = FastAPI(title="Test-drafting agent")
    # shortcut: in-memory history is lost on restart and grows unbounded; fine for local use
    sessions: dict[str, dict] = {}

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    def session(session_id):
        # Each session has its own history and a thread id grouping its turns in LangSmith
        return sessions.setdefault(session_id, {"messages": [], "thread_id": str(uuid.uuid4())})

    @app.post("/api/chat")
    def chat(request: ChatRequest):
        if not request.message.strip():
            raise HTTPException(400, "Message is empty")
        state = session(request.session_id)
        messages = state["messages"] + [HumanMessage(content=request.message)]
        config = {"metadata": {"thread_id": state["thread_id"]}}

        def stream():
            try:
                for kind, data in iter_reply(agent, messages, config):
                    if kind == "text":
                        yield data
                    else:
                        # History is saved only once the whole turn succeeded
                        state["messages"] = data
            except Exception as e:  # noqa: BLE001
                # Same as the terminal chat: report the error and drop the failed turn
                yield f"Error invoking agent: {e}"

        return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")

    @app.post("/api/reset")
    def reset(request: ResetRequest):
        sessions.pop(request.session_id, None)
        return {"ok": True}

    return app


def main() -> None:
    load_dotenv()
    # Verify that API key is set before building the agent
    if not os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is not set. Copy .env.example to .env and set your API key.")
        return
    # Local only: read_input opens any file path it's given, so never expose this on a network
    uvicorn.run(create_app(), host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
