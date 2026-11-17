
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os

load_dotenv()

model_name = os.getenv("MODEL_NAME")
api_key = os.getenv("GOOGLE_API_KEY")

model = init_chat_model(
    model_name,
    model_provider="google_genai",
    api_key=api_key
)

response = model.invoke("Say: Hello! MockMate is connected successfully.")

print(response.content)
