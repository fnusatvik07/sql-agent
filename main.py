import logging
import time
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

# ─────────────────────────────
# Environment & Logging Setup
# ─────────────────────────────
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SQLChatServer")

# ─────────────────────────────
# FastAPI App
# ─────────────────────────────
app = FastAPI(
    title="LangChain SQL Chat API",
    version="1.1.0",
    description="LLM-powered SQL agent with proper final answer formatting and full logging.",
)

# ─────────────────────────────
# Database + LLM Setup
# ─────────────────────────────
db = SQLDatabase.from_uri("sqlite:///Chinook.db")
llm = init_chat_model("openai:gpt-4.1")

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

system_prompt = f"""
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {db.dialect} query to run,
then look at the results of the query and return the answer.

Limit results to 5 unless otherwise requested.
Double-check syntax before execution.
Never perform any DML statements like INSERT, UPDATE, DELETE, or DROP.
"""

agent = create_react_agent(llm, tools, prompt=system_prompt)

# ─────────────────────────────
# Request Model
# ─────────────────────────────
class ChatRequest(BaseModel):
    question: str


# ─────────────────────────────
# Middleware for request logging
# ─────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"➡️ {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"💥 Request failed: {e}", exc_info=True)
        raise e
    duration = round(time.time() - start_time, 3)
    logger.info(f"✅ {request.method} {request.url} completed in {duration}s with status {response.status_code}")
    return response


# ─────────────────────────────
# Chat Endpoint
# ─────────────────────────────
@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Ask a natural-language question about the SQL database.
    Returns only the final formatted answer.
    Full logs remain in server.log.
    """
    start_time = time.time()
    question = request.question.strip()
    logger.info(f"🧠 Chat Request: {question}")

    try:
        messages = [{"role": "user", "content": question}]
        final_response = None
        all_contents = []

        # Stream reasoning steps internally
        for step in agent.stream({"messages": messages}, stream_mode="values"):
            step_messages = step.get("messages", [])
            if not step_messages:
                continue

            last_msg = step_messages[-1]
            role = getattr(last_msg, "role", "unknown")
            content = getattr(last_msg, "content", "") or ""
            msg_type = getattr(last_msg, "type", "text")

            # Track every output for logging
            logger.debug(f"Step | Role: {role} | Type: {msg_type} | Content: {content}")

            # Detect and log tool calls
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for call in last_msg.tool_calls:
                    tool_name = call.get("name")
                    tool_input = call.get("args")
                    logger.info(f"🛠️ Tool Call → {tool_name} | Input: {tool_input}")

            # Save last non-empty assistant/human-like message as possible final answer
            if content.strip():
                all_contents.append(content.strip())

        # Get last message that looks like a natural-language answer
        if all_contents:
            final_response = all_contents[-1]
        else:
            final_response = "No response generated."

        duration = round(time.time() - start_time, 3)
        logger.info(f"✅ Final Answer ({duration}s): {final_response}")

        return JSONResponse(
            content={
                "question": question,
                "answer": final_response,
                "execution_time_sec": duration,
            }
        )

    except Exception as e:
        logger.error(f"💥 Error in /chat: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


# ─────────────────────────────
# Health Endpoint
# ─────────────────────────────
@app.get("/health")
async def health():
    """Check LLM and DB connectivity."""
    try:
        db.run("SELECT 1;")
        logger.info("✅ Health check OK")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


@app.get("/check")
async def health():
    """Check Github Actions"""
    try:
        db.run("SELECT 1;")
        logger.info("✅ Health check OK")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


# ─────────────────────────────
# Run server
# ─────────────────────────────
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting LangChain SQL Chat Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
