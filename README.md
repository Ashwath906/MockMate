# MockMate – AI-Powered Mock Technical Interview Agent

MockMate is an AI-powered technical interview practice application built using Python, LangChain, LangGraph, and Deep Agents. It simulates technical interviews, evaluates candidate answers, tracks weak topics, and supports interview session management.

## Features

- **Interactive Interviews:** Practice technical interviews based on your target role, interview round, and difficulty.
- **AI Question Generation:** Generates interview questions using a configured Google Gemini model.
- **Answer Evaluation:** Evaluates answers using a structured scorecard.
- **Weak Topic Tracking:** Records areas where candidates need improvement.
- **Adaptive Interviews:** Uses saved weak-topic history to guide future practice.
- **Session Management:** Start, resume, and delete interview sessions.
- **Persistent Memory:** Uses LangGraph checkpointing to preserve interview state.
- **Workspace Protection:** Restricts file operations to the designated workspace and requires approval for sensitive operations.
- **Conversation Summarization:** Uses summarization middleware to manage longer interview conversations.

## Technology Stack

- Python 3.12+
- uv
- LangChain
- LangGraph
- Deep Agents
- Google Gemini
- Pydantic
- SQLite checkpointing

## Project Structure

```text
mockmate/
├── main.py
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── README.md
├── src/
│   └── mockmate/
│       ├── agent.py
│       ├── tools.py
│       ├── memory.py
│       ├── scorecard.py
│       └── weak_topics.py
└── workspace/
    └── sessions/
```

## Requirements

- Python 3.12 or later
- uv package manager
- Google Gemini API key
- Internet connection

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Ashwath906/MockMate.git
cd MockMate
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Copy the example environment file:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Open `.env` and add your Google Gemini API key.

Example:

```env
MODEL_PROVIDER=google_genai
MODEL_NAME=gemini-3.5-flash
GOOGLE_API_KEY=your_actual_api_key
```

Never share or upload your actual API key.

### 4. Run MockMate

```bash
uv run python main.py
```

## How to Use

1. Start the application.
2. Choose whether to resume an existing session or start a new interview.
3. Enter your target job role.
4. Select the interview round.
5. Choose the difficulty level.
6. Answer the interview questions.
7. Review the evaluation scorecard and improvement suggestions.
8. Type `exit` to leave the interview.
9. Resume a previous session or practise again to improve weak topics.

## Security

MockMate uses workspace path validation to prevent file operations outside the permitted workspace.

- Absolute paths are rejected.
- Parent-directory traversal is rejected.
- File overwrite and deletion require approval.
- Interview session data and API keys should not be committed to GitHub.

## Development

Install or synchronize dependencies:

```bash
uv sync
```

Check Python syntax:

```bash
uv run python -m py_compile main.py
```

Run the application:

```bash
uv run python main.py
```

## Future Enhancements

- Interview performance analytics
- Additional interview categories
- More detailed progress reports
- Improved question personalization

## Author

Developed as a technical workshop project.

**Project:** MockMate – AI-Powered Mock Technical Interview Agent