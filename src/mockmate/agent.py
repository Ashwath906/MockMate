
import os
from dotenv import load_dotenv
from pydantic import ValidationError

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

from mockmate.tools import save_file
from mockmate.scorecard import InterviewScorecard
from mockmate.memory import checkpointer, get_thread_config
from langchain.agents.middleware import SummarizationMiddleware
load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER")
MODEL_NAME = os.getenv("MODEL_NAME")
API_KEY = os.getenv("GOOGLE_API_KEY")

if not MODEL_PROVIDER or not MODEL_NAME or not API_KEY:
    raise ValueError("Missing model configuration in .env")

model = init_chat_model(
    MODEL_NAME,
    model_provider=MODEL_PROVIDER,
    api_key=API_KEY
)

SYSTEM_PROMPT = """
You are MockMate, an AI-powered technical interviewer.

Your responsibilities:
1. Conduct professional technical interviews.
2. Ask exactly ONE interview question at a time.
3. Wait for the candidate's answer before asking another question.
4. Never reveal the expected answer before the candidate responds.
5. Ask questions based on the candidate's role, round and difficulty.
6. Be professional and supportive.
7. Never ask multiple questions in one message.
8. Use the save_file tool when interview information needs to be saved.
9. Remember the previous messages in the current interview.
"""

agent = create_agent(
    model=model,
    tools=[save_file],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
    middleware=[
        SummarizationMiddleware(
            model,
            trigger=("messages", 12),
            keep=("messages", 6)
        )
    ]
)


def ask_interviewer(
    user_input: str,
    thread_id: str = "mockmate-default"
) -> str:

    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": user_input}
            ]
        },
        config=get_thread_config(thread_id)
    )

    content = result["messages"][-1].content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )

    return str(content)


def evaluate_answer(
    question: str,
    answer: str
) -> InterviewScorecard:

    evaluation_prompt = f"""
    Evaluate this interview answer honestly.

    Question: {question}
    Candidate answer: {answer}

    Return a score from 0 to 10.
    Give exactly 2 strengths.
    Give exactly 2 gaps.
    Give 1 improvement hint.
    Give 1 next topic.
    """

    structured_model = model.with_structured_output(
        InterviewScorecard
    )

    for attempt in range(2):
        try:
            result = structured_model.invoke(evaluation_prompt)
            return InterviewScorecard.model_validate(result)

        except (ValidationError, ValueError, TypeError) as error:
            evaluation_prompt += f"""

            Your previous response was invalid:
            {error}

            Try again. Follow every scorecard requirement exactly.
            """

    raise ValueError(
        "Gemini failed to generate a valid scorecard after 2 attempts."
    )

def has_saved_conversation(thread_id: str) -> bool:
    """Check whether a conversation exists in SQLite memory."""

    state = agent.get_state(
        get_thread_config(thread_id)
    )

    return bool(
        state.values
        and state.values.get("messages")
    )
