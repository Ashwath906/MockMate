import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

print("Testing LangChain with Gemini 3.5 Flash...", flush=True)

try:
    model = init_chat_model(
        "gemini-3.5-flash",
        model_provider="google_genai",
        api_key=os.getenv("GOOGLE_API_KEY"),
        timeout=60,
        max_retries=0,
    )

    response = model.invoke("Reply with exactly: MockMate connected")

    print("SUCCESS:", response.content, flush=True)

except Exception as error:
    print("FAILED:", repr(error), flush=True)