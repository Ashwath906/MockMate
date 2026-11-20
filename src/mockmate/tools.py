
from pathlib import Path
from langchain.tools import tool

WORKSPACE = Path("workspace").resolve()


@tool
def save_file(filename: str, content: str) -> str:
    """Save interview information inside the workspace/sessions folder."""

    if Path(filename).name != filename or filename in ("", ".", ".."):
        return "Error: Invalid filename."

    sessions_dir = WORKSPACE / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    file_path = (sessions_dir / filename).resolve()

    if not file_path.is_relative_to(sessions_dir.resolve()):
        return "Error: File path is outside the workspace."

    file_path.write_text(content, encoding="utf-8")

    return f"File saved successfully: {file_path}"

