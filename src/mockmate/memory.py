
import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


DATABASE_PATH = Path("workspace/mockmate_memory.sqlite")
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


connection = sqlite3.connect(
    str(DATABASE_PATH),
    check_same_thread=False
)

checkpointer = SqliteSaver(connection)

checkpointer.setup()


def get_thread_config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id
        }
    }
