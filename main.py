
import json
from datetime import datetime
from pathlib import Path

from mockmate.agent import ask_interviewer, evaluate_answer
from mockmate.weak_topics import (
    record_weak_topics,
    read_weak_topics,
    reset_weak_topics,
)


SESSIONS_DIR = Path("workspace/sessions")
WEAK_TOPICS_FILE = Path("workspace/weak-topics.md")


# --------------------------------------------------
# SESSION FILE MANAGEMENT
# --------------------------------------------------

def save_session(session, session_file):
    """Save interview session automatically."""
    session["updated_at"] = datetime.now().isoformat()

    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
        json.dumps(session, indent=4),
        encoding="utf-8",
    )


def create_session():
    """Create a new interview session."""

    print("\n--- New MockMate Interview ---")

    role = input("Enter your target role (or type 'just start'): ").strip()
    if not role or role.lower() == "just start":
        role = "Software Engineer"

    interview_round = input(
        "Enter interview round (or type 'just start'): "
    ).strip()
    if not interview_round or interview_round.lower() == "just start":
        interview_round = "Technical"

    difficulty = input(
        "Enter difficulty (Easy/Medium/Hard, or 'just start'): "
    ).strip()
    if not difficulty or difficulty.lower() == "just start":
        difficulty = "Medium"

    session_id = datetime.now().strftime("session_%Y%m%d_%H%M%S")

    session = {
        "session_id": session_id,
        "thread_id": session_id,
        "role": role,
        "round": interview_round,
        "difficulty": difficulty,
        "answers": [],
        "scorecards": [],
        "current_question": None,
        "pending_answer": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    session_file = SESSIONS_DIR / f"{session_id}.json"
    save_session(session, session_file)

    print("\nInterview session created successfully.")
    print(f"Role: {role}")
    print(f"Round: {interview_round}")
    print(f"Difficulty: {difficulty}")

    return session, session_file


# --------------------------------------------------
# APPROVAL BEFORE DESTRUCTIVE OPERATIONS
# --------------------------------------------------

def request_file_approval(file_path, action="overwrite"):
    """Ask permission before a destructive file operation."""

    if not file_path.exists():
        print("File does not exist.")
        return "reject"

    print(f"\nWARNING: You are about to {action}: {file_path}")
    print("1. Approve")
    print("2. Edit")
    print("3. Reject")

    choice = input("Choose (1/2/3): ").strip()

    if choice == "1":
        print("Operation approved.")
        return "approve"

    if choice == "2":
        print("Edit selected.")
        return "edit"

    print("Operation rejected. Original file remains unchanged.")
    return "reject"


def reset_weak_topics_with_approval():
    """Reset or edit weak-topic history only after user approval."""

    WEAK_TOPICS_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not WEAK_TOPICS_FILE.exists():
        print("Weak-topic file does not exist. Creating it.")
        print(reset_weak_topics())
        return

    decision = request_file_approval(
        WEAK_TOPICS_FILE,
        "reset weak-topic history",
    )

    if decision == "approve":
        print(reset_weak_topics())

    elif decision == "edit":
        print("\nEnter the new weak-topic file content.")
        print("Press Enter on an empty line to finish.")

        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)

        new_content = "\n".join(lines) + "\n"

        confirm = input("Save this edited content? (yes/no): ").strip().lower()

        if confirm == "yes":
            WEAK_TOPICS_FILE.write_text(
                new_content,
                encoding="utf-8",
            )
            print("Edited weak-topic file saved.")
        else:
            print("Edit cancelled. Original file remains unchanged.")

    else:
        print("Weak-topic history was not changed.")


# --------------------------------------------------
# SESSION SELECTION AND DELETION
# --------------------------------------------------
def reset_weak_topics_with_approval():
    """Reset weak-topic history only after user approval."""

    file_path = Path("workspace/weak-topics.md")

    if not file_path.exists():
        print("Weak-topic file does not exist.")
        return

    decision = request_file_approval(
        file_path,
        "reset weak-topic history"
    )

    if decision == "approve" or decision == "1":
        print(reset_weak_topics())

    elif decision == "edit" or decision == "2":
        print("Edit selected. Original file has not been changed.")
        print("Please use a text editor to modify the file manually.")

    else:
        print("Operation rejected. Original file remains unchanged.")
def choose_session():
    """Resume an existing session, create a new one, or delete a session."""

    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    existing_sessions = sorted(SESSIONS_DIR.glob("*.json"))

    print("\n========== MOCKMATE ==========")
    print("1. Enter an existing session ID to resume")
    print("2. Press Enter to start a new interview")
    print("3. Type 'delete' to delete a session")
    print("4. Type 'reset' to manage weak-topic history")

    if existing_sessions:
        print("\nAvailable sessions:")
        for file in existing_sessions:
            print(f"- {file.stem}")

    choice = input("\nYour choice: ").strip()

    if choice.lower() == "reset":
        reset_weak_topics_with_approval()
        return None, None

    if choice.lower() == "delete":
        session_id = input("Enter the session ID to delete: ").strip()

        if not session_id:
            print("No session ID entered.")
            return None, None

        session_file = (
            SESSIONS_DIR / f"{session_id}.json"
        ).resolve()

        sessions_root = SESSIONS_DIR.resolve()

        if (
            not session_file.is_relative_to(sessions_root)
            or not session_file.is_file()
        ):
            print("Session not found or invalid session path.")
            return None, None

        decision = request_file_approval(
            session_file,
            "delete interview session",
        )

        if decision == "approve":
            session_file.unlink()
            print("Interview session deleted successfully.")
        elif decision == "edit":
            print("Editing is not available for session deletion.")
            print("The original session was not deleted.")
        else:
            print("Session deletion cancelled.")

        return None, None

    if choice:
        session_file = (SESSIONS_DIR / f"{choice}.json").resolve()

        if (
            not session_file.is_relative_to(SESSIONS_DIR.resolve())
            or not session_file.is_file()
        ):
            print("Session not found.")
            return None, None

        session = json.loads(session_file.read_text(encoding="utf-8"))

        print("\nPrevious interview session loaded.")
        print(f"Role: {session.get('role', 'Unknown')}")
        print(f"Round: {session.get('round', 'Unknown')}")
        print(f"Difficulty: {session.get('difficulty', 'Unknown')}")

        return session, session_file

    return create_session()


# --------------------------------------------------
# WEAK TOPIC ADAPTATION
# --------------------------------------------------

def build_weak_topic_context():
    """Read weak topics from previous interview sessions."""

    topics = read_weak_topics()

    if not topics:
        return "No previous weak topics were recorded."

    context = "Previously identified weak topics:\n"

    for topic in topics:
        context += f"- {topic}\n"

    return context


def build_next_question_prompt(session):
    """Build the prompt for the next interview question."""

    weak_topic_context = build_weak_topic_context()

    return f"""
Continue the mock technical interview.

Candidate role: {session['role']}
Interview round: {session['round']}
Difficulty: {session['difficulty']}

{weak_topic_context}

Instructions:
1. Ask exactly ONE interview question.
2. Do not answer the question yourself.
3. Do not provide the model answer.
4. Wait for the candidate's response.
5. Prefer testing previously identified weak topics when appropriate.
6. Keep the question relevant to the candidate's role and interview round.
"""


# --------------------------------------------------
# SCORECARD DISPLAY AND EVALUATION
# --------------------------------------------------

def print_scorecard(scorecard):
    """Display the validated interview scorecard."""

    print("\n========== ANSWER SCORECARD ==========")
    print(f"Score: {scorecard.score}/10")

    print("\nStrengths:")
    for item in scorecard.strengths:
        print(f"- {item}")

    print("\nAreas to improve:")
    for item in scorecard.gaps:
        print(f"- {item}")

    print(f"\nHint: {scorecard.hint}")
    print(f"Next topic: {scorecard.next_topic}")
    print("======================================\n")


def evaluate_and_record(session, question, answer):
    """Evaluate an answer and record its scorecard."""

    scorecard = evaluate_answer(question, answer)

    print_scorecard(scorecard)

    session["answers"].append({
        "question": question,
        "answer": answer,
        "score": scorecard.score,
    })

    session["scorecards"].append(scorecard.model_dump())

    result = record_weak_topics(scorecard)
    print(result)

    return scorecard


# --------------------------------------------------
# RESPONSE HANDLING
# --------------------------------------------------

def get_response_text(response):
    """Extract readable text from the interviewer response."""

    if isinstance(response, str):
        return response

    if isinstance(response, dict):
        if "messages" in response and response["messages"]:
            message = response["messages"][-1]
            return getattr(message, "content", str(message))

        if "output" in response:
            return str(response["output"])

    return str(response)


# --------------------------------------------------
# MAIN INTERVIEW LOOP
# --------------------------------------------------

def main():

    session, session_file = choose_session()

    # A reset or deletion operation returns no session.
    if session is None:
        return

    thread_id = session.get("thread_id", session["session_id"])

    print("\nMockMate interview started.")
    print("Type 'exit' at the answer prompt to stop the interview.")

    # Recover an answer if its evaluation was interrupted.
    if session.get("pending_answer") and session.get("current_question"):

        print("\nRecovering your previous unanswered evaluation...")

        try:
            evaluate_and_record(
                session,
                session["current_question"],
                session["pending_answer"],
            )

            session["pending_answer"] = None
            save_session(session, session_file)

        except Exception as error:
            save_session(session, session_file)
            print(f"Could not recover evaluation: {error}")
            print("Your answer remains saved for the next run.")
            return

    while True:

        # Generate a question if one is not already waiting.
        if not session.get("current_question"):

            prompt = build_next_question_prompt(session)

            try:
                response = ask_interviewer(prompt, thread_id)
                question = get_response_text(response)

            except Exception as error:
                print(f"Interviewer error: {error}")
                save_session(session, session_file)
                return

            session["current_question"] = question.strip()
            save_session(session, session_file)

            print("\nMockMate:")
            print(session["current_question"])

        # Wait for the candidate's answer.
        answer = input("\nYou: ").strip()

        if answer.lower() in ("exit", "quit"):
            save_session(session, session_file)
            print("\nInterview paused. Your session has been saved.")
            print(f"Session ID: {session['session_id']}")
            break

        if not answer:
            print("Please enter an answer before continuing.")
            continue

        # Save the answer before evaluation so it can be recovered.
        session["pending_answer"] = answer
        save_session(session, session_file)

        try:
            evaluate_and_record(
                session,
                session["current_question"],
                answer,
            )

            session["pending_answer"] = None
            session["current_question"] = None
            save_session(session, session_file)

        except Exception as error:
            save_session(session, session_file)
            print(f"Evaluation error: {error}")
            print("Your answer has been saved. You can resume this session later.")
            break


if __name__ == "__main__":
    main()
